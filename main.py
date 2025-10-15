import pygame
import sys
from constants import *
from waypoint_simulation import WaypointSimulation

def main():
    pygame.init()
    screen = pygame.display.set_mode((DEFAULT_SCREEN_WIDTH, DEFAULT_SCREEN_HEIGHT))
    pygame.display.set_caption("Traffic Simulation - Waypoint Based")
    clock = pygame.time.Clock()

    center = (DEFAULT_SCREEN_WIDTH // 2, DEFAULT_SCREEN_HEIGHT // 2)
    simulation = WaypointSimulation(center)

    running = True
    time_acc = 0.0

    while running:
        dt = clock.tick(FPS) / 1000.0
        time_acc += dt

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # Обновление симуляции
        simulation.update(dt)

        # Отрисовка
        simulation.draw(screen)

        pygame.display.flip()

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()