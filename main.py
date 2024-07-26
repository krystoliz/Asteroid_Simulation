import pygame
import math
import random

pygame.init()
WIDTH, HEIGHT = 1000, 1000  # Increased size for better visualization
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Asteroid Belt Dynamics with Stochastic Perturbations")

WHITE = (255, 255, 255)
YELLOW = (255, 255, 0)
BLUE = (100, 149, 237)
GREY = (169, 169, 169)

FONT = pygame.font.SysFont("comicsans", 16)

class Body:
    G = 6.67428e-11
    SCALE = 50 / 1.496e11  # 1 AU = 50 pixels (adjusted from 250)
    TIMESTEP = 3600 * 24 * 3.61  # 3.61 days per frame

    def __init__(self, x, y, radius, color, mass):
        self.x = x
        self.y = y
        self.radius = radius
        self.color = color
        self.mass = mass
        self.orbit = []
        self.x_vel = 0
        self.y_vel = 0

    def draw(self, win):
        x = self.x * self.SCALE + WIDTH / 2
        y = self.y * self.SCALE + HEIGHT / 2

        if len(self.orbit) > 2:
            updated_points = []
            for point in self.orbit:
                x, y = point
                x = x * self.SCALE + WIDTH / 2
                y = y * self.SCALE + HEIGHT / 2
                updated_points.append((x, y))

            pygame.draw.lines(win, self.color, False, updated_points, 2)
        pygame.draw.circle(win, self.color, (x, y), self.radius)

    def attraction(self, other):
        other_x, other_y = other.x, other.y
        distance_x = other_x - self.x
        distance_y = other_y - self.y
        distance = math.sqrt(distance_x**2 + distance_y**2)

        force = self.G * self.mass * other.mass / distance**2
        theta = math.atan2(distance_y, distance_x)
        force_x = math.cos(theta) * force
        force_y = math.sin(theta) * force
        return force_x, force_y

    def update_position(self, bodies):
        total_fx = total_fy = 0
        for body in bodies:
            if self == body:
                continue

            fx, fy = self.attraction(body)
            total_fx += fx
            total_fy += fy

        self.x_vel += total_fx / self.mass * self.TIMESTEP
        self.y_vel += total_fy / self.mass * self.TIMESTEP

        self.x += self.x_vel * self.TIMESTEP
        self.y += self.y_vel * self.TIMESTEP
        self.orbit.append((self.x, self.y))

def apply_stochastic_perturbations(asteroids):
    for asteroid in asteroids:
        if random.random() < 0.8:  # 10% chance of perturbation each timestep
            delta_vx = random.uniform(-100, 100)  # small random velocity change
            delta_vy = random.uniform(-100, 100)
            asteroid.x_vel += delta_vx
            asteroid.y_vel += delta_vy

def count_out_of_belt_asteroids(asteroids):
    count = 0
    for asteroid in asteroids:
        distance = math.sqrt(asteroid.x**2 + asteroid.y**2)
        if distance < 2.0 * 1.496e11 or distance > 3.5 * 1.496e11:
            count += 1
    return count

def get_top_farthest_asteroids(asteroids, top_n=5):
    distances = []
    for asteroid in asteroids:
        distance = math.sqrt(asteroid.x**2 + asteroid.y**2)
        distances.append(distance)
    distances.sort(reverse=True)
    return distances[:top_n]

def draw_info_box(win, num_out_of_belt, top_distances, years_elapsed):
    info_text = FONT.render(f"Asteroids out of belt: {num_out_of_belt}", 1, WHITE)
    win.blit(info_text, (10, 10))

    time_text = FONT.render(f"Time elapsed: {years_elapsed:.2f} years", 1, WHITE)
    win.blit(time_text, (10, 30))

    y_offset = 50
    for i, distance in enumerate(top_distances):
        distance_text = FONT.render(f"Top {i+1} distance: {distance / 1.496e11:.2f} AU", 1, WHITE)
        win.blit(distance_text, (10, y_offset))
        y_offset += 20

def main():
    run = True
    clock = pygame.time.Clock()

    sun = Body(0, 0, 30, YELLOW, 1.98892e30)
    sun.x_vel = 0
    sun.y_vel = 0

    jupiter = Body(5.2 * 1.496e11, 0, 18, BLUE, 1.898e27)
    jupiter.y_vel = 13070

    asteroids = []
    for _ in range(300):  # Create 100 asteroids in the asteroid belt
        dist = random.uniform(2.0 * 1.496e11, 3.5 * 1.496e11)
        angle = random.uniform(0, 2 * math.pi)
        x = dist * math.cos(angle)
        y = dist * math.sin(angle)
        mass = random.uniform(1e15, 1e20)
        asteroid = Body(x, y, 4, GREY, mass)
        speed = math.sqrt(Body.G * sun.mass / dist)
        asteroid.x_vel = -speed * math.sin(angle)
        asteroid.y_vel = speed * math.cos(angle)
        asteroids.append(asteroid)

    bodies = [sun, jupiter] + asteroids

    days_elapsed = 0

    while run:
        clock.tick(240)  # Increased FPS for faster simulation
        WIN.fill((0, 0, 0))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

        apply_stochastic_perturbations(asteroids)

        for body in bodies:
            body.update_position(bodies)
            body.draw(WIN)

        num_out_of_belt = count_out_of_belt_asteroids(asteroids)
        top_distances = get_top_farthest_asteroids(asteroids)

        years_elapsed = days_elapsed / 365.25
        draw_info_box(WIN, num_out_of_belt, top_distances, years_elapsed)

        days_elapsed += 3.61  # Increment by the number of days per frame

        pygame.display.update()

    pygame.quit()

main()
