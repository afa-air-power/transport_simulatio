import pygame
import sys
from simulation import TrafficSimulation
from ui import UIManager
from constants import *
from utils import draw_roads, draw_entities


def main():
    pygame.init()
    screen = pygame.display.set_mode((screen_config.width, screen_config.height))
    pygame.display.set_caption("Traffic Simulation")
    clock = pygame.time.Clock()

    sim = TrafficSimulation()
    ui = UIManager(sim)

    running = True
    while running:
        dt = clock.tick(FPS) / 1000.0  # Delta time в секундах

        # Обработка событий
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            else:
                ui.handle_events(event)

        # Обновление
        sim.update(dt)
        ui.update()

        # Отрисовка
        screen.fill(BLACK)
        center_x = screen_config.sim_width // 2
        center_y = screen_config.sim_height // 2
        draw_roads(screen, center_x, center_y, NUM_LANES)
        draw_entities(screen, sim, center_x, center_y)
        ui.draw(screen, ui.font)

        pygame.display.flip()

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()