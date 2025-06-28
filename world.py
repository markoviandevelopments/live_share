import pygame
import math
import random
import copy

width, height = 800, 800

pygame.init()
window = pygame.display.set_mode((width, height))
font = pygame.font.SysFont('roboto', 24)

# World/Environment Info
grid_c = 40 # number of food grids across
max_f = 10 # maximum number of food units
food_grid = []
can_pass = False

# Agent Info
num_agents = 100
agent_size = 5
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
        # 0: Red Intensity, 1: Green Intensity, 2: Blue Intensity, 3: x-move intensity, 4: y-move intensity
        self.genes = [random.uniform(0, 1), random.uniform(0, 1), random.uniform(0, 1), random.uniform(0, 1), random.uniform(0, 1)]
        self.id = next_agent_id
        next_agent_id += 1
      
    def identify(self):
        if random.uniform(0, 1) < 0.000001:
            print(f'ID: {self.id} Genes: {self.genes} Age: {self.age}')

    def move(self):
        x = self.x
        y = self.y
        
        x_t = x + 0.4 * math.cos(self.angle)
        y_t = y + 0.4 * math.sin(self.angle)

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

        self.angle += self.genes[3] * math.pi
        self.angle += self.genes[4] * random.uniform(-2 * math.pi, 2 * math.pi)
        

    
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
        # lil guy to reproduce if it has enough food
        if self.food > 10:
            new_self = copy.deepcopy(self)
            new_self.food = 3
            new_self.mutate()
            self.food -= 5
            agents.append(new_self)
    
    def mutate(self):
        r = random.uniform(0, 1)
        color_shift = 1
        # self.make_gene_valid(i)
        if r < 0.1:
            for i in range(3, len(self.genes)):
                self.genes[i] += random.uniform(-1, 1) ** (-1 * random.randint(0, 5))
                self.make_gene_valid(i)
        elif r < 0.2:
            i = random.randint(3, len(self.genes) - 1)
            self.genes[i] += random.uniform(-1, 1) ** (-1 * random.randint(0, 5))
        if random.uniform(0,1) < 0.05:
            mutated_color = self.color[color_shift] + random.randint(-5,5)
            mutated_color = max(0, min(255, mutated_color)) 
            self.color = self.color[:color_shift] + (mutated_color,), self.color[color_shift + 1]

        
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
        for i in range(30):
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


    window.fill((0,0,0))
    for y in range(grid_c):
        for x in range(grid_c):
            color = (food_grid[x][y] * 255 / max_f, 0, 0)
            if not can_pass and y == int(grid_c / 2):
                color = (100, 100 , 100)
            pS = int(width / grid_c)
            pygame.draw.rect(window, color, (x * pS, y * pS, pS, pS))
    
    for agent in agents:
        agent.identify()
        agent.age += 1
        agent.color = (int(max(min(agent.food * 25.5, 255), 0)), int(max(min(agent.food * 25.5, 255), 0)), int(max(min(agent.food * 25.5, 255), 0)))
        farbe = (int(agent.genes[0] * 255), int(agent.genes[1] * 255), int(agent.genes[2] * 255))
        pygame.draw.rect(window, farbe, (int(agent.x), int(agent.y), agent_size, agent_size))

    text = font.render(f"Population: {len(agents)} ItC: {itC} Can Pass? {can_pass}", True, (255, 255, 255))
    window.blit(text, (10, 10))

    pygame.display.flip()

    world.generate_food()

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

    # Generate new food (schmeckt!)
    for i in range(90):
        x = int(random.randint(0, grid_c - 1))
        y = random.randint(0, grid_c - 1)
        if food_grid[x][y] < max_f and random.uniform(0, 1) < 1:
            food_grid[x][y] += 1
    
    if len(agents) < 100:
        world.add_agents(100)
    
    itC += 1

pygame.quit()

