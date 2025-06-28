import pygame
import math
import random
import copy
import time


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

zoom_f = 1
scroll_x = 0
scroll_y = 0

# Agent Info
num_agents = 100
agent_size = 7
agents = []
next_agent_id = 0
itC = 0

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
        for i in range(100):
            self.genes.append(random.uniform(0, 1))
        self.nodes = []
        for i in range(100):
            self.nodes.append(0)
        self.memory = [0, 0, 0]
        self.id = next_agent_id
        next_agent_id += 1
    
    def think(self):
        weight_i = 0
        self.angle = math.remainder(self.angle)
        self.nodes[0] = self.angle
        self.nodes[1] = self.food
        self.nodes[2] = self.memory[0]
        self.nodes[3] = self.memory[1]
        self.nodes[4] = self.memory[2]
        self.nodes[5] = random.uniform(0, 1)
        self.nodes[6] = 1

        for j in range(3):
            self.nodes[j+7] = 0
            for i in range(7):
                self.nodes[j+7] += self.nodes[i] * (self.genes[weight_i + 3] - 0.5) * 2 / 7
                weight_i += 1
            self.nodes[j+7] = max(self.nodes[j + 7], 0)
        
        for j in range(3):
            self.nodes[j+10] = 0
            for i in range(3):
                self.nodes[j+10] += self.nodes[i + 7] * (self.genes[weight_i + 3] - 0.5) * 2 / 3
                weight_i += 1
            self.nodes[j+10] = max(self.nodes[j+10], 0)
        
        self.memory[0] = max(min(self.nodes[11], 1), 0)
        self.memory[1] += max(min(self.nodes[12] / 10, 1), 0)
        self.memory[2] = max(min(self.nodes[13], 1), 0)

        return [self.nodes[j+10], self.memory[0]]

      
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
        if self.food > 10:
            new_self = copy.deepcopy(self)
            new_self.food = 3
            new_self.mutate()
            new_self.id = next_agent_id
            next_agent_id += 1
            self.food -= 5
            agents.append(new_self)
    
    def mutate(self):
        r = random.uniform(0, 1)
        # color_shift = 1
        # self.make_gene_valid(i)
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
        
        if random.uniform(0,1) < 0.15:
            i = random.randint(0, 2)
            self.genes[i] += random.choice([-1, 1]) * random.uniform(0, 1) * 2 ** (-5)
            self.make_gene_valid(i)

            # mutated_color = self.color[color_shift] + random.randint(-1,1)
            # mutated_color = max(0, min(255, mutated_color)) 
            # self.color = self.color[:color_shift] + (mutated_color,), self.color[color_shift + 1]

        
    def make_gene_valid(self, i):
        if self.genes[i] < 0:
            self.genes[i] = 0
        elif self.genes[i] > 1:
            self.genes[i] = 1
        
class World:
    def __init__(self):
        self.width = width
        self.height = height

    def initialize_food(self):
        for x in range(grid_c):
            temp = []
            for y in range(grid_c):
                temp.append(random.randint(0, max_f))
            food_grid.append(temp)

    def add_agents(self, i):
        for _ in range(i):
            x = random.uniform(0, 1) * width
            y = random.uniform(0, 1) * height
            agents.append(Agent(x,y))

    def generate_food(self):
        for i in range(int(food_gen_c)):
            x = random.randint(0, grid_c - 1)
            y = random.randint(0, grid_c - 1)
            if food_grid[x][y] < max_f and random.uniform(0, 1) < 1:
                food_grid[x][y] += 1

world = World()
world.initialize_food()
world.add_agents(num_agents)

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
    
    world.generate_food()
    
    if len(agents) < 100:
        world.add_agents(100)
    
    itC += 1
    time.sleep(time_d)

pygame.quit()