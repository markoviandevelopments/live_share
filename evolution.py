import pygame
import math
import random
import copy
import time
import torch
import torch.nn as nn
import numpy as np
import requests


width, height = 1600, 1600

pygame.init()
window = pygame.display.set_mode((width, height))
font = pygame.font.SysFont('roboto', 24)

# World/Environment Info
grid_c = int(160 * width / 1600 * height / 1600) # number of food grids across
food_gen_c = int(200 * width / 1600 * height / 1600)
max_f = 10 # maximum number of food units
food_grid = []
can_pass = False
time_d = 0
env_grid = []   # 0: Water, 1: Grassland, 2: Desert
desert_centers = []
desert_centers_c = 30
desert_r = 10

zoom_f = 1
scroll_x = 0
scroll_y = 0

# Agent Info
num_agents = 1000
agent_size = 7
agents = []
next_agent_id = 0
itC = 0

current_mode = "off"
top_species_colors = []

def sigmoid(x_in):
    if x_in > 30:
        return 1
    elif x_in < -30:
        return 0
    else:
        return 1 / (1 + math.exp(x_in))

class NeuralNetwork(nn.Module):
    def __init__(self):
        super(NeuralNetwork, self).__init__()
        self.layer1 = nn.Linear(10, 5)
        self.layer2 = nn.Linear(5, 5)
        self.layer3 = nn.Linear(5, 5)
        self.relu = nn.ReLU()

    def forward(self, x):
        x = self.relu(self.layer1(x))
        x = self.relu(self.layer2(x))
        x = self.layer3(x)
        return x


class Agent:
    def __init__(self, x, y):
        global next_agent_id
        self.x = x
        self.y = y
        self.angle = random.uniform(0, 2 * math.pi)
        self.food = random.uniform(0,1)
        self.money = random.uniform(0,1)
        self.age = 0
        self.color = (int(self.food * 255), int(self.food * 255), int(self.food * 255))
        # 0: Red Intensity, 1: Green Intensity, 2: Blue Intensity, 3+: weights
        self.genes = [random.uniform(0, 1), random.uniform(0, 1), random.uniform(0, 1)]
        # Calculate number of weights: layer1 (9*5), layer2 (5*5), layer3 (5*5), plus biases
        num_weights = (10 * 5 + 5) + (5 * 5 + 5) + (5 * 5 + 5)
        for i in range(num_weights):
            self.genes.append(random.uniform(0, 1) / 1)
        self.nodes = []
        self.model = NeuralNetwork()
        self._initialize_weights()
        self.memory = [0, 0, 0, 0, 0]
        self.id = next_agent_id
        next_agent_id += 1
    
    def _initialize_weights(self):
        # Map genes to PyTorch model weights
        gene_idx = 3  # Start after color genes
        with torch.no_grad():
            # Layer 1: 10 inputs to 5 outputs
            weight = self.model.layer1.weight  # Shape: [5, 10]
            for i in range(5):
                for j in range(10):
                    weight[i, j] = (self.genes[gene_idx] - 0.5) * 2
                    gene_idx += 1
            bias = self.model.layer1.bias  # Shape: [5]
            for i in range(5):
                bias[i] = (self.genes[gene_idx] - 0.5) * 2
                gene_idx += 1
            # Layer 2: 5 inputs to 5 outputs
            weight = self.model.layer2.weight  # Shape: [5, 3]
            for i in range(5):
                for j in range(5):
                    weight[i, j] = (self.genes[gene_idx] - 0.5) * 2
                    gene_idx += 1
            bias = self.model.layer2.bias  # Shape: [5]
            for i in range(5):
                bias[i] = (self.genes[gene_idx] - 0.5) * 2
                gene_idx += 1
            # Layer 3: 5 inputs to 5 outputs
            weight = self.model.layer3.weight  # Shape: [5, 3]
            for i in range(5):
                for j in range(5):
                    weight[i, j] = (self.genes[gene_idx] - 0.5) * 2
                    gene_idx += 1
            bias = self.model.layer3.bias  # Shape: [5]
            for i in range(5):
                bias[i] = (self.genes[gene_idx] - 0.5) * 2
                gene_idx += 1
        
    
    def _update_genes_from_weights(self):
        # Update genes from model weights
        gene_idx = 3
        with torch.no_grad():
            # Layer 1
            weight = self.model.layer1.weight
            for i in range(5):
                for j in range(10):
                    self.genes[gene_idx] = (weight[i, j].item() / 2) + 0.5
                    gene_idx += 1
            bias = self.model.layer1.bias
            for i in range(5):
                self.genes[gene_idx] = (bias[i].item() / 2) + 0.5
                gene_idx += 1
            # Layer 2
            weight = self.model.layer2.weight
            for i in range(5):
                for j in range(5):
                    self.genes[gene_idx] = (weight[i, j].item() / 2) + 0.5
                    gene_idx += 1
            bias = self.model.layer2.bias
            for i in range(5):
                self.genes[gene_idx] = (bias[i].item() / 2) + 0.5
                gene_idx += 1
            # Layer 3
            weight = self.model.layer3.weight
            for i in range(5):
                for j in range(5):
                    self.genes[gene_idx] = (weight[i, j].item() / 2) + 0.5
                    gene_idx += 1
            bias = self.model.layer3.bias
            for i in range(5):
                self.genes[gene_idx] = (bias[i].item() / 2) + 0.5
                gene_idx += 1

    
    def think(self):
        self.angle = math.remainder(self.angle, 2 * math.pi)

        food_grid_x_i = max(min(math.floor(self.x / width * grid_c), grid_c - 1), 0)
        food_grid_y_i = max(min(math.floor(self.y / height * grid_c), grid_c - 1), 0)
        food_av = food_grid[food_grid_x_i][food_grid_y_i]
        
        inputs = torch.tensor([
            math.cos(self.angle),
            math.sin(self.angle),
            env_grid[food_grid_x_i][food_grid_y_i],
            food_av / max_f,
            sigmoid(self.food / 10),
            self.memory[0],
            self.memory[1],
            self.memory[2],
            random.uniform(0, 1),
            1
        ], dtype=torch.float32)
        with torch.no_grad():
            outputs = self.model(inputs)
        outputs = outputs.numpy()


        outputs = list(outputs)

        for i in range(len(outputs)):
            outputs[i] = max(min(outputs[i], 1), 0)
        
        self.memory[0] = max(min(outputs[0], 1), 0)
        self.memory[1] += max(min(outputs[1] / 10, 1), 0)
        self.memory[2] = max(min(outputs[2], 1), 0)
        self.memory[3] = max(min(outputs[3], 1), 0)
        self.memory[4] = max(min(outputs[4], 1), 0)

        return outputs

      
    def identify(self):
        if random.uniform(0, 1) < 0.000001:
            print(f'ID: {self.id} Genes: {self.genes} Age: {self.age}')

    def move(self):
        x = self.x
        y = self.y

        outputs = self.think()

        self.angle += min(max(outputs[0], 0), 1) * 2 * math.pi
        
        x_t = x + 5 * outputs[1] * math.cos(self.angle)
        y_t = y + 5 * outputs[1] * math.sin(self.angle)

        if x_t < 0:
            x_t = 0
        elif x_t > width:
            x_t = width

        if y_t < 0:
            y_t = 0
        elif y_t > width:
            y_t = width
        
        food_grid_x_i = max(min(math.floor(x_t / width * grid_c), grid_c - 1), 0)
        food_grid_y_i = max(min(math.floor(y_t / height * grid_c), grid_c - 1), 0)
        
        if food_grid_y_i != int(grid_c / 2) or can_pass:
            self.x = x_t
            self.y = y_t
        

    
    def eat(self):
        global food_grid
        # Essen
        food_grid_x_i = max(min(math.floor(self.x / width * grid_c), grid_c - 1), 0)
        food_grid_y_i = max(min(math.floor(self.y / height * grid_c), grid_c - 1), 0)
        if food_grid[food_grid_x_i][food_grid_y_i] > 2:
            food_grid[food_grid_x_i][food_grid_y_i] -= 1
            self.food += 1
        
        if self.age > 5000 and random.uniform(0, 1) < 0.001:
            self.food = 0
        
    def poop(self):
        if random.uniform(0,1) > 0.98:
            self.food -= random.uniform(0.0, 0.1)

    def reproduce(self):
        global next_agent_id
        # lil guy to reproduce if it has enough food
        if self.food > 10 and self.memory[3] > 0.5:
            new_self = copy.deepcopy(self)
            new_self.food = int(self.food * self.memory[4]) - 2
            new_self.mutate()
            new_self.id = next_agent_id
            next_agent_id += 1
            self.food -= int(self.memory[4]) + 2
            agents.append(new_self)
    
    def mutate(self):
        r = random.uniform(0, 1)
        if r < 0.05:
            random_mag = random.randint(-7, 0)
            for i in range(3, len(self.genes)):
                self.genes[i] += random.choice([-1, 1]) * random.uniform(0, 1) * 2 ** random_mag
                self.make_gene_valid(i)
        elif r < 0.1:
            i = random.randint(3, len(self.genes) - 1)
            self.genes[i] += random.choice([-1, 1]) * random.uniform(0, 1) * 2 ** (random.randint(-7, 0))
            self.make_gene_valid(i)
        elif r < 0.15:
            i = random.randint(3, len(self.genes) - 1)
            self.genes[i] = random.uniform(0, 1)

        if random.uniform(0, 1) < 0.15:
            i = random.randint(0, 2)
            self.genes[i] += random.choice([-1, 1]) * random.uniform(0, 1) * 2 ** (-4)
            self.make_gene_valid(i)
        
        self._initialize_weights()  # Update model weights after mutation

    def make_gene_valid(self, i):
        if self.genes[i] < 0:
            self.genes[i] = 0
        elif self.genes[i] > 1:
            self.genes[i] = 1



def add_agents(i):
    for _ in range(i):
        x = random.uniform(0, 1) * width
        y = random.uniform(0, 1) * height
        agents.append(Agent(x,y))

def generate_food():
    for i in range(int(food_gen_c)):
        x = random.randint(0, grid_c - 1)
        y = random.randint(0, grid_c - 1)

        is_desert = False
        for j in range(desert_centers_c):
            dist = ((x - desert_centers[j][0]) ** 2 + (y - desert_centers[j][1]) ** 2) ** 0.5

            if dist < desert_r:
                env_grid[x][y] = 1
                is_desert
        
        if is_desert:
            continue
  
        if food_grid[x][y] < max_f and random.uniform(0, 1) < 1:
            food_grid[x][y] += 1

def update_top_species():
    global top_species_colors, current_mode
    sorted_agents = sorted(agents, key=lambda a: a.food, reverse=True)[:300]
    top_species_colors = [
        {
            'r': int(agent.genes[0] * 255),
            'g': int(agent.genes[1] * 255),
            'b': int(agent.genes[2] * 255)
        } for agent in sorted_agents[:5]
    ]
    # Send data to Flask server
    try:
        response = requests.post('http://192.168.1.126:5000/update', json={
            'mode': 'top_species_glow',
            'top_species_colors': top_species_colors
        }, timeout=1)
        response.raise_for_status()
        print("Successfully sent top species colors to Flask server")
    except requests.RequestException as e:
        print(f"Error sending data to Flask server: {e}")



food_grid = [[random.randint(0, max_f) for _ in range(grid_c)] for _ in range(grid_c)]
env_grid = [[0 for _ in range(grid_c)] for _ in range(grid_c)]
desert_centers = [[random.randint(0, grid_c - 1), random.randint(0, grid_c - 1)] for _ in range(desert_centers_c)]
add_agents(num_agents)

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    
    keys = pygame.key.get_pressed()
    if keys[pygame.K_t]:
        can_pass = not can_pass
    if keys[pygame.K_m]:
        food_gen_c *= 1.1
    if keys[pygame.K_n]:
        food_gen_c *= 0.9

    if keys[pygame.K_w]:
        scroll_y -= 10 * zoom_f
    if keys[pygame.K_a]:
        scroll_x -= 10 * zoom_f
    if keys[pygame.K_s]:
        scroll_y += 10 * zoom_f
    if keys[pygame.K_d]:
        scroll_x += 10 * zoom_f
    
    if keys[pygame.K_e]:
        zoom_f *= 0.99
    if keys[pygame.K_r]:
        zoom_f *= 1.01
    if keys[pygame.K_q]:
        zoom_f = 1
        scroll_x = 0
        scroll_y = 0
    
    if keys[pygame.K_z]:
        time_d *= 0.9
    if keys[pygame.K_x]:
        time_d *= 1.1
        time_d += 0.001



    window.fill((0,0,0))
    for y in range(grid_c):
        for x in range(grid_c):
            color = (food_grid[x][y] * 255 / max_f, 0, 0)
            if not can_pass and y == int(grid_c / 2):
                color = (100, 100 , 100)
            elif env_grid[x][y] == 1:
                color = (220, 200, 190)
            pS = width / grid_c * zoom_f
            x_draw = int(x * pS - scroll_x)
            y_draw = int(y * pS - scroll_y)
            pygame.draw.rect(window, color, (x_draw, y_draw, math.ceil(pS), math.ceil(pS)))
    
    for agent in agents:
        agent.identify()
        agent.age += 1
        agent.color = (int(max(min(agent.food * 25.5, 255), 0)), int(max(min(agent.food * 25.5, 255), 0)), int(max(min(agent.food * 25.5, 255), 0)))
        farbe = (int(agent.genes[0] * 255), int(agent.genes[1] * 255), int(agent.genes[2] * 255))
        x = agent.x * zoom_f - scroll_x
        y = agent.y * zoom_f - scroll_y
        pygame.draw.rect(window, farbe, (int(x - 0.5 * agent_size), int(y - 0.5 * agent_size), agent_size, agent_size))
        start_pos = (int(x), int(y))
        end_pos = (int(x + 1.5 * agent_size * math.cos(agent.angle)), int(y + 1.5 * agent_size * math.sin(agent.angle)))
        pygame.draw.line(window, (255, 255, 255), start_pos, end_pos, width=2)

    text = font.render(f"Population: {len(agents)} ItC: {itC} Can Pass? {can_pass} Food Gen: {food_gen_c} Time Delay: {round(time_d, 4)}", True, (255, 255, 255))
    window.blit(text, (10, 10))

    pygame.display.flip()

    og_len = len(agents)
    for i, agent in enumerate(reversed(agents)):

        agent.food -= random.uniform(0, 0.15)
        og_index = og_len - 1 - i
        if agent.food <= 0:
            agents.pop(og_index)
            continue
        
        agent.eat()
        agent.move()
        agent.poop()
        agent.reproduce() 
    
    generate_food()
    if itC % 100 == 0:
        update_top_species()
    if len(agents) < 100:
        add_agents(100)
    
    if len(agents) < 100:
        add_agents(100)
    
    itC += 1
    time.sleep(time_d)

pygame.quit()
