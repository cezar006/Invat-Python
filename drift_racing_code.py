import pygame
import math
import random

pygame.init()

# --------------------------------------------------
# SETTINGS
# --------------------------------------------------
WIDTH, HEIGHT = 1280, 720
WORLD_W, WORLD_H = 3000, 2200

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Python Drift Racing")

clock = pygame.time.Clock()

# Colors
GRASS = (45, 120, 55)
ROAD = (55, 55, 60)
ROAD_EDGE = (220, 220, 220)
RED = (220, 50, 50)
WHITE = (245, 245, 245)
BLACK = (20, 20, 20)
YELLOW = (255, 210, 40)


# --------------------------------------------------
# CAR
# --------------------------------------------------
class Car:
    def __init__(self, x, y):
        self.x = x
        self.y = y

        self.angle = 0

        self.vx = 0
        self.vy = 0

        self.acceleration = 0.38
        self.brake_power = 0.25

        self.max_speed = 15
        self.reverse_speed = 6

        self.turn_speed = 3.0

        # Lower grip = more drift
        self.grip = 0.91

        self.width = 72
        self.height = 38

        self.skid_marks = []

    def update(self, keys):

        angle_rad = math.radians(self.angle)

        forward_x = math.cos(angle_rad)
        forward_y = -math.sin(angle_rad)

        # Acceleration
        if keys[pygame.K_w] or keys[pygame.K_UP]:
            self.vx += forward_x * self.acceleration
            self.vy += forward_y * self.acceleration

        # Brake / reverse
        if keys[pygame.K_s] or keys[pygame.K_DOWN]:
            self.vx -= forward_x * self.brake_power
            self.vy -= forward_y * self.brake_power

        speed = math.hypot(self.vx, self.vy)

        # Steering depends on movement
        if speed > 0.4:

            steering_strength = min(speed / 5, 1)

            if keys[pygame.K_a] or keys[pygame.K_LEFT]:
                self.angle += self.turn_speed * steering_strength

            if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
                self.angle -= self.turn_speed * steering_strength

        # --------------------------------------------------
        # DRIFT PHYSICS
        # --------------------------------------------------

        forward_velocity = (
            self.vx * forward_x +
            self.vy * forward_y
        )

        desired_vx = forward_x * forward_velocity
        desired_vy = forward_y * forward_velocity

        drifting = keys[pygame.K_SPACE]

        if drifting:
            grip = 0.965
        else:
            grip = self.grip

        self.vx = self.vx * grip + desired_vx * (1 - grip)
        self.vy = self.vy * grip + desired_vy * (1 - grip)

        # Natural friction
        self.vx *= 0.992
        self.vy *= 0.992

        # Limit speed
        speed = math.hypot(self.vx, self.vy)

        if speed > self.max_speed:
            scale = self.max_speed / speed
            self.vx *= scale
            self.vy *= scale

        # Tire marks if sliding fast
        velocity_angle = math.atan2(-self.vy, self.vx)

        drift_angle = abs(
            (velocity_angle - angle_rad + math.pi)
            % (2 * math.pi)
            - math.pi
        )

        if speed > 5 and drift_angle > 0.18:
            rear_distance = 25

            rear_x = self.x - forward_x * rear_distance
            rear_y = self.y - forward_y * rear_distance

            side_x = math.sin(angle_rad) * 14
            side_y = math.cos(angle_rad) * 14

            self.skid_marks.append(
                (
                    rear_x + side_x,
                    rear_y + side_y,
                    rear_x - side_x,
                    rear_y - side_y
                )
            )

        if len(self.skid_marks) > 1500:
            self.skid_marks = self.skid_marks[-1500:]

        self.x += self.vx
        self.y += self.vy

        self.x = max(50, min(WORLD_W - 50, self.x))
        self.y = max(50, min(WORLD_H - 50, self.y))

    def draw(self, screen, camera_x, camera_y):

        # Tire marks
        for x1, y1, x2, y2 in self.skid_marks:
            pygame.draw.circle(
                screen,
                (0, 0, 255),
        #        (35, 35, 35),
                (int(x1 - camera_x), int(y1 - camera_y)),
                58
            )

            pygame.draw.circle(
                screen,
                (0, 0, 255),
                (int(x2 - camera_x), int(y2 - camera_y)),
                58
            )

        # Create car
        car_surface = pygame.Surface(
            (self.width, self.height),
            pygame.SRCALPHA
        )

        # Body
        pygame.draw.rect(
            car_surface,
            (120,0,128),
            (2, 2, self.width + 40, self.height + 40),
            border_radius=8
        )

        # Windshield
        pygame.draw.rect(
            car_surface,
            (50, 90, 120),
            (25, 5, 23, 28),
            border_radius=4
        )

        # Hood stripe
        pygame.draw.rect(
            car_surface,
            RED,
            (50, 5, 12, 28)
        )

        # Headlights
        pygame.draw.rect(
            car_surface,
            YELLOW,
            (62, 5, 7, 8)
        )

        pygame.draw.rect(
            car_surface,
            YELLOW,
            (62, 25, 7, 8)
        )

        # Wheels
        pygame.draw.rect(car_surface, BLACK, (12, -1, 15, 5))
        pygame.draw.rect(car_surface, BLACK, (12, 34, 15, 5))

        pygame.draw.rect(car_surface, BLACK, (50, -1, 15, 5))
        pygame.draw.rect(car_surface, BLACK, (50, 34, 15, 5))

        rotated = pygame.transform.rotate(
            car_surface,
            self.angle
        )

        rect = rotated.get_rect(
            center=(
                self.x - camera_x,
                self.y - camera_y
            )
        )

        screen.blit(rotated, rect)


# --------------------------------------------------
# TRACK
# --------------------------------------------------
def draw_track(screen, camera_x, camera_y):

    screen.fill(GRASS)

    # Main giant circuit
    outer = pygame.Rect(
        250 - camera_x,
        250 - camera_y,
        2500,
        1650
    )

    pygame.draw.rect(
        screen,
        ROAD_EDGE,
        outer,
        border_radius=250
    )

    inner = pygame.Rect(
        370 - camera_x,
        370 - camera_y,
        2260,
        1410
    )

    pygame.draw.rect(
        screen,
        ROAD,
        inner,
        border_radius=200
    )

    # Inner grass island
    island = pygame.Rect(
        750 - camera_x,
        650 - camera_y,
        1500,
        850
    )

    pygame.draw.rect(
        screen,
        GRASS,
        island,
        border_radius=170
    )

    # Center road
    pygame.draw.rect(
        screen,
        ROAD,
        (
            1300 - camera_x,
            350 - camera_y,
            350,
            1450
        )
    )

    # Start line
    start_x = 550 - camera_x
    start_y = 350 - camera_y

    for i in range(8):
        for j in range(2):

            color = WHITE if (i + j) % 2 == 0 else BLACK

            pygame.draw.rect(
                screen,
                color,
                (
                    start_x + i * 20,
                    start_y + j * 20,
                    20,
                    20
                )
            )


# --------------------------------------------------
# DECORATIONS
# --------------------------------------------------
trees = []

for _ in range(100):
    trees.append(
        (
            random.randint(50, WORLD_W - 50),
            random.randint(50, WORLD_H - 50)
        )
    )


def draw_trees(screen, camera_x, camera_y):

    for x, y in trees:

        sx = x - camera_x
        sy = y - camera_y

        if -50 < sx < WIDTH + 50 and -50 < sy < HEIGHT + 50:

            pygame.draw.circle(
                screen,
                (20, 80, 30),
                (int(sx), int(sy)),
                18
            )

            pygame.draw.circle(
                screen,
                (30, 130, 45),
                (int(sx - 5), int(sy - 5)),
                13
            )


# --------------------------------------------------
# GAME
# --------------------------------------------------

car = Car(600, 450)

font = pygame.font.SysFont("Arial", 28, bold=True)
big_font = pygame.font.SysFont("Arial", 42, bold=True)

running = True

while running:

    dt = clock.tick(60)

    for event in pygame.event.get():

        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False

    keys = pygame.key.get_pressed()

    car.update(keys)

    # Camera follows car
    camera_x = car.x - WIDTH / 2
    camera_y = car.y - HEIGHT / 2

    camera_x = max(
        0,
        min(WORLD_W - WIDTH, camera_x)
    )

    camera_y = max(
        0,
        min(WORLD_H - HEIGHT, camera_y)
    )

    draw_track(screen, camera_x, camera_y)
    draw_trees(screen, camera_x, camera_y)

    car.draw(screen, camera_x, camera_y)

    # --------------------------------------------------
    # HUD
    # --------------------------------------------------

    speed = math.hypot(car.vx, car.vy)

    kmh = int(speed * 15)

    speed_text = big_font.render(
        f"{kmh} KM/H",
        True,
        WHITE
    )

    screen.blit(
        speed_text,
        (WIDTH - 240, HEIGHT - 80)
    )

    controls = font.render(
        "WASD / Arrows = Drive    SPACE = Drift    ESC = Exit",
        True,
        WHITE
    )

    screen.blit(
        controls,
        (25, 25)
    )

    if keys[pygame.K_SPACE]:

        drift_text = big_font.render(
            "DRIFT!",
            True,
            YELLOW
        )

        screen.blit(
            drift_text,
            (WIDTH // 2 - 70, 50)
        )

    pygame.display.flip()

pygame.quit()
