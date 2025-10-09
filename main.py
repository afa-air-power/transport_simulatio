# main.py
import pygame
from pygame.locals import *
import time
import sys
from simulation import Simulation
from ui import UIManager
from utils import draw_roads, draw_entities
from constants import *

pygame.init()

def main():
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Advanced Traffic Intersection Simulation")
    clock = pygame.time.Clock()
    sim = Simulation()
    ui = UIManager(sim)
    start_time = time.time()
    running = True

    while running:
        dt = clock.tick(60) / 1000.0
        current_time = time.time() - start_time

        for event in pygame.event.get():
            if event.type == QUIT:
                running = False
            ui.handle_event(event)

        sim.update(dt, current_time)
        sim.detect_collisions()

        screen.fill(BLACK)
        center_x, center_y = SIM_WIDTH // 2, SIM_HEIGHT // 2
        draw_roads(screen, center_x, center_y)
        draw_entities(screen, sim, center_x, center_y)
        ui.draw(screen)

        pygame.display.flip()

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()