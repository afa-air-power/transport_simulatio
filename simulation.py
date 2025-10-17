import pygame
import random
import math
import basic
import constants
from constants import *
from traffic_controller import TrafficController


class PathGenerator:

    @staticmethod
    def generate_waypoints(from_direction, lane, turn_direction):
        road_half = NUM_LANES * LANE_WIDTH / 2
        from constants import screen_config
        entry_dist_x = screen_config.sim_width / 2 + 50
        entry_dist_y = screen_config.sim_height / 2 + 50
        waypoints = []
        if from_direction == 'from_west':
            entry_y = -road_half + (lane + 0.5) * LANE_WIDTH
            waypoints.append((-entry_dist_x, entry_y))
            waypoints.append((-road_half - 20, entry_y))
            if turn_direction == 'straight':
                waypoints.append((road_half + 20, entry_y))
                waypoints.append((entry_dist_x, entry_y))
            elif turn_direction == 'left':
                exit_x = -road_half + (lane + 0.5) * LANE_WIDTH
                waypoints.append((-15, entry_y))
                waypoints.append((-5, -5))
                waypoints.append((exit_x, -15))
                waypoints.append((exit_x, -road_half - 20))
                waypoints.append((exit_x, -entry_dist_y))
            elif turn_direction == 'right':
                exit_x = road_half - (lane + 0.5) * LANE_WIDTH
                waypoints.append((-15, entry_y))
                waypoints.append((-5, 5))
                waypoints.append((exit_x, 15))
                waypoints.append((exit_x, road_half + 20))
                waypoints.append((exit_x, entry_dist_y))
        elif from_direction == 'from_east':
            entry_y = road_half - (lane + 0.5) * LANE_WIDTH
            waypoints.append((entry_dist_x, entry_y))
            waypoints.append((road_half + 20, entry_y))
            if turn_direction == 'straight':
                waypoints.append((-road_half - 20, entry_y))
                waypoints.append((-entry_dist_x, entry_y))
            elif turn_direction == 'left':
                exit_x = road_half - (lane + 0.5) * LANE_WIDTH
                waypoints.append((15, entry_y))
                waypoints.append((5, 5))
                waypoints.append((exit_x, 15))
                waypoints.append((exit_x, road_half + 20))
                waypoints.append((exit_x, entry_dist_y))
            elif turn_direction == 'right':
                exit_x = -road_half + (lane + 0.5) * LANE_WIDTH
                waypoints.append((15, entry_y))
                waypoints.append((5, -5))
                waypoints.append((exit_x, -15))
                waypoints.append((exit_x, -road_half - 20))
                waypoints.append((exit_x, -entry_dist_y))
        elif from_direction == 'from_north':
            entry_x = road_half - (lane + 0.5) * LANE_WIDTH
            waypoints.append((entry_x, -entry_dist_y))
            waypoints.append((entry_x, -road_half - 20))
            if turn_direction == 'straight':
                waypoints.append((entry_x, road_half + 20))
                waypoints.append((entry_x, entry_dist_y))
            elif turn_direction == 'left':
                exit_y = -road_half + (lane + 0.5) * LANE_WIDTH
                waypoints.append((entry_x, -15))
                waypoints.append((5, -5))
                waypoints.append((15, exit_y))
                waypoints.append((road_half + 20, exit_y))
                waypoints.append((entry_dist_x, exit_y))
            elif turn_direction == 'right':
                exit_y = road_half - (lane + 0.5) * LANE_WIDTH
                waypoints.append((entry_x, -15))
                waypoints.append((-5, -5))
                waypoints.append((-15, exit_y))
                waypoints.append((-road_half - 20, exit_y))
                waypoints.append((-entry_dist_x, exit_y))
        elif from_direction == 'from_south':
            entry_x = -road_half + (lane + 0.5) * LANE_WIDTH
            waypoints.append((entry_x, entry_dist_y))
            waypoints.append((entry_x, road_half + 20))
            if turn_direction == 'straight':
                waypoints.append((entry_x, -road_half - 20))
                waypoints.append((entry_x, -entry_dist_y))
            elif turn_direction == 'left':
                exit_y = road_half - (lane + 0.5) * LANE_WIDTH
                waypoints.append((entry_x, 15))
                waypoints.append((-5, 5))
                waypoints.append((-15, exit_y))
                waypoints.append((-road_half - 20, exit_y))
                waypoints.append((-entry_dist_x, exit_y))
            elif turn_direction == 'right':
                exit_y = -road_half + (lane + 0.5) * LANE_WIDTH
                waypoints.append((entry_x, 15))
                waypoints.append((5, 5))
                waypoints.append((15, exit_y))
                waypoints.append((road_half + 20, exit_y))
                waypoints.append((entry_dist_x, exit_y))
        return waypoints


class Car(basic.basic_similation_element,TrafficController):
    SAFE_DISTANCE = constants.SAFE_DISTANCE
    COMFORTABLE_DISTANCE = constants.COMFORTABLE_DISTANCE
    WAYPOINT_REACH_DISTANCE = constants.WAYPOINT_REACH_DISTANCE
    LANE_CHANGE_DISTANCE = constants.LANE_CHANGE_DISTANCE

    def __init__(self, waypoints, speed, color, from_direction, turn_direction):

        self.waypoints = waypoints
        self.current_waypoint_index = 0
        self.pos = list(waypoints[0])
        self.max_speed = 200
        self.speed = speed * 0.5
        self.current_speed = self.speed
        self.color = color
        self.neon_color = self.generate_neon_color(color)
        self.from_direction = from_direction
        self.turn_direction = turn_direction
        car_type = random.choice(['small', 'medium', 'large'])
        if car_type == 'small':
            self.length = 8
            self.width = 4
        elif car_type == 'medium':
            self.length = 12
            self.width = 6
        else:
            self.length = 16
            self.width = 7
        self.waiting_time = 0.0
        self.is_waiting = False
        self.glow_pulse = random.uniform(0, math.pi * 2)
        self.heading = self._calculate_heading()
        super().__init__()

    def _calculate_heading(self):
        if self.current_waypoint_index >= len(self.waypoints) - 1:
            return [1, 0]
        current = self.waypoints[self.current_waypoint_index]
        next_wp = self.waypoints[self.current_waypoint_index + 1]
        dx = next_wp[0] - current[0]
        dy = next_wp[1] - current[1]
        dist = math.hypot(dx, dy)
        if dist > 0:
            return [dx / dist, dy / dist]
        return [1, 0]

    def _get_current_lane_position(self):
        if abs(self.heading[0]) > abs(self.heading[1]):
            return self.pos[1]
        else:
            return self.pos[0]

    def _is_on_same_lane(self, other_car, tolerance=LANE_WIDTH * 0.6):
        self_is_horizontal = abs(self.heading[0]) > abs(self.heading[1])
        other_is_horizontal = abs(other_car.heading[0]) > abs(other_car.
                                                              heading[1])
        if self_is_horizontal != other_is_horizontal:
            return False
        my_lane_pos = self._get_current_lane_position()
        other_lane_pos = other_car._get_current_lane_position()
        lane_diff = abs(my_lane_pos - other_lane_pos)
        return lane_diff < tolerance

    def _move_towards_waypoint(self, dt, speed):
        if self.current_waypoint_index >= len(self.waypoints):
            return False
        target = self.waypoints[self.current_waypoint_index]
        dx = target[0] - self.pos[0]
        dy = target[1] - self.pos[1]
        dist = math.hypot(dx, dy)
        if dist < self.WAYPOINT_REACH_DISTANCE:
            self.current_waypoint_index += 1
            if self.current_waypoint_index < len(self.waypoints):
                self.heading = self._calculate_heading()
            return True
        if dist > 0:
            self.heading = [dx / dist, dy / dist]
            move_dist = min(speed * dt, dist)
            new_x = self.pos[0] + self.heading[0] * move_dist
            new_y = self.pos[1] + self.heading[1] * move_dist
            road_half = NUM_LANES * LANE_WIDTH / 2
            stop_line_margin = 2.0
            if abs(self.heading[0]) > abs(self.heading[1]):
                if self.heading[0] > 0:
                    stop_line = -road_half - stop_line_margin
                    if self.pos[0] >= stop_line:
                        if self.is_waiting:
                            self.speed = 0
                            return True
                    elif new_x > stop_line:
                        if self.is_waiting:
                            self.pos[0] = stop_line
                            self.speed = 0
                            return True
                        else:
                            self.pos[0] = new_x
                            self.pos[1] = new_y
                            return True
                else:
                    stop_line = road_half + stop_line_margin
                    if self.pos[0] <= stop_line:
                        if self.is_waiting:
                            self.speed = 0
                            return True
                    elif new_x < stop_line:
                        if self.is_waiting:
                            self.pos[0] = stop_line
                            self.speed = 0
                            return True
                        else:
                            self.pos[0] = new_x
                            self.pos[1] = new_y
                            return True
            elif self.heading[1] > 0:
                stop_line = -road_half - stop_line_margin
                if self.pos[1] >= stop_line:
                    if self.is_waiting:
                        self.speed = 0
                        return True
                elif new_y > stop_line:
                    if self.is_waiting:
                        self.pos[1] = stop_line
                        self.speed = 0
                        return True
                    else:
                        self.pos[0] = new_x
                        self.pos[1] = new_y
                        return True
            else:
                stop_line = road_half + stop_line_margin
                if self.pos[1] <= stop_line:
                    if self.is_waiting:
                        self.speed = 0
                        return True
                elif new_y < stop_line:
                    if self.is_waiting:
                        self.pos[1] = stop_line
                        self.speed = 0
                        return True
                    else:
                        self.pos[0] = new_x
                        self.pos[1] = new_y
                        return True
            self.pos[0] = new_x
            self.pos[1] = new_y
        return True

    def _check_traffic_light(self, controller):
        road_half = NUM_LANES * LANE_WIDTH / 2
        stop_distance = 200
        if abs(self.heading[0]) > abs(self.heading[1]):
            if self.heading[0] > 0:
                light_color = controller.get_color('west')
                in_stop_zone = self.pos[0] < -road_half and self.pos[0
                ] > -road_half - stop_distance
            else:
                light_color = controller.get_color('east')
                in_stop_zone = self.pos[0] > road_half and self.pos[0
                ] < road_half + stop_distance
        elif self.heading[1] > 0:
            light_color = controller.get_color('north')
            in_stop_zone = self.pos[1] < -road_half and self.pos[1
            ] > -road_half - stop_distance
        else:
            light_color = controller.get_color('south')
            in_stop_zone = self.pos[1] > road_half and self.pos[1
            ] < road_half + stop_distance
        return in_stop_zone and light_color in ['red', 'yellow']

    def _get_distance_to_stopline(self):
        road_half = NUM_LANES * LANE_WIDTH / 2
        if abs(self.heading[0]) > abs(self.heading[1]):
            if self.heading[0] > 0:
                return -road_half - self.pos[0]
            else:
                return self.pos[0] - road_half
        elif self.heading[1] > 0:
            return -road_half - self.pos[1]
        else:
            return self.pos[1] - road_half

    def _find_car_ahead(self, all_cars):
        min_dist = float('inf')
        car_ahead = None
        for other in all_cars:
            if other is self:
                continue
            if not self._is_on_same_lane(other):
                continue
            dot_product = self.heading[0] * other.heading[0] + self.heading[1
            ] * other.heading[1]
            if dot_product < 0.5:
                continue
            dx = other.pos[0] - self.pos[0]
            dy = other.pos[1] - self.pos[1]
            dist_center_to_center = math.hypot(dx, dy)
            forward_dot = dx * self.heading[0] + dy * self.heading[1]
            if forward_dot > 0:
                our_half_length = self.length * 2.5 / 2
                other_half_length = other.length * 2.5 / 2
                real_distance = (dist_center_to_center - our_half_length -
                                 other_half_length)
                if real_distance > 2 and real_distance < min_dist:
                    min_dist = real_distance
                    car_ahead = other
        return car_ahead, min_dist

    @staticmethod
    def generate_neon_color(base_color):
        return tuple(min(255, c + 100) for c in base_color)

    def is_path_completed(self):
        return self.current_waypoint_index >= len(self.waypoints)

    def update(self, dt, controller, all_cars):
        self.glow_pulse += dt * 3
        acceleration = 12.0
        deceleration = 30.0
        emergency_deceleration = 60.0
        target_speed = self.max_speed
        should_stop = False
        reason = None
        light_is_red = self._check_traffic_light(controller)
        dist_to_stopline = self._get_distance_to_stopline(
        ) if light_is_red else float('inf')
        car_ahead, dist_ahead = self._find_car_ahead(all_cars)
        closest_obstacle_dist = float('inf')
        if light_is_red and dist_to_stopline > 0:
            closest_obstacle_dist = dist_to_stopline
            reason = 'light'
        if car_ahead and dist_ahead < closest_obstacle_dist:
            closest_obstacle_dist = dist_ahead
            reason = 'car'
        if closest_obstacle_dist < float('inf'):
            if closest_obstacle_dist <= self.SAFE_DISTANCE:
                should_stop = True
                target_speed = 0
            else:
                available_distance = closest_obstacle_dist - self.SAFE_DISTANCE
                safe_speed = math.sqrt(2 * deceleration * available_distance)
                if reason == 'light':
                    if closest_obstacle_dist > 120:
                        target_speed = min(self.max_speed, safe_speed * 1.05)
                    elif closest_obstacle_dist > 60:
                        target_speed = min(self.max_speed * 0.6, safe_speed *
                                           0.9)
                    elif closest_obstacle_dist > 30:
                        target_speed = safe_speed * 0.7
                    else:
                        target_speed = safe_speed * 0.5
                elif car_ahead:
                    leader_speed = car_ahead.speed
                    if leader_speed > 5:
                        if (closest_obstacle_dist > self.
                                COMFORTABLE_DISTANCE * 2):
                            target_speed = min(leader_speed * 1.05,
                                               safe_speed, self.max_speed)
                        elif closest_obstacle_dist > self.COMFORTABLE_DISTANCE:
                            target_speed = min(leader_speed, safe_speed)
                        elif closest_obstacle_dist > self.SAFE_DISTANCE * 1.5:
                            target_speed = min(leader_speed * 0.8,
                                               safe_speed * 0.8)
                        else:
                            target_speed = min(leader_speed * 0.5,
                                               safe_speed * 0.6)
                    elif closest_obstacle_dist > self.COMFORTABLE_DISTANCE:
                        target_speed = safe_speed * 0.7
                    elif closest_obstacle_dist > self.SAFE_DISTANCE * 2:
                        target_speed = safe_speed * 0.4
                    else:
                        target_speed = min(5, safe_speed * 0.3)
                else:
                    target_speed = safe_speed * 0.8
                if (target_speed < 2 and closest_obstacle_dist > self.
                        SAFE_DISTANCE * 1.8):
                    target_speed = 2
                elif target_speed < 2:
                    target_speed = 0
                    should_stop = True
        self.is_waiting = should_stop
        if self.is_waiting:
            self.waiting_time += dt
        else:
            self.waiting_time = 0.0
        if closest_obstacle_dist < self.SAFE_DISTANCE * 0.8:
            self.speed = 0
            should_stop = True
            self.is_waiting = True
        elif target_speed > self.speed:
            self.speed = min(target_speed, self.speed + acceleration * dt)
        elif target_speed < self.speed:
            speed_diff = self.speed - target_speed
            if closest_obstacle_dist < self.SAFE_DISTANCE * 1.2:
                self.speed = max(target_speed, self.speed -
                                 emergency_deceleration * dt)
            elif closest_obstacle_dist < self.COMFORTABLE_DISTANCE:
                self.speed = max(target_speed, self.speed - deceleration *
                                 1.5 * dt)
            else:
                self.speed = max(target_speed, self.speed - deceleration * dt)
        effective_speed = self.speed
        self._move_towards_waypoint(dt, effective_speed)
        if NUM_LANES < 2:
            return
        road_half = NUM_LANES * LANE_WIDTH / 2
        if abs(self.heading[0]) > abs(self.heading[1]):
            relative_pos = self.pos[1] if self.heading[0] > 0 else -self.pos[1]
            self.current_lane = int((relative_pos + road_half) / LANE_WIDTH)
        else:
            relative_pos = self.pos[0] if self.heading[1] > 0 else -self.pos[0]
            self.current_lane = int((relative_pos + road_half) / LANE_WIDTH)
        self.current_lane = max(0, min(NUM_LANES - 1, self.current_lane))
        possible_lanes = []
        if self.current_lane > 0:
            possible_lanes.append(self.current_lane - 1)
        if self.current_lane < NUM_LANES - 1:
            possible_lanes.append(self.current_lane + 1)
        if not possible_lanes:
            return
        for target_lane in possible_lanes:
            if self.is_lane_safe(target_lane, all_cars):
                self.start_lane_change(target_lane)
                return

    def is_lane_safe(self, target_lane, all_cars):
        road_half = NUM_LANES * LANE_WIDTH / 2
        target_offset = -road_half + target_lane * LANE_WIDTH + LANE_WIDTH / 2
        for other in all_cars:
            if other is self:
                continue
            if abs(self.heading[0] - other.heading[0]) < 0.1 and abs(self.
                                                                             heading[1] - other.heading[1]) < 0.1:
                if abs(self.heading[0]) > abs(self.heading[1]):
                    other_offset = other.pos[1] if self.heading[0
                                                   ] > 0 else -other.pos[1]
                else:
                    other_offset = other.pos[0] if self.heading[1
                                                   ] > 0 else -other.pos[0]
                if abs(other_offset - target_offset) < LANE_WIDTH / 2:
                    dx = other.pos[0] - self.pos[0]
                    dy = other.pos[1] - self.pos[1]
                    dist = math.hypot(dx, dy)
                    if dist < self.LANE_CHANGE_DISTANCE:
                        return False
        return True

    def start_lane_change(self, target_lane):
        self.is_changing_lane = True
        self.target_lane = target_lane
        self.lane_change_progress = 0.0
        self.lane_change_start_pos = list(self.pos)
        road_half = NUM_LANES * LANE_WIDTH / 2
        self.lane_change_target_offset = (-road_half + target_lane *
                                          LANE_WIDTH + LANE_WIDTH / 2)
        self.last_lane_change_time = 0

    def update_lane_change(self, dt, speed):
        lane_change_speed = 0.8
        self.lane_change_progress += lane_change_speed * dt
        if self.lane_change_progress >= 1.0:
            self.is_changing_lane = False
            self.lane_change_progress = 0.0
            self.current_lane = self.target_lane
        else:
            t = self.ease_in_out_cubic(self.lane_change_progress)
            self.pos[0] += self.heading[0] * speed * dt
            self.pos[1] += self.heading[1] * speed * dt
            if abs(self.heading[0]) > abs(self.heading[1]):
                start_offset = self.lane_change_start_pos[1] if self.heading[0
                                                                ] > 0 else -self.lane_change_start_pos[1]
                current_offset = start_offset + (self.
                                                 lane_change_target_offset - start_offset) * t
                self.pos[1] = current_offset if self.heading[0
                                                ] > 0 else -current_offset
            else:
                start_offset = self.lane_change_start_pos[0] if self.heading[1
                                                                ] > 0 else -self.lane_change_start_pos[0]
                current_offset = start_offset + (self.
                                                 lane_change_target_offset - start_offset) * t
                self.pos[0] = current_offset if self.heading[1
                                                ] > 0 else -current_offset

    def check_start_turn(self):
        road_half = NUM_LANES * LANE_WIDTH / 2
        at_intersection = -road_half < self.pos[0
        ] < road_half and -road_half < self.pos[1] < road_half
        if at_intersection and self.turn_direction != 'straight':
            self.start_turn()

    def start_turn(self):
        self.is_turning = True
        self.turn_progress = 0.0
        turn_radius = 35
        if self.turn_direction == 'left':
            if abs(self.heading[0]) > abs(self.heading[1]):
                self.turn_center = [self.pos[0], self.pos[1] + turn_radius *
                                    (1 if self.heading[0] > 0 else -1)]
                self.turn_start_angle = math.atan2(self.pos[1] - self.
                                                   turn_center[1], self.pos[0] - self.turn_center[0])
            else:
                self.turn_center = [self.pos[0] - turn_radius * (1 if self.
                                                                 heading[1] > 0 else -1), self.pos[1]]
                self.turn_start_angle = math.atan2(self.pos[1] - self.
                                                   turn_center[1], self.pos[0] - self.turn_center[0])
        elif abs(self.heading[0]) > abs(self.heading[1]):
            self.turn_center = [self.pos[0], self.pos[1] - turn_radius * (1 if
                                                                          self.heading[0] > 0 else -1)]
            self.turn_start_angle = math.atan2(self.pos[1] - self.
                                               turn_center[1], self.pos[0] - self.turn_center[0])
        else:
            self.turn_center = [self.pos[0] + turn_radius * (1 if self.
                                                             heading[1] > 0 else -1), self.pos[1]]
            self.turn_start_angle = math.atan2(self.pos[1] - self.
                                               turn_center[1], self.pos[0] - self.turn_center[0])

    def update_turn(self, dt, speed):
        turn_radius = 35
        turn_speed = 0.7
        self.turn_progress += turn_speed * dt
        if self.turn_progress >= 1.0:
            self.is_turning = False
            self.turn_progress = 0.0
            if self.turn_direction == 'left':
                if abs(self.original_heading[0]) > abs(self.original_heading[1]
                                                       ):
                    self.heading = [0, self.original_heading[0]]
                    self.target_heading = [0, self.original_heading[0]]
                else:
                    self.heading = [-self.original_heading[1], 0]
                    self.target_heading = [-self.original_heading[1], 0]
            elif self.turn_direction == 'right':
                if abs(self.original_heading[0]) > abs(self.original_heading[1]
                                                       ):
                    self.heading = [0, -self.original_heading[0]]
                    self.target_heading = [0, -self.original_heading[0]]
                else:
                    self.heading = [self.original_heading[1], 0]
                    self.target_heading = [self.original_heading[1], 0]
        else:
            eased_progress = self.ease_in_out_quintic(self.turn_progress)
            total_angle = math.pi / 2
            current_angle = (self.turn_start_angle + total_angle *
                             eased_progress * (1 if self.turn_direction == 'left' else -1))
            self.pos[0] = self.turn_center[0] + turn_radius * math.cos(
                current_angle)
            self.pos[1] = self.turn_center[1] + turn_radius * math.sin(
                current_angle)
            self.heading[0] = -math.sin(current_angle) * (1 if self.
                                                          turn_direction == 'left' else -1)
            self.heading[1] = math.cos(current_angle) * (1 if self.
                                                         turn_direction == 'left' else -1)

    @staticmethod
    def ease_in_out_cubic(t):
        if t < 0.5:
            return 4 * t * t * t
        else:
            return 1 - pow(-2 * t + 2, 3) / 2

    @staticmethod
    def ease_in_out_quintic(t):
        if t < 0.5:
            return 16 * t * t * t * t * t
        else:
            return 1 - pow(-2 * t + 2, 5) / 2

    def draw(self, screen):
        x, y = self.pos
        angle = math.degrees(math.atan2(self.heading[1], self.heading[0]))
        car_length = self.length * 2.5
        car_width = self.width * 2.5
        glow_size = int(8 + 4 * math.sin(self.glow_pulse))
        glow_surf = pygame.Surface((car_length + glow_size * 2, car_width +
                                    glow_size * 2), pygame.SRCALPHA)
        for i in range(glow_size, 0, -1):
            alpha = int(80 * (1 - i / glow_size))
            glow_color = *self.neon_color, alpha
            pygame.draw.rect(glow_surf, glow_color, (glow_size - i,
                                                     glow_size - i, car_length + i * 2, car_width + i * 2),
                             border_radius=6)
        rotated_glow = pygame.transform.rotate(glow_surf, -angle)
        glow_rect = rotated_glow.get_rect(center=(x, y))
        screen.blit(rotated_glow, glow_rect)
        rect_surf = pygame.Surface((car_length, car_width), pygame.SRCALPHA)
        dark_color = tuple(min(80, c // 3) for c in self.color)
        pygame.draw.rect(rect_surf, dark_color, (0, 0, car_length,
                                                 car_width), border_radius=6)
        for i in range(3):
            pygame.draw.rect(rect_surf, (*self.neon_color, 150 - i * 50), (
                i, i, car_length - i * 2, car_width - i * 2), 2,
                             border_radius=6)
        window_color = 20, 40, 60, 200
        window_width = car_length * 0.3
        window_spacing = car_length * 0.15
        pygame.draw.rect(rect_surf, window_color, (car_length -
                                                   window_spacing - window_width, car_width * 0.15, window_width,
                                                   car_width * 0.7), border_radius=3)
        pygame.draw.rect(rect_surf, window_color, (window_spacing,
                                                   car_width * 0.15, window_width, car_width * 0.7), border_radius=3)
        pygame.draw.rect(rect_surf, (*self.neon_color, 100), (car_length -
                                                              window_spacing - window_width, car_width * 0.15,
                                                              window_width,
                                                              car_width * 0.7), 1, border_radius=3)
        if self.is_waiting:
            light_x = 8
            for offset in [0.25, 0.75]:
                glow_surf_light = pygame.Surface((16, 16), pygame.SRCALPHA)
                pygame.draw.circle(glow_surf_light, (255, 0, 0, 150), (8, 8), 8
                                   )
                pygame.draw.circle(glow_surf_light, (255, 0, 0, 80), (8, 8), 10
                                   )
                rect_surf.blit(glow_surf_light, (light_x - 8, car_width *
                                                 offset - 8))
                pygame.draw.circle(rect_surf, (255, 50, 50), (int(light_x),
                                                              int(car_width * offset)), 4)
                pygame.draw.circle(rect_surf, (255, 150, 150), (int(light_x
                                                                    ), int(car_width * offset)), 2)
        else:
            light_x = car_length - 8
            for offset in [0.25, 0.75]:
                glow_surf_light = pygame.Surface((20, 20), pygame.SRCALPHA)
                pygame.draw.circle(glow_surf_light, (100, 200, 255, 120), (
                    10, 10), 10)
                pygame.draw.circle(glow_surf_light, (150, 220, 255, 60), (
                    10, 10), 12)
                rect_surf.blit(glow_surf_light, (light_x - 10, car_width *
                                                 offset - 10))
                pygame.draw.circle(rect_surf, (200, 240, 255), (int(light_x
                                                                    ), int(car_width * offset)), 4)
                pygame.draw.circle(rect_surf, (255, 255, 255), (int(light_x
                                                                    ), int(car_width * offset)), 2)
        stripe_y_top = car_width * 0.2
        stripe_y_bottom = car_width * 0.8
        pygame.draw.line(rect_surf, (*self.neon_color, 180), (car_length *
                                                              0.2, stripe_y_top), (car_length * 0.8, stripe_y_top), 2)
        pygame.draw.line(rect_surf, (*self.neon_color, 180), (car_length *
                                                              0.2, stripe_y_bottom),
                         (car_length * 0.8, stripe_y_bottom), 2)
        rotated = pygame.transform.rotate(rect_surf, -angle)
        rect = rotated.get_rect(center=(x, y))
        screen.blit(rotated, rect)


class Pedestrian(basic.basic_similation_element,TrafficController):

    def __init__(self, pos, goal, speed, color, size):
        super().__init__()
        self.pos = list(pos)
        self.goal = goal
        self.speed = speed*random.randint(3,6)
        self.color = color
        self.is_going = 0
        self.neon_color = tuple(min(255, c + 120) for c in color)
        self.size = size
        self.glow_pulse = random.uniform(0, math.pi * 2)

    def update(self, dt, controller):
        self.glow_pulse += dt * 4
        can_cross = controller.is_all_red() and controller.timer < 0.2
        if can_cross or self.is_going:
            self.is_going = 1
            dx = self.goal[0] - self.pos[0]
            dy = self.goal[1] - self.pos[1]
            dist = math.hypot(dx, dy)
            if dist > 1:
                move_dist = self.speed * dt
                self.pos[0] += move_dist * (dx / dist)
                self.pos[1] += move_dist * (dy / dist)

    def draw(self, screen):
        glow_intensity = int(100 + 60 * math.sin(self.glow_pulse))
        glow_surf = pygame.Surface((self.size * 6, self.size * 6), pygame.
                                   SRCALPHA)
        for i in range(self.size * 2, 0, -1):
            alpha = int(glow_intensity * (1 - i / (self.size * 2)))
            pygame.draw.circle(glow_surf, (*self.neon_color, alpha), (self.
                                                                      size * 3, self.size * 3), i)
        screen.blit(glow_surf, (int(self.pos[0]) - self.size * 3, int(self.
                                                                      pos[1]) - self.size * 3))
        dark_color = tuple(c // 3 for c in self.color)
        pygame.draw.circle(screen, dark_color, (int(self.pos[0]), int(self.
                                                                      pos[1])), self.size)
        pygame.draw.circle(screen, self.neon_color, (int(self.pos[0]), int(
            self.pos[1])), self.size, 2)
        pygame.draw.circle(screen, self.neon_color, (int(self.pos[0]), int(
            self.pos[1])), self.size // 2)


class TrafficSimulation:

    def __init__(self):
        self.controller = TrafficController()
        self.cars: list[Car] = []
        self.peds: list[Pedestrian] = []
        self.pedestrians: list[Pedestrian] = self.peds
        self.paused: bool = False
        self.last_car_spawns = {d: (0) for d in DIR_INS}
        self.last_ped_spawn = 0
        self.ped_spawn_interval = 3.0
        self.current_phase = 0
        self.phase_time = 0.0
        self.waiting_cars_h = 0
        self.waiting_cars_v = 0
        self.h_wait_time_sq_sum = 0.0
        self.v_wait_time_sq_sum = 0.0
        self.speed_multiplier = 1.0

    def update_screen_size(self):
        self.controller.update_light_positions()

    def toggle_pause(self):
        self.paused = not self.paused

    def can_spawn_car(self, direction):
        info = pygame.display.Info()
        window_width = info.current_w
        window_height = info.current_h
        road_half = NUM_LANES * LANE_WIDTH / 2
        spawn_margin = 50
        window_half_width = window_width / 2
        window_half_height = window_height / 2
        min_spawn_distance = 80
        if direction == 'from_west':
            spawn_x = -window_half_width - spawn_margin
            for car in self.cars:
                if car.from_direction == 'from_west' and abs(car.pos[0] -
                                                             spawn_x) < min_spawn_distance:
                    return False
        elif direction == 'from_east':
            spawn_x = window_half_width + spawn_margin
            for car in self.cars:
                if car.from_direction == 'from_east' and abs(car.pos[0] -
                                                             spawn_x) < min_spawn_distance:
                    return False
        elif direction == 'from_north':
            spawn_y = -window_half_height - spawn_margin
            for car in self.cars:
                if car.from_direction == 'from_north' and abs(car.pos[1] -
                                                              spawn_y) < min_spawn_distance:
                    return False
        elif direction == 'from_south':
            spawn_y = window_half_height + spawn_margin
            for car in self.cars:
                if car.from_direction == 'from_south' and abs(car.pos[1] -
                                                              spawn_y) < min_spawn_distance:
                    return False
        return True

    def spawn_car(self, direction):
        lane = random.randint(0, 1)
        turn_direction = random.choices(['straight', 'left', 'right'],
                                        weights=[0.6, 0.2, 0.2])[0]
        waypoints = PathGenerator.generate_waypoints(direction, lane,
                                                     turn_direction)
        speed = random.uniform(SPEED_MIN, SPEED_MAX)
        color = random.choice([RED, GREEN, BLUE, YELLOW, WHITE])
        car = Car(waypoints, speed, color, direction, turn_direction)
        self.cars.append(car)

    def spawn_pedestrian(self):
        road_half = NUM_LANES * LANE_WIDTH / 2
        sidewalk_dist = road_half + SIDEWALK_WIDTH / 2
        start_x_sign = random.choice([-1, 1])
        start_y_sign = random.choice([-1, 1])
        start_pos = start_x_sign * sidewalk_dist, start_y_sign * sidewalk_dist
        if random.choice([True, False]):
            goal_pos = start_pos[0], -start_pos[1]
        else:
            goal_pos = -start_pos[0], start_pos[1]
        speed = random.uniform(PED_SPEED_MIN, PED_SPEED_MAX)
        self.peds.append(Pedestrian(start_pos, goal_pos, speed, (200, 200,
                                                                 255), 2))

    def update(self, dt):
        if self.paused:
            return
        self.waiting_cars_h = 0
        self.waiting_cars_v = 0
        self.h_wait_time_sq_sum = 0.0
        self.v_wait_time_sq_sum = 0.0
        visible_cars_h = 0
        visible_cars_v = 0
        road_half = NUM_LANES * LANE_WIDTH / 2
        for car in self.cars:
            dist_to_intersection = 0
            if abs(car.heading[0]) > abs(car.heading[1]):
                if car.heading[0] > 0:
                    dist_to_intersection = -road_half - car.pos[0]
                else:
                    dist_to_intersection = car.pos[0] - road_half
            elif car.heading[1] > 0:
                dist_to_intersection = -road_half - car.pos[1]
            else:
                dist_to_intersection = car.pos[1] - road_half
            if 0 < dist_to_intersection < CAR_VISIBILITY_RANGE:
                if abs(car.heading[0]) > abs(car.heading[1]):
                    visible_cars_h += 1
                else:
                    visible_cars_v += 1
            if car.is_waiting:
                if abs(car.heading[0]) > abs(car.heading[1]):
                    self.waiting_cars_h += 1
                    self.h_wait_time_sq_sum += car.waiting_time ** 2
                else:
                    self.waiting_cars_v += 1
                    self.v_wait_time_sq_sum += car.waiting_time ** 2
        self.controller.update(dt, self.waiting_cars_h, self.waiting_cars_v,
                               self.h_wait_time_sq_sum, self.v_wait_time_sq_sum,
                               visible_cars_h, visible_cars_v)
        self.current_phase = self.controller.current_phase
        self.phase_time = self.controller.timer
        for direction in DIR_INS:
            density = self.controller.traffic_density.get(direction, 0.0)
            if density > 0:
                interval = 10.0 / density
                self.last_car_spawns[direction] += dt
                if self.last_car_spawns[direction] >= interval and len(self
                                                                               .cars) < MAX_CARS:
                    if self.can_spawn_car(direction):
                        self.spawn_car(direction)
                        self.last_car_spawns[direction] = 0
                    else:
                        self.last_car_spawns[direction] = interval - 0.5
        self.last_ped_spawn += dt
        if self.last_ped_spawn > self.ped_spawn_interval and len(self.peds) < 50:
            self.spawn_pedestrian()
            self.last_ped_spawn = 0
        for car in self.cars:
            car.update(dt, self.controller, self.cars)
        for ped in self.peds:
            ped.update(dt, self.controller)
        from constants import screen_config
        limit_x = screen_config.sim_width / 2 + 100
        limit_y = screen_config.sim_height / 2 + 100
        self.cars = [c for c in self.cars if not c.is_path_completed() and
                     -limit_x < c.pos[0] < limit_x and -limit_y < c.pos[1] < limit_y]
        self.peds[:] = [p for p in self.peds if math.hypot(p.pos[0] - p.
                                                           goal[0], p.pos[1] - p.goal[1]) > 5]

    def draw(self, screen):
        for car in self.cars:
            car.draw(screen)
        for ped in self.peds:
            ped.draw(screen)
