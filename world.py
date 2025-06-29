import random
from agent import Agent
from terrain import TerrainType


class World:
    def __init__(self, config):
        self.config = config
        self.food_grid = []
        self.terrain_grid = []
        self.agents = []
        self.next_agent_id = 0
        self.initialize_grids()

    def initialize_grids(self):
        self.food_grid = [[random.randint(0, self.config.MAX_FOOD) for _ in range(self.config.GRID_COUNT)]
                          for _ in range(self.config.GRID_COUNT)]
        
        self.terrain_grid = [[self.generate_terrain() for _ in range(self.config.GRID_COUNT)]
                    for _ in range(self.config.GRID_COUNT)]

    def add_agents(self, num_agents):
        for _ in range(num_agents):
            x = random.uniform(0, 1) * self.config.WIDTH
            y = random.uniform(0, 1) * self.config.HEIGHT
            agent = Agent(x, y, self.config, self.next_agent_id)
            self.next_agent_id += 1
            self.agents.append(agent)

    def generate_food(self):
        for _ in range(self.config.FOOD_GEN_COUNT):
            x = random.randint(0, self.config.GRID_COUNT - 1)
            y = random.randint(0, self.config.GRID_COUNT - 1)
            terrain = self.terrain_grid[x][y]
            if terrain == TerrainType.FOREST:
                spawn_chance = 1.0
            elif terrain == TerrainType.WATER:
                spawn_chance = 0.5
            else:
                spawn_chance = 0.1

            if self.food_grid[x][y] < self.config.MAX_FOOD and random.uniform(0, 1) < spawn_chance:
                self.food_grid[x][y] += 1 

    def generate_terrain(self):
        roll = random.uniform(0, 1)
        if roll < 0.6:
            return TerrainType.DESSERT
        elif roll < 0.85:
            return TerrainType.FOREST
        else:
            return TerrainType.WATER

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
            agent.move(self.food_grid, self.terrain_grid, can_pass)
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
