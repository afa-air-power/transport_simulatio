# waypoint_system.py
import pygame
import random
import math
from constants import *

def vec_len(v):
    return math.hypot(v[0], v[1])

def normalize(v):
    l = vec_len(v)
    return (v[0]/l, v[1]/l) if l != 0 else (0, 0)

def dist(a, b):
    return math.hypot(a[0] - b[0], a[1] - b[1])

# helper чтобы получить позицию полосы по индексу
def lane_offset_vector(direction, lane_index):
    # lane_index: 0..LANES_PER_DIR-1 (0 — ближе к центру, 1 — дальше)
    offset = (lane_index - (LANES_PER_DIR - 1) / 2) * LANE_WIDTH
    if direction in ('N', 'S'):
        return (offset, 0)
    else:
        return (0, offset)

# базовые точки: начала полос (far out) и стоп-линии перед перекрестком
def build_waypoint_paths(center):
    """Строит пути (waypoints) для каждого направления, полосы и поворота"""
    far = 600
    stop_dist = ROAD_HALF - 40
    cx, cy = center

    paths = {}  # paths[(dir, lane_index, turn)] = list of (x,y) waypoints

    # exit directions mapping for turns
    # from N: left -> W, straight -> S, right -> E
    turn_map = {
        'N': {'L': 'W', 'S': 'S', 'R': 'E'},
        'S': {'L': 'E', 'S': 'N', 'R': 'W'},
        'W': {'L': 'S', 'S': 'E', 'R': 'N'},
        'E': {'L': 'N', 'S': 'W', 'R': 'S'}
    }

    def build_path(direction, lane, turn):
        wps = []
        # start far
        if direction == 'N':
            start = (cx + lane_offset_vector('N', lane)[0], cy - far)
            stop = (cx + lane_offset_vector('N', lane)[0], cy - stop_dist)
        elif direction == 'S':
            start = (cx + lane_offset_vector('S', lane)[0], cy + far)
            stop = (cx + lane_offset_vector('S', lane)[0], cy + stop_dist)
        elif direction == 'W':
            start = (cx - far, cy + lane_offset_vector('W', lane)[1])
            stop = (cx - stop_dist, cy + lane_offset_vector('W', lane)[1])
        else:  # E
            start = (cx + far, cy + lane_offset_vector('E', lane)[1])
            stop = (cx + stop_dist, cy + lane_offset_vector('E', lane)[1])

        # basic approach
        wps.append(start)
        # an entry point just before intersection
        wps.append(stop)

        # crossing maneuvers: create intermediate control points that route car to correct exit lane
        exit_dir = turn_map[direction][turn]
        # define exit lane offset: choose lane 0 (inner) for simplicity as target
        if exit_dir in ('N', 'S'):
            exit_lane_center = (cx + lane_offset_vector('N', 0)[0], cy + (-far if exit_dir == 'N' else far))
        else:
            exit_lane_center = (cx + (-far if exit_dir == 'W' else far), cy + lane_offset_vector('W', 0)[1])

        # mid control points — move through the center but offset towards exit lane
        # build a short curve: from stop -> mid -> exit_far
        if direction == 'N':
            mid = (cx - 80 if turn == 'L' else (cx + 80 if turn == 'R' else cx), cy - 20)
        elif direction == 'S':
            mid = (cx + 80 if turn == 'L' else (cx - 80 if turn == 'R' else cx), cy + 20)
        elif direction == 'W':
            mid = (cx - 20, cy + 80 if turn == 'L' else (cy - 80 if turn == 'R' else cy))
        else:  # E
            mid = (cx + 20, cy - 80 if turn == 'L' else (cy + 80 if turn == 'R' else cy))

        # push mid and an exit point
        wps.append(mid)
        wps.append(exit_lane_center)
        # finally an end point far away
        if exit_dir == 'N':
            wps.append((exit_lane_center[0], cy - far))
        elif exit_dir == 'S':
            wps.append((exit_lane_center[0], cy + far))
        elif exit_dir == 'W':
            wps.append((cx - far, exit_lane_center[1]))
        else:
            wps.append((cx + far, exit_lane_center[1]))

        return wps

    # fill paths
    for d in ('N', 'S', 'W', 'E'):
        for lane in range(LANES_PER_DIR):
            for turn in ('L', 'S', 'R'):
                paths[(d, lane, turn)] = build_path(d, lane, turn)

    return paths

class WaypointVehicle:
    """Машина, следующая по waypoints"""
    WIDTH = 20
    LENGTH = 36

    def __init__(self, path, speed_kmh, center):
        self.path = path[:]  # list of waypoints
        self.pos = list(self.path[0])
        self.idx = 1  # next waypoint index
        self.speed = speed_kmh * KMH_TO_PPS * SPEED_SCALE  # px/sec
        self.color = random.choice([(200, 70, 70), (70, 200, 80), (70, 140, 200), (220, 180, 60)])
        self.stopped = False
        self.id = random.randint(1000, 9999)
        self.center = center

    def get_incoming_direction(self):
        """Определяет направление въезда по начальной позиции пути"""
        start = self.path[0]
        cx, cy = self.center
        if start[1] < cy - 200:
            return 'N'
        elif start[1] > cy + 200:
            return 'S'
        elif start[0] < cx - 200:
            return 'W'
        else:
            return 'E'

    def update(self, dt, others, traffic_light):
        """Обновляет позицию машины"""
        # compute target point
        if self.idx >= len(self.path):
            return False  # finished

        target = self.path[self.idx]
        to_target = (target[0] - self.pos[0], target[1] - self.pos[1])
        d = vec_len(to_target)
        direction = normalize(to_target) if d != 0 else (0, 0)

        # determine if we must stop for red light
        stop_for_light = False
        incoming_dir = self.get_incoming_direction()

        # if approaching stop (distance to stop waypoint small) and light is red -> stop
        # identify stop index as 1 in our path building
        dist_to_stop = dist(self.pos, self.path[1]) if len(self.path) > 1 else 9999
        if dist_to_stop < 60:
            # if light is red for our incoming group and not yellow (allow passing on yellow)
            if not traffic_light.is_green(incoming_dir) and not traffic_light.is_yellow(incoming_dir):
                stop_for_light = True

        # braking for vehicle ahead: find nearest vehicle ahead on roughly same path (simple)
        slow_for_vehicle = False
        for other in others:
            if other is self:
                continue
            # if other is ahead along path: check distance
            if dist(self.pos, other.pos) < SAFE_DISTANCE:
                slow_for_vehicle = True
                break

        desired_speed = 0.0 if stop_for_light or slow_for_vehicle else self.speed
        # simple acceleration/deceleration
        accel = 120.0  # px/s^2
        if desired_speed > self.speed:
            self.speed = min(desired_speed, self.speed + accel * dt)
        else:
            self.speed = max(desired_speed, self.speed - accel * dt)

        # move toward target by self.speed * dt but not overshoot
        move = self.speed * dt
        if move >= d:
            # snap to waypoint
            self.pos[0], self.pos[1] = target
            self.idx += 1
        else:
            self.pos[0] += direction[0] * move
            self.pos[1] += direction[1] * move

        return True

    def draw(self, surf, center_x, center_y):
        """Рисует машину как поворачивающийся прямоугольник"""
        if self.idx >= len(self.path):
            return

        # Позиция на экране (paths уже содержат абсолютные координаты относительно center)
        x = int(self.pos[0])
        y = int(self.pos[1])

        # Направление к следующей точке для поворота
        target = self.path[self.idx] if self.idx < len(self.path) else self.path[-1]
        angle = math.degrees(math.atan2(target[1] - self.pos[1], target[0] - self.pos[0]))

        # Создаем поверхность для машины
        rect_surf = pygame.Surface((self.LENGTH, self.WIDTH))
        rect_surf.fill(self.color)

        # Поворачиваем поверхность
        rotated = pygame.transform.rotate(rect_surf, -angle)
        rotated_rect = rotated.get_rect(center=(x, y))
        surf.blit(rotated, rotated_rect.topleft)