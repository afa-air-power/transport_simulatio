import pygame
import sys
from simulation import TrafficSimulation
from ui import UIManager
from constants import *
from utils import draw_roads, draw_entities


def main():
    pygame.init()
    screen = pygame.display.set_mode((screen_config.width, screen_config.
        height), pygame.RESIZABLE)
    pygame.display.set_caption('Traffic Simulation')
    clock = pygame.time.Clock()
    sim = TrafficSimulation()
    ui = UIManager(sim)
    ui.import_config()
    running = True
    while running:
        dt = clock.tick(FPS) / 1000.0
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.VIDEORESIZE:
                screen_config.update(event.w, event.h)
                screen = pygame.display.set_mode((screen_config.width,
                    screen_config.height), pygame.RESIZABLE)
                sim.update_screen_size()
                ui.rebuild_ui_elements()
            else:
                ui.handle_events(event)
        sim.update(dt)
        ui.update(dt)
        screen.fill(BLACK)
        center_x = screen_config.sim_width // 2
        center_y = screen_config.sim_height // 2
        draw_roads(screen, center_x, center_y, NUM_LANES, ui.zoom_level)
        draw_entities(screen, sim, center_x, center_y, ui.zoom_level)
        ui.draw(screen, ui.font)
        pygame.display.flip()
    pygame.quit()
    sys.exit()


if __name__ == '__main__':
    main()
