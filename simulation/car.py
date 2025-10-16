        # Простое движение вперед
        else:
            self.x += self.speed * math.cos(self.angle)
            self.y += self.speed * math.sin(self.angle)

    def smooth_turn(self, target_angle):
        # Плавный поворот к целевому углу
        angle_diff = (target_angle - self.angle + math.pi) % (2 * math.pi) - math.pi
        turn_step = 0.02  # Очень маленький шаг для максимальной плавности
        if abs(angle_diff) > turn_step:
            self.angle += turn_step if angle_diff > 0 else -turn_step
        else:
            self.angle = target_angle
            self.is_turning = False # Завершаем поворот

    def is_past_intersection(self, intersection):
        # Проверяем, проехал ли автомобиль перекресток
        if self.direction == "up" and self.y < intersection.y - intersection.size / 2:
            return True
        if self.direction == "down" and self.y > intersection.y + intersection.size / 2:
            return True
        if self.direction == "left" and self.x < intersection.x - intersection.size / 2:
            return True
        if self.direction == "right" and self.x > intersection.x + intersection.size / 2:
            return True
        return False
