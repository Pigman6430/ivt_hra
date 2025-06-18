import pygame
import math
pygame.init()
screen = pygame.display.set_mode((1500, 800))

class Plane(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.original_image = pygame.image.load('plane.png').convert_alpha()
        self.original_image = pygame.transform.scale(self.original_image, (120, 40))
        self.image = self.original_image
        self.rect = self.image.get_rect()

        img_center_x = self.original_image.get_width() / 2
        img_center_y = self.original_image.get_height() / 2
        self.front_gear_offset = pygame.math.Vector2(img_center_x * 0.6, img_center_y)
        self.rear_gear_offset = pygame.math.Vector2(-img_center_x * 0.3, img_center_y)

        self.pos = pygame.math.Vector2(800, 600)
        self.velocity = pygame.math.Vector2(0, 0)
        self.angle = 0.0
        self.throttle = 0.0
        self.state = 'grounded'
        self.angle_of_attack = 0.0

        self.mass = 100.0
        self.GRAVITY_FORCE = 9.81 * self.mass
        self.THRUST_POWER = 10000.0
        self.LIFT_COEFFICIENT = 0.0005
        self.DRAG_COEFFICIENT = 0.001
        self.CRITICAL_AOA = 20.0
        self.DAMPING_FACTOR = 1.5
        self.BRAKE_POWER = 150
        self.GROUND_FRICTION = 0.8
        self.MIN_TAKEOFF_SPEED = 200
        self.MAX_LANDING_SPEED_V = 200
        
    def update(self, dt, get_terrain_height_func):
        if self.state == 'crashed':
            self.velocity *= 0.9
            self.pos += self.velocity * dt
            self.angle += (0 - self.angle) * 0.01 
            return

        angle_rad = math.radians(-self.angle)
        thrust_direction = pygame.math.Vector2(math.cos(angle_rad), math.sin(angle_rad))
        thrust = thrust_direction * self.throttle * self.THRUST_POWER
        
        gravity = pygame.math.Vector2(0, self.GRAVITY_FORCE)

        speed = self.velocity.length()
        lift = pygame.math.Vector2(0, 0)
        drag = pygame.math.Vector2(0, 0)
        velocity_angle = 0

        if speed > 1.0:
            drag = -self.velocity.normalize() * speed * speed * self.DRAG_COEFFICIENT
            
            velocity_angle = math.degrees(math.atan2(-self.velocity.y, self.velocity.x))
            self.angle_of_attack = self.angle - velocity_angle
            
            lift_direction = self.velocity.rotate(90).normalize()
            
            if abs(self.angle_of_attack) > self.CRITICAL_AOA:
                lift_magnitude = 0
            else:
                lift_magnitude = speed * speed * self.LIFT_COEFFICIENT * math.sin(math.radians(2 * self.angle_of_attack))
            
            lift = -lift_direction * lift_magnitude

        if self.state == 'flying':
            if speed > 10.0:
                angle_diff = (velocity_angle - self.angle + 180) % 360 - 180
                self.angle += angle_diff * self.DAMPING_FACTOR * dt

            net_force = thrust + gravity + lift + drag
            acceleration = net_force / self.mass
            self.velocity += acceleration * dt
            self.pos += self.velocity * dt
            
            self.check_ground_collision(get_terrain_height_func, dt)

        elif self.state == 'grounded':
            friction = -self.velocity * self.GROUND_FRICTION
            
            net_force = thrust + friction
            acceleration = net_force / self.mass
            self.velocity += acceleration * dt
            self.pos += self.velocity * dt
            
            self.snap_to_ground(get_terrain_height_func, dt)

            if speed > self.MIN_TAKEOFF_SPEED and self.angle > 0:
                self.state = 'flying'
                self.velocity.y -= 75

        self.image = pygame.transform.rotate(self.original_image, self.angle)
        self.rect = self.image.get_rect(center=self.pos)
        
    def check_ground_collision(self, get_terrain_height_func, dt):
        front_gear_world_pos = self.pos + self.front_gear_offset.rotate(-self.angle)
        rear_gear_world_pos = self.pos + self.rear_gear_offset.rotate(-self.angle)

        ground_y_front = get_terrain_height_func(front_gear_world_pos.x)
        ground_y_rear = get_terrain_height_func(rear_gear_world_pos.x)

        if front_gear_world_pos.y >= ground_y_front or rear_gear_world_pos.y >= ground_y_rear:
            if abs(self.velocity.y) > self.MAX_LANDING_SPEED_V:
                self.state = 'crashed'
                self.throttle = 0
            else:
                self.state = 'grounded'
                self.velocity.y = 0
                self.snap_to_ground(get_terrain_height_func, dt)

    def snap_to_ground(self, get_terrain_height_func, dt):
        front_gear_pos = self.pos + self.front_gear_offset.rotate(-self.angle)
        rear_gear_pos = self.pos + self.rear_gear_offset.rotate(-self.angle)

        ground_y_front = get_terrain_height_func(front_gear_pos.x)
        ground_y_rear = get_terrain_height_func(rear_gear_pos.x)
        
        dx = front_gear_pos.x - rear_gear_pos.x
        dy = ground_y_front - ground_y_rear
        ground_angle = -math.degrees(math.atan2(dy, dx)) if dx != 0 else 0

        angle_diff = (ground_angle - self.angle + 180) % 360 - 180
        self.angle += angle_diff * 5 * dt
        
        rotated_front_offset = self.front_gear_offset.rotate(-self.angle)
        rotated_rear_offset = self.rear_gear_offset.rotate(-self.angle)
        
        target_y_front = ground_y_front - rotated_front_offset.y
        target_y_rear = ground_y_rear - rotated_rear_offset.y
        
        self.pos.y = max(target_y_front, target_y_rear)