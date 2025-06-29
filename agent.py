import random
import math
import copy

class Agent:
    def __init__(self, x, y):
        global next_agent_id
    def __init__(self, x, y):
        global next_agent_id
        self.x = x
        self.y = y
        self.angle = random.uniform(0, 2 * math.pi)
        self.food = random.uniform(0,1)
        self.food = random.uniform(0,1)
        self.money = random.uniform(0,1)
        self.age = 0
        self.color = (int(self.food * 255), int(self.food * 255), int(self.food * 255))
        # 0: Red Intensity, 1: Green Intensity, 2: Blue Intensity, 3+: weights
        self.genes = [random.uniform(0, 1), random.uniform(0, 1), random.uniform(0, 1)]
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
    
        self.id = next_agent_id
        next_agent_id += 1
    
    def think(self):
        weight_i = 0
        self.angle = math.remainder(self.angle)
        self.angle = math.remainder(self.angle, 2 * math.pi)
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
    def move(self):
        x = self.x
        y = self.y

        outputs = self.think()

        self.angle += min(max(outputs[0], 0), 1) * 2 * math.pi
        
        x_t = x + 5 * outputs[1] * math.cos(self.angle)
        y_t = y + 5 * outputs[1] * math.sin(self.angle)

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
        # color_shift = 1
        # self.make_gene_valid(i)
        if r < 0.05:
            random_mag = random.randint(-7, 0)
            for i in range(3, len(self.genes)):
                self.genes[i] += random.choice([-1, 1]) * random.uniform(0, 1) * 2 ** random_mag
                self.make_gene_valid(i)
                self.make_gene_valid(i)
        elif r < 0.1:
            i = random.randint(3, len(self.genes) - 1)
            self.genes[i] += random.choice([-1, 1]) * random.uniform(0, 1) * 2 ** (random.randint(-7, 0))
            self.make_gene_valid(i)
            self.genes[i] += random.choice([-1, 1]) * random.uniform(0, 1) * 2 ** (random.randint(-7, 0))
            self.make_gene_valid(i)
        elif r < 0.15:
            i = random.randint(3, len(self.genes) - 1)
            self.genes[i] = random.uniform(0, 1)
        
        if random.uniform(0,1) < 0.15:
        
        if random.uniform(0,1) < 0.15:
            i = random.randint(0, 2)
            self.genes[i] += random.choice([-1, 1]) * random.uniform(0, 1) * 2 ** (-5)
            self.make_gene_valid(i)
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
         
            # mutated_color = self.color[color_shift] + random.randint(-1,1)
            # mutated_color = max(0, min(255, mutated_color)) 
            # self.color = self.color[:color_shift] + (mutated_color,), self.color[color_shift + 1]

        
    def make_gene_valid(self, i):
        if self.genes[i] < 0:
            self.genes[i] = 0
        elif self.genes[i] > 1:
            self.genes[i] = 1
         