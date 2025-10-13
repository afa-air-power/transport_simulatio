# entities.py
import random
import math
from constants import *

class Vehicle:
    def __init__(self, dir_in, num_lanes=NUM_LANES):
        self.dir_in = dir_in
        self.turn = random.choices([0, 1, 2], TURN_PROBS)[0]
        self.lane = random.randint(0, num_lanes - 1)
        self.target_lane = self.lane
        self.set_target_lane(num_lanes)

        self.target_speed = random.uniform(SPEED_MIN, SPEED_MAX)
        self.current_speed = 0
        self.pos = self.get_initial_pos(num_lanes)
        self.heading = self.get_initial_heading()
        if self.turn == 0:
            self.color = (random.randint(0, 100), random.randint(150, 255), random.randint(0, 100))
        elif self.turn == 1:
            self.color = (random.randint(150, 255), random.randint(0, 100), random.randint(0, 100))
        else:
            self.color = (random.randint(0, 100), random.randint(0, 100), random.randint(150, 255))
        self.dist_to_inter = ROAD_SIZE
        self.has_turned = False
        self.turning = False
        self.turn_center = (0, 0)
        self.turn_angle = 0
        self.turn_start_angle = 0
        self.turn_end_angle = 0
        self.stopped = False
        self.wait_time = 0
        self.mass = random.uniform(800, 1500)
        self.length = random.uniform(4, 6)
        self.width = random.uniform(2, 3.5)
        self.accel_rate = random.uniform(1.5, 3.0)
        self.brake_rate = random.uniform(4.0, 6.0)

    def set_target_lane(self, num_lanes):
        """Определяет целевую полосу в зависимости от направления поворота."""
        # turn: 0=прямо, 1=направо, 2=налево
        # lane: 0=крайняя левая, N-1=крайняя правая (относительно направления движения)
        if num_lanes < 2:
            self.target_lane = self.lane
            return

        # Простое правило: левая полоса для поворота налево, правая - направо.
        # Для движения прямо можно использовать любую полосу, кроме крайней для поворота.
        if self.turn == 2:  # Налево
            self.target_lane = 0
        elif self.turn == 1:  # Направо
            self.target_lane = num_lanes - 1
        else:  # Прямо
            # Если случайно оказались в полосе только для поворота, надо сместиться
            if self.lane == 0:
                self.target_lane = 1
            elif self.lane == num_lanes - 1:
                self.target_lane = num_lanes - 2
            else:
                self.target_lane = self.lane

    def get_initial_pos(self, num_lanes):
        offset = - (num_lanes * LANE_WIDTH) / 2 + self.lane * LANE_WIDTH + LANE_WIDTH / 2
        if self.dir_in == 'from_west':
            return (-ROAD_SIZE, offset)
        elif self.dir_in == 'from_east':
            return (ROAD_SIZE, -offset)
        elif self.dir_in == 'from_north':
            return (offset, -ROAD_SIZE)
        elif self.dir_in == 'from_south':
            return (-offset, ROAD_SIZE)

    def get_initial_heading(self):
        return {
            'from_west': (1, 0),
            'from_east': (-1, 0),
            'from_north': (0, 1),
            'from_south': (0, -1)
        }[self.dir_in]

    def update_lane_pos(self, num_lanes):
        offset = - (num_lanes * LANE_WIDTH) / 2 + self.lane * LANE_WIDTH + LANE_WIDTH / 2
        if self.heading[0] != 0:
            self.pos = (self.pos[0], offset if self.heading[0] > 0 else -offset)
        else:
            self.pos = (offset if self.heading[1] > 0 else -offset, self.pos[1])

    def accelerate(self, dt, target_speed):
        if target_speed > self.current_speed:
            self.current_speed = min(self.current_speed + self.accel_rate * dt, target_speed)
        else:
            self.current_speed = max(self.current_speed - self.brake_rate * dt, target_speed)

    def move(self, dt):
        if self.turning:
            angular_speed = self.current_speed / TURN_RADIUS
            self.turn_angle -= angular_speed * dt if (self.turn_end_angle - self.turn_start_angle) % (2 * math.pi) > math.pi else angular_speed * dt  # Direction based on turn
            self.pos = (self.turn_center[0] + TURN_RADIUS * math.cos(self.turn_angle),
                        self.turn_center[1] + TURN_RADIUS * math.sin(self.turn_angle))
            self.heading = (math.cos(self.turn_angle), math.sin(self.turn_angle))
            if abs(self.turn_angle - self.turn_end_angle) < 0.01:
                self.turning = False
                self.has_turned = True
                self.dist_to_inter = TURN_RADIUS * math.pi / 2  # Approximate distance traveled during turn
        else:
            self.pos = (self.pos[0] + self.heading[0] * self.current_speed * dt,
                        self.pos[1] + self.heading[1] * self.current_speed * dt)
            self.dist_to_inter -= self.current_speed * dt

    def start_turn(self):
        if self.turn == 0:
            return False
        self.turn_center = (self.pos[0] + TURN_CENTERS[self.dir_in][self.turn][0],
                            self.pos[1] + TURN_CENTERS[self.dir_in][self.turn][1])
        self.turn_start_angle, self.turn_end_angle = TURN_ANGLES[self.dir_in][self.turn]
        self.turn_angle = self.turn_start_angle
        self.turning = True
        return True

class Pedestrian:
    def __init__(self, cross, group_pos=None, num_lanes=NUM_LANES):
        self.cross = cross
        self.size = random.uniform(PED_SIZE_MIN, PED_SIZE_MAX)
        self.speed = random.uniform(PED_SPEED_MIN, PED_SPEED_MAX)
        self.color = (random.randint(100, 255), random.randint(100, 255), random.randint(100, 255))  # Random color
        self.pos = group_pos if group_pos else self.get_initial_pos(num_lanes)
        self.heading = self.get_initial_heading()
        self.current_speed = 0
        self.stopped = True
        self.wait_time = 0
        self.goal = self.get_goal(num_lanes)  # Goal position across the road

    def get_initial_pos(self, num_lanes):
        side = random.choice([-1, 1])
        offset = random.uniform(-10, 10)  # Slight random offset for realism
        sidewalk_offset = num_lanes * LANE_WIDTH / 2 + SIDEWALK_WIDTH / 2 + 10
        if self.cross == 'horizontal':
            return (offset, side * sidewalk_offset)
        else:
            return (side * sidewalk_offset, offset)

    def get_initial_heading(self):
        if self.cross == 'horizontal':
            return (0, -self.pos[1] / abs(self.pos[1]))
        else:
            return (-self.pos[0] / abs(self.pos[0]), 0)

    def get_goal(self, num_lanes):
        sidewalk_offset = num_lanes * LANE_WIDTH / 2 + SIDEWALK_WIDTH / 2 + 10
        if self.cross == 'horizontal':
            return (self.pos[0], -self.pos[1])
        else:
            return (-self.pos[0], self.pos[1])

    def calculate_forces(self, peds, cars, dt):
        # Attraction to goal
        dx, dy = self.goal[0] - self.pos[0], self.goal[1] - self.pos[1]
        dist_to_goal = math.hypot(dx, dy)
        if dist_to_goal > 0:
            attraction = (dx / dist_to_goal * PED_ATTRACTION, dy / dist_to_goal * PED_ATTRACTION)
        else:
            attraction = (0, 0)

        # Repulsion from other peds
        repulsion_peds = (0, 0)
        for other in peds:
            if other != self:
                dx_o, dy_o = other.pos[0] - self.pos[0], other.pos[1] - self.pos[1]
                dist = math.hypot(dx_o, dy_o)
                if dist < 5 and dist > 0:
                    rep_force = PED_REPULSION / dist ** 2
                    repulsion_peds = (repulsion_peds[0] - dx_o / dist * rep_force, repulsion_peds[1] - dy_o / dist * rep_force)

        # Repulsion from cars (stronger)
        repulsion_cars = (0, 0)
        for car in cars:
            dx_c, dy_c = car.pos[0] - self.pos[0], car.pos[1] - self.pos[1]
            dist = math.hypot(dx_c, dy_c)
            if dist < 10 and dist > 0:
                rep_force = PED_REPULSION * 2 / dist ** 2  # Stronger for cars
                repulsion_cars = (repulsion_cars[0] - dx_c / dist * rep_force, repulsion_cars[1] - dy_c / dist * rep_force)

        total_force = (attraction[0] + repulsion_peds[0] + repulsion_cars[0], attraction[1] + repulsion_peds[1] + repulsion_cars[1])
        norm = math.hypot(*total_force)
        if norm > 0:
            self.heading = (total_force[0] / norm, total_force[1] / norm)

    def move(self, dt, can_go, peds, cars):
        if can_go:
            self.calculate_forces(peds, cars, dt)
            self.current_speed = self.speed
        else:
            self.current_speed = 0
        self.pos = (self.pos[0] + self.heading[0] * self.current_speed * dt,
                    self.pos[1] + self.heading[1] * self.current_speed * dt)
        if self.current_speed == 0:
            self.wait_time += dt