import pygame
import math

class Renderer:
    def __init__(self, config):
        self.config = config
        pygame.init()
        self.window = pygame.display.set_mode((self.config.WIDTH, self.config.HEIGHT))
        self.font = pygame.font.SysFont(self.config.FONT_NAME, self.config.FONT_SIZE)

    def render(self, world, can_pass, iteration_count):
        self.window.fill((0, 0, 0))

        # Render food grid
        pixel_size = self.config.WIDTH // self.config.GRID_COUNT
        for y in range(self.config.GRID_COUNT):
            for x in range(self.config.GRID_COUNT):
                color = (world.food_grid[x][y] * 255 // self.config.MAX_FOOD, 0, 0)
                if not can_pass and y == self.config.GRID_COUNT // 2:
                    color = (100, 100, 100)
                pygame.draw.rect(self.window, color, (x * pixel_size, y * pixel_size, pixel_size, pixel_size))

        # Render agents
        for agent in world.agents:
            farbe = (int(agent.genes[0] * 255), int(agent.genes[1] * 255), int(agent.genes[2] * 255))
            pygame.draw.rect(self.window, farbe,
                             (int(agent.x - 0.5 * self.config.AGENT_SIZE),
                              int(agent.y - 0.5 * self.config.AGENT_SIZE),
                              self.config.AGENT_SIZE, self.config.AGENT_SIZE))
            start_pos = (int(agent.x), int(agent.y))
            end_pos = (int(agent.x + 1.5 * self.config.AGENT_SIZE * math.cos(agent.angle)),
                       int(agent.y + 1.5 * self.config.AGENT_SIZE * math.sin(agent.angle)))
            pygame.draw.line(self.window, (255, 255, 255), start_pos, end_pos, width=2)

        # Render UI
        text = self.font.render(f"Population: {len(world.agents)} ItC: {iteration_count} Can Pass? {can_pass}",
                                True, (255, 255, 255))
        self.window.blit(text, (10, 10))

        pygame.display.flip()

    def quit(self):
        pygame.quit()

