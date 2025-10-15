import pygame
import sys
from constants import *
from waypoint_simulation import WaypointSimulation

def test_waypoints():
    pygame.init()
    screen = pygame.display.set_mode((DEFAULT_SCREEN_WIDTH, DEFAULT_SCREEN_HEIGHT))
    pygame.display.set_caption("Traffic Simulation - Waypoint Test")
    clock = pygame.time.Clock()

    center = (DEFAULT_SCREEN_WIDTH // 2, DEFAULT_SCREEN_HEIGHT // 2)
    simulation = WaypointSimulation(center)

    frame_count = 0
    max_frames = 300  # Run for 5 seconds at 60 FPS

    print("Starting waypoint simulation test...")
    print(f"Number of paths created: {len(simulation.paths)}")

    while frame_count < max_frames:
        dt = clock.tick(FPS) / 1000.0

        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                break

        # Update simulation
        simulation.update(dt)

        # Draw
        simulation.draw(screen)

        pygame.display.flip()
        frame_count += 1

        # Print some stats every second
        if frame_count % 60 == 0:
            print(f"Frame {frame_count}, Vehicles: {len(simulation.vehicles)}")

    print("Test completed successfully!")
    pygame.quit()

if __name__ == "__main__":
    test_waypoints()