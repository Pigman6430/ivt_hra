import pygame
import random
import math
import plane

plane = plane.Plane()

seed_value = 3
octaves_value = 5
persistence_value = 0.6
lacunarity_value = 1.5
amplitude = 1.6
scale = 4000.0

random.seed(seed_value)
p = list(range(256))
random.shuffle(p)
p += p

def _fade(t):
    return t * t * t * (t * (t * 6 - 15) + 10)

def _lerp(a, b, t):
    return a + t * (b - a)

def _gradient(seed, x):
    x_int = int(x) & 255
    hash_value = p[(x_int + seed) & 255]
    return 1 if hash_value % 2 == 0 else -1

def _perlin_noise_single_octave(x, seed):
    x0 = math.floor(x)
    x1 = x0 + 1
    t = x - x0
    g0 = _gradient(seed, x0)
    g1 = _gradient(seed, x1)
    n0 = g0 * t
    n1 = g1 * (t - 1)
    fade_t = _fade(t)
    return _lerp(n0, n1, fade_t)

def pnoise1d(sx, octaves, persistence, lacunarity, base):
    total_noise = 0.0
    max_amplitude = 0.0
    amplitude = 1.0
    frequency = 1.0
    for i in range(octaves):
        noise_value = _perlin_noise_single_octave(sx * frequency, base + i)
        total_noise += noise_value * amplitude
        max_amplitude += amplitude
        amplitude *= persistence
        frequency *= lacunarity
    if max_amplitude == 0:
        return 0.0
    return total_noise / max_amplitude

terrain_height = 800
screen_width = 1500
screen_height = 800
terrain_width = 1500
surface_depth = 20
dirt = (88, 57, 39)
terrain_cache = {}

clock = pygame.time.Clock()

def get_color(noise_val):
    if noise_val < 0.35: return (210, 180, 140)
    elif noise_val < 0.6: return (34, 139, 34)
    elif noise_val < 0.8: return (130, 130, 130)
    else: return (255, 255, 255)

def get_lower_color(noise_val):
    if noise_val < 0.3: return (0,0,255)
    elif noise_val < 0.6: return (210, 180, 140)
    elif noise_val < 0.8: return (34, 139, 34)
    else: return (130, 130, 130)

def stop_value(noise_val):
    if noise_val < 0.30: return 0.0
    elif noise_val < 0.35: return 0.30
    elif noise_val < 0.6: return 0.35
    elif noise_val < 0.8: return 0.6
    else: return 0.8

def get_terrain_height_at(world_x):
    if world_x in terrain_cache:
        height_normalized = terrain_cache[world_x]
    else:
        sx = world_x / scale
        height_normalized = (pnoise1d(sx, octaves=octaves_value,
                                      persistence=persistence_value,
                                      lacunarity=lacunarity_value,
                                      base=seed_value) * amplitude + 1) / 2.0
        terrain_cache[world_x] = height_normalized
    world_y = (1 - height_normalized) * terrain_height
    return world_y

camera = pygame.Rect(0, 0, screen_width, screen_height)
all_sprites = pygame.sprite.Group()
all_sprites.add(plane)

def main():
    pygame.init()
    font = pygame.font.Font(None, 36)
    screen_size = (screen_width, screen_height)
    screen = pygame.display.set_mode(screen_size)
    pygame.display.set_caption("Pygame Flight Sim")
    running = True

    while running:
        dt = clock.tick(60) / 1000
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        
        keys = pygame.key.get_pressed()
        
        if plane.state != 'crashed':
            if keys[pygame.K_w] or keys[pygame.K_UP]:
                plane.throttle = min(1.0, plane.throttle + 0.5 * dt)
            elif keys[pygame.K_s] or keys[pygame.K_DOWN]:
                plane.throttle = max(0.0, plane.throttle - 0.5 * dt)

        if plane.state == 'flying':
            PITCH_RATE = 40.0
            if keys[pygame.K_a] or keys[pygame.K_LEFT]:
                plane.angle += PITCH_RATE * dt
            elif keys[pygame.K_d] or keys[pygame.K_RIGHT]:
                plane.angle -= PITCH_RATE * dt
        elif plane.state == "crashed":
            if keys[pygame.K_r]:
                plane.pos = pygame.math.Vector2(800, 600)
                plane.velocity = pygame.math.Vector2(0, 0)
                plane.angle = 0.0
                plane.throttle = 0.0
                plane.state = 'grounded'
                plane.angle_of_attack = 0.0
        
        if plane.state != 'crashed':
            plane.angle = max(-20, min(20, plane.angle))
        
        if plane.state == 'grounded':
            PITCH_RATE_GROUND = 20.0
            if keys[pygame.K_a] or keys[pygame.K_LEFT]:
                plane.angle += PITCH_RATE_GROUND * dt
            plane.angle = min(plane.angle, 20)
            if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
                plane.angle -= PITCH_RATE_GROUND * dt
                plane.angle = max(plane.angle, -5)
            if keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]:
                plane.velocity.x -= plane.BRAKE_POWER * dt
                plane.velocity.x = max(plane.velocity.x, -20)

        screen.fill((135, 206, 235))
        
        for screen_x in range(screen_width):
            world_x = screen_x + int(camera.x)
            height_normalized = 0.0
            
            if world_x in terrain_cache:
                height_normalized = terrain_cache[world_x]
            else:
                sx = world_x / scale
                height_normalized = (pnoise1d(sx,
                                              octaves=octaves_value,
                                              persistence=persistence_value,
                                              lacunarity=lacunarity_value,
                                              base=seed_value) * amplitude + 1) / 2.0
                terrain_cache[world_x] = height_normalized

            world_y_surface = (1 - height_normalized) * terrain_height
            world_y_surface_bottom = world_y_surface + surface_depth
            world_y_water_level = (1 - 0.3) * terrain_height
            world_y_stop_level = (1 - stop_value(height_normalized)) * terrain_height
            
            screen_y_surface = world_y_surface - camera.y
            screen_y_surface_bottom = world_y_surface_bottom - camera.y
            screen_y_water_level = world_y_water_level - camera.y
            screen_y_stop_level = world_y_stop_level - camera.y

            pygame.draw.line(screen, get_color(height_normalized), (screen_x, screen_y_surface), (screen_x, min(screen_y_surface_bottom, screen_y_stop_level)))
            if screen_y_stop_level < screen_y_surface_bottom:
                pygame.draw.line(screen, get_lower_color(height_normalized), (screen_x, screen_y_stop_level), (screen_x, screen_y_surface_bottom))
            elif height_normalized < 0.3:
                pygame.draw.line(screen, (0, 0, 255), (screen_x, screen_y_water_level), (screen_x, screen_y_surface))
            
            pygame.draw.line(screen, dirt, (screen_x, screen_y_surface_bottom), (screen_x, screen_height))

        plane.update(dt, get_terrain_height_at)

        camera.x = plane.pos.x - screen_width / 2
        camera.y = plane.pos.y - screen_height / 2
        
        for sprite in all_sprites:
            screen_pos_x = sprite.pos.x - camera.x - 80
            screen_pos_y = sprite.pos.y - camera.y - 25
            screen.blit(sprite.image, (screen_pos_x, screen_pos_y))
        
        fps = str(int(clock.get_fps()))
        fps_text = font.render("FPS: " + fps, True, (255, 255, 0))
        screen.blit(fps_text, (10, 10))
        
        throttle_text = font.render(f"Throttle: {plane.throttle:.0%}", True, (255, 255, 0))
        velocity_text = font.render(f"Velocity: {plane.velocity.length():.0f}", True, (255, 255, 0))
        pos_text = font.render(f"Pos: {plane.pos.x:.0f} x {plane.pos.y:.0f} y", True, (255, 255, 0))
        
        

        screen.blit(throttle_text, (10, 70))
        screen.blit(velocity_text, (10, 100))
        screen.blit(pos_text, (10, 160))
        
        if plane.state == 'crashed':
            crash_font = pygame.font.Font(None, 100)
            crash_text = crash_font.render("CRASHED! R to restart", True, (255, 0, 0))
            text_rect = crash_text.get_rect(center=(screen_width/2, screen_height/2))
            screen.blit(crash_text, text_rect)
            
        pygame.display.flip()

    pygame.quit()

if __name__ == "__main__":
    main()