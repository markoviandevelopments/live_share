import pygame
from config import Config
from world import World
from renderer import Renderer


def main():
    config = Config()
    world = World(config)
    renderer = Renderer(config)
    world.add_agents(config.INITIAL_AGENT_COUNT)

    can_pass = False
    iteration_count = 0
    running = True

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_t:
                    can_pass = not can_pass

        world.update(can_pass)
        renderer.render(world, can_pass, iteration_count)
        iteration_count += 1

    renderer.quit()

if __name__ == "__main__":
    main()
