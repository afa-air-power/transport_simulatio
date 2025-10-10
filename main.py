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

class Camera:
    def __init__(self):
        self.zoom = 1.0
        self.min_zoom = 0.5
        self.max_zoom = 2.0
        self.zoom_step = 0.1

    def handle_event(self, event):
        if event.type == MOUSEWHEEL:
            self.zoom += event.y * self.zoom_step
            self.zoom = max(self.min_zoom, min(self.max_zoom, self.zoom))

def main():
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Advanced Traffic Intersection Simulation")
    clock = pygame.time.Clock()
    sim = Simulation()
    ui = UIManager(sim)
    camera = Camera()
    start_time = time.time()
    running = True

    while running:
        dt = clock.tick(60) / 1000.0
        current_time = time.time() - start_time

        for event in pygame.event.get():
            if event.type == QUIT:
                running = False
            ui.handle_event(event)
            camera.handle_event(event)

        sim.update(dt, current_time)
        sim.detect_collisions()

        screen.fill(BLACK)
        center_x, center_y = SIM_WIDTH // 2, SIM_HEIGHT // 2
        draw_roads(screen, center_x, center_y,4)
        draw_entities(screen, sim, center_x, center_y, camera.zoom)
        ui.draw(screen)

        pygame.display.flip()

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()