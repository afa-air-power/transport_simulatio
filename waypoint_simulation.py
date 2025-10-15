# waypoint_simulation.py
import pygame
import random
import math
from collections import deque

from constants import *
from waypoint_system import build_waypoint_paths, WaypointVehicle
from simple_traffic_light import SimpleTrafficLight

class WaypointSimulation:
    """Симуляция с четким представлением полос через waypoints"""

    def __init__(self, center):
        self.center = center
        self.vehicles = []
        self.traffic_light = SimpleTrafficLight()

        # Строим все пути для waypoints
        self.paths = build_waypoint_paths(center)

        # spawn timers per direction-lane
        self.spawn_timers = []
        for d in ('N', 'S', 'W', 'E'):
            for lane in range(LANES_PER_DIR):
                self.spawn_timers.append({
                    'dir': d,
                    'lane': lane,
                    't': random.random() * SPAWN_INTERVAL_MEAN
                })

    def spawn_vehicle(self, entry):
        """Создает новое транспортное средство"""
        d = entry['dir']
        lane = entry['lane']
        turn = random.choices(['L', 'S', 'R'], weights=[0.15, 0.7, 0.15])[0]
        path = self.paths[(d, lane, turn)]
        speed_kmh = random.uniform(MIN_KMH, MAX_KMH)
        v = WaypointVehicle(path, speed_kmh, self.center)
        self.vehicles.append(v)

    def update(self, dt):
        """Обновляет симуляцию"""
        # update traffic light
        self.traffic_light.update(dt)

        # spawn logic - limit to 20 vehicles for debugging
        if len(self.vehicles) < 20:
            for entry in self.spawn_timers:
                entry['t'] -= dt
                if entry['t'] <= 0:
                    self.spawn_vehicle(entry)
                    entry['t'] = max(0.3, random.gauss(SPAWN_INTERVAL_MEAN, SPAWN_JITTER))

        # update vehicles
        alive = []
        for v in self.vehicles:
            ok = v.update(dt, self.vehicles, self.traffic_light)
            if ok:
                alive.append(v)
        self.vehicles = alive

    def draw_roads(self, screen):
        """Рисует дороги"""
        cx, cy = self.center

        # draw horizontal road
        pygame.draw.rect(screen, (50, 50, 50), (0, cy - ROAD_HALF, DEFAULT_SCREEN_WIDTH, ROAD_HALF * 2))
        # draw vertical
        pygame.draw.rect(screen, (50, 50, 50), (cx - ROAD_HALF, 0, ROAD_HALF * 2, DEFAULT_SCREEN_HEIGHT))

        # lane markings (simple dashed)
        for i in range(-LANES_PER_DIR, LANES_PER_DIR + 1):
            # horizontal centerlines
            y = cy + i * LANE_WIDTH
            pygame.draw.line(screen, (200, 200, 200), (0, y), (DEFAULT_SCREEN_WIDTH, y), 1)
            # vertical
            x = cx + i * LANE_WIDTH
            pygame.draw.line(screen, (200, 200, 200), (x, 0), (x, DEFAULT_SCREEN_HEIGHT), 1)

    def draw_paths_debug(self, screen):
        """Рисует waypoint пути для отладки"""
        for key, p in self.paths.items():
            for i in range(len(p) - 1):
                pygame.draw.line(screen, (120, 120, 120),
                                (int(p[i][0]), int(p[i][1])),
                                (int(p[i+1][0]), int(p[i+1][1])), 2)
            for pt in p:
                pygame.draw.circle(screen, (180, 180, 180),
                                  (int(pt[0]), int(pt[1])), 3)

    def draw(self, screen):
        """Рисует все элементы симуляции"""
        cx, cy = self.center

        # Background
        screen.fill((40, 40, 40))

        # Roads
        self.draw_roads(screen)

        # Debug paths - let's see the waypoints
        self.draw_paths_debug(screen)

        # Vehicles
        for v in self.vehicles:
            v.draw(screen, 0, 0)  # paths already contain absolute coordinates

        # Traffic light
        self.traffic_light.draw(screen, cx, cy)

        # HUD
        font = pygame.font.SysFont(None, 18)
        txt = font.render(f"Vehicles: {len(self.vehicles)}", True, (240, 240, 240))
        screen.blit(txt, (10, 10))