import random
import math
import copy

class Agent:
    def __init__(self, x, y, config, agent_id):
        self.x = x
        self.y = y
        self.angle = random.uniform(0, 2 * math.pi)
        self.food = random.uniform(0, 1)
        self.money = random.uniform(0,1)
        self.age = 0
        self.id = agent_id
        self.config = config
        # Genes: [0: Red, 1: Green, 2: Blue, 3: x-move intensity, 4: y-move intensity]
        self.genes = [random.uniform(0, 1) for _ in range(5)]
        for i in range(100):
            self.genes.append(random.uniform(0, 1))
        self.nodes = []
        for i in range(100):
            self.nodes.append(0)
        self.memory = [0, 0, 0]

    def think(self):
        weight_i = 0
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

    def move(self, food_grid, can_pass):

        x = self.x
        y = self.y

        outputs = self.think()
        self.angle = min(max(outputs[0], 0), 1) * 2 * math.pi

        x_t = self.x + 2 * outputs[1] * math.cos(self.angle)
        y_t = self.y + 2 * outputs[1] * math.sin(self.angle)

        x_t = max(0, min(x_t, self.config.WIDTH))
        y_t = max(0, min(y_t, self.config.HEIGHT))

        grid_c = self.config.GRID_COUNT
        food_grid_x_i = max(min(math.floor(x_t / self.config.WIDTH * grid_c), grid_c - 1), 0)
        food_grid_y_i = max(min(math.floor(y_t / self.config.HEIGHT * grid_c), grid_c - 1), 0)

        if food_grid_y_i != int(grid_c / 2) or can_pass:
            self.x = x_t
            self.y = y_t


        self.angle += self.genes[3] * math.pi
        self.angle += self.genes[4] * random.uniform(-2 * math.pi, 2 * math.pi)

    def eat(self, food_grid):
        grid_c = self.config.GRID_COUNT
        food_grid_x_i = max(min(math.floor(self.x / self.config.WIDTH * grid_c), grid_c - 1), 0)
        food_grid_y_i = max(min(math.floor(self.y / self.config.HEIGHT * grid_c), grid_c - 1), 0)
        if food_grid[food_grid_x_i][food_grid_y_i] > self.config.AGENT_EAT_THRESHOLD:
            food_grid[food_grid_x_i][food_grid_y_i] -= self.config.AGENT_EAT_AMOUNT
            self.food += self.config.AGENT_EAT_AMOUNT

        if self.age > self.config.AGENT_DEATH_AGE and random.uniform(0, 1) < self.config.AGENT_DEATH_PROB:
            self.food = 0

    def poop(self):
        if random.uniform(0, 1) > self.config.AGENT_POOP_PROB:
            self.food -= random.uniform(self.config.AGENT_POOP_AMOUNT_MIN, self.config.AGENT_POOP_AMOUNT_MAX)

    def reproduce(self):
        if self.food > self.config.AGENT_REPRODUCE_FOOD_THRESHOLD:
            new_agent = copy.deepcopy(self)
            new_agent.food = self.config.AGENT_REPRODUCE_NEW_FOOD
            new_agent.mutate()
            self.food -= self.config.AGENT_REPRODUCE_FOOD_COST
            return new_agent
        return None

    def mutate(self):
        r = random.uniform(0, 1)
        if r < 0.05:
            random_mag = random.randint(-7, 0)
            for i in range(3, len(self.genes)):
                self.genes[i] += random.choice([-1, 1]) * random.uniform(0, 1) * 2 ** random_mag
                self._make_gene_valid(i)
        elif r < 0.1:
            i = random.randint(3, len(self.genes) - 1)
            self.genes[i] += random.choice([-1, 1]) * random.uniform(0, 1) * 2 ** random.randint(-7, 0)
            self._make_gene_valid(i)
        elif r < 0.15:
            i = random.randint(3, len(self.genes) - 1)
            self.genes[i] = random.uniform(0, 1)

        if random.uniform(0, 1) < 0.15:
            i = random.randint(0, 2)
            self.genes[i] += random.choice([-1, 1]) * random.uniform(0, 1) * 2 ** -5
            self._make_gene_valid(i)

    def _make_gene_valid(self, i):
        self.genes[i] = max(0, min(1, self.genes[i]))

    