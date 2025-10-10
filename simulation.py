# simulation.py
import random
import math
from entities import Vehicle, Pedestrian
from traffic_controller import TrafficController
from constants import *

class Simulation:
    def __init__(self):
        self.cars = []
        self.peds = []
        self.controller = TrafficController()
        self.next_car_times = {d: 0 for d in DIR_INS}
        self.next_ped_times = {'horizontal': 0, 'vertical': 0}
        self.paused = False
        self.completed_wait_times = []
        self.interval_min = INTERVAL_MIN
        self.interval_max = INTERVAL_MAX
        self.speed_min = SPEED_MIN
        self.speed_max = SPEED_MAX
        self.green_time = LIGHT_GREEN
        self.yellow_time = LIGHT_YELLOW
        self.red_time = LIGHT_RED

    def generate_entities(self, current_time):
        if len(self.cars) >= MAX_CARS:
            return
        for d in DIR_INS:
            if current_time > self.next_car_times[d]:
                self.cars.append(Vehicle(d))
                interval = random.uniform(self.interval_min, self.interval_max)
                self.next_car_times[d] = current_time + interval
        for cross in ['horizontal', 'vertical']:
            if current_time > self.next_ped_times[cross]:
                if random.random() < PED_GROUP_PROB:
                    group_size = random.randint(*PED_GROUP_SIZE)
                    base_pos = Pedestrian(cross).get_initial_pos()  # Base for group
                    for _ in range(group_size):
                        group_offset = (random.uniform(-3, 3), random.uniform(-3, 3))
                        group_pos = (base_pos[0] + group_offset[0], base_pos[1] + group_offset[1])
                        self.peds.append(Pedestrian(cross, group_pos))
                else:
                    self.peds.append(Pedestrian(cross))
                self.next_ped_times[cross] = current_time + random.uniform(PED_INTERVAL_MIN, PED_INTERVAL_MAX)

    def group_cars(self):
        groups = {d: {l: [] for l in range(NUM_LANES)} for d in DIR_INS}
        for c in self.cars:
            if not c.has_turned:
                groups[c.dir_in][c.lane].append(c)
        for g in groups.values():
            for lane_cars in g.values():
                lane_cars.sort(key=lambda c: c.dist_to_inter)  # Smallest dist (front) first
        return groups

    def update(self, dt, current_time):
        if self.paused:
            return

        self.generate_entities(current_time)

        h_wait = [c.wait_time for c in self.cars if c.dir_in in ('from_west', 'from_east') and c.stopped] + \
                 [p.wait_time for p in self.peds if p.cross == 'horizontal' and p.stopped]
        v_wait = [c.wait_time for c in self.cars if c.dir_in in ('from_north', 'from_south') and c.stopped] + \
                 [p.wait_time for p in self.peds if p.cross == 'vertical' and p.stopped]

        self.controller.green_time = self.green_time
        self.controller.yellow_time = self.yellow_time
        self.controller.red_time = self.red_time
        self.controller.update(dt, h_wait, v_wait)

        groups = self.group_cars()

        new_cars = []
        for c in self.cars:
            road = 'horizontal' if c.dir_in in ('from_west', 'from_east') else 'vertical'
            light_color = self.controller.get_color(road)

            if not c.has_turned:
                # Lane change logic
                target_lane = 0 if c.turn == 1 else (NUM_LANES - 1 if c.turn == 2 else None)
                if target_lane is None and c.dist_to_inter < VISIBILITY * 1.5:
                    lane_cars = groups[c.dir_in][c.lane]
                    if c in lane_cars:
                        idx = lane_cars.index(c)
                        front = lane_cars[idx - 1] if idx > 0 else None
                        if front and front.current_speed < c.target_speed * 0.8 and c.dist_to_inter > 50:
                            for dl in [-1, 1]:
                                tl = c.lane + dl
                                if 0 <= tl < NUM_LANES:
                                    safe = True
                                    for other in groups[c.dir_in][tl]:
                                        if abs(c.dist_to_inter - other.dist_to_inter) < SAFE_LANE_CHANGE_DIST:
                                            safe = False
                                            break
                                    if safe:
                                        c.lane = tl
                                        c.update_lane_pos()
                                        break

                if target_lane is not None and target_lane != c.lane and 50 < c.dist_to_inter < 200:
                    safe = True
                    for other in groups[c.dir_in][target_lane]:
                        if abs(c.dist_to_inter - other.dist_to_inter) < SAFE_LANE_CHANGE_DIST:
                            safe = False
                            break
                    if safe:
                        c.lane = target_lane
                        c.update_lane_pos()

            # Target speed
            target_speed = c.target_speed
            if c.dist_to_inter < VISIBILITY:
                if light_color == 'red' or (light_color == 'yellow' and c.dist_to_inter / max(1, c.current_speed) > self.controller.yellow_time + 1):
                    target_speed = 0

            if not c.has_turned:
                lane_cars = groups.get(c.dir_in, {}).get(c.lane, [])
                if c in lane_cars:
                    idx = lane_cars.index(c)
                    front = lane_cars[idx - 1] if idx > 0 else None
                    if front:
                        dist_front = c.dist_to_inter - front.dist_to_inter - (c.length + front.length) / 2
                        if dist_front < SAFE_DIST + c.current_speed * dt:
                            target_speed = min(target_speed, front.current_speed)
                        if dist_front < SAFE_DIST / 2:
                            target_speed = 0

            c.accelerate(dt, target_speed)
            c.move(dt)

            # Wait time when approaching red or slowed
            if c.dist_to_inter < VISIBILITY and c.current_speed < c.target_speed * 0.9:
                c.wait_time += dt
                c.stopped = True
            else:
                if c.stopped:
                    self.completed_wait_times.append(c.wait_time)
                    c.wait_time = 0  # Reset after adding
                c.stopped = False

            # Turning
            if c.dist_to_inter <= 0 and not c.has_turned:
                if light_color == 'green' or (light_color == 'yellow' and c.dist_to_inter > -10):
                    c.heading = TURN_HEADINGS[c.dir_in][c.turn]
                    c.has_turned = True
                    c.dist_to_inter = -c.dist_to_inter  # Now moving away
                    c.update_lane_pos()  # Adjust lane post-turn if needed
                else:
                    c.current_speed = 0

            if abs(c.pos[0]) > ROAD_SIZE + 50 or abs(c.pos[1]) > ROAD_SIZE + 50:
                continue
            new_cars.append(c)
        self.cars = new_cars

        # Update peds with forces
        new_peds = []
        for p in self.peds:
            can_go = self.controller.get_ped_color(p.cross) == 'green'
            p.move(dt, can_go, self.peds)
            crossed = abs(p.pos[0]) > NUM_LANES * LANE_WIDTH / 2 + 10 or abs(p.pos[1]) > NUM_LANES * LANE_WIDTH / 2 + 10
            if not crossed:
                new_peds.append(p)
        self.peds = new_peds

    def detect_collisions(self):
        for i, c1 in enumerate(self.cars):
            for c2 in self.cars[i+1:]:
                dist = math.hypot(c1.pos[0] - c2.pos[0], c1.pos[1] - c2.pos[1])
                if dist < (c1.length + c2.length) / 2:
                    # Instead of pass, slow down or stop
                    if c1.current_speed > c2.current_speed:
                        c1.current_speed = max(0, c1.current_speed - c1.brake_rate * 0.1)
                    else:
                        c2.current_speed = max(0, c2.current_speed - c2.brake_rate * 0.1)
        # Ped-car avoidance
        for p in self.peds:
            for c in self.cars:
                dist = math.hypot(p.pos[0] - c.pos[0], p.pos[1] - c.pos[1])
                if dist < 10:  # Increased range
                    p.current_speed *= 0.5  # Slow ped
                    c.current_speed *= 0.5  # Slow car