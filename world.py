import random
from agent import Agent

class World:
    def __init__(self):
        self.width = 600
        self.height = 600

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

    def update(self, can_pass):
        # Update agents
        agents_to_remove = []
        new_agents = []
        for agent in self.agents:
            agent.food -= random.uniform(self.config.AGENT_FOOD_DECAY_MIN, self.config.AGENT_FOOD_DECAY_MAX)
            if agent.food <= 0:
                agents_to_remove.append(agent)
                continue
            agent.eat(self.food_grid)
            agent.move(self.food_grid, can_pass)
            agent.poop()
            new_agent = agent.reproduce()
            if new_agent:
                new_agent.id = self.next_agent_id
                self.next_agent_id += 1
                new_agents.append(new_agent)
            agent.age += 1
            agent.identify()

        # Remove dead agents and add new ones
        self.agents = [agent for agent in self.agents if agent not in agents_to_remove]
        self.agents.extend(new_agents)

        # Maintain minimum population
        if len(self.agents) < self.config.INITIAL_AGENT_COUNT:
            self.add_agents(self.config.INITIAL_AGENT_COUNT - len(self.agents))

        # Generate new food
        self.generate_food()

