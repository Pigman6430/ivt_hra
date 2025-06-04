import pygame
import random
import math
from collections import deque

def _fade(t):
    return t * t * t * (t * (t * 6 - 15) + 10)

def _lerp(a, b, t):
    return a + t * (b - a)

_gradient_memo = {}
_local_random_instance = random.Random()

def _gradient_optimized(seed_param, x_param):
    x_int = math.floor(x_param)
    memo_key = (seed_param, x_int)
    if memo_key in _gradient_memo:
        return _gradient_memo[memo_key]

    temp_seed_for_choice = int(seed_param * 10000 + x_int * 7313) % 100000007
    _local_random_instance.seed(temp_seed_for_choice)
    result = _local_random_instance.choice([-1, 1])
    
    _gradient_memo[memo_key] = result
    return result

def _perlin_noise_single_octave(x, seed_for_octave):
    x0 = math.floor(x)
    x1 = x0 + 1
    t = x - x0

    g0 = _gradient_optimized(seed_for_octave, x0)
    g1 = _gradient_optimized(seed_for_octave, x1)

    n0 = g0 * t
    n1 = g1 * (t - 1)

    fade_t = _fade(t)
    return _lerp(n0, n1, fade_t)

def pnoise1d(sx, octaves, persistence, lacunarity, base_seed):
    total_noise = 0.0
    max_amplitude = 0.0
    amplitude = 1.0
    frequency = 1.0

    for i in range(octaves):
        noise_value = _perlin_noise_single_octave(sx * frequency, base_seed + i)
        total_noise += noise_value * amplitude
        max_amplitude += amplitude
        amplitude *= persistence
        frequency *= lacunarity

    if max_amplitude == 0:
        return 0.0
    return total_noise / max_amplitude

octaves_value = 8
persistence_value = 0.5
lacunarity_value = 2.0
seed_value = 7

screen_width = 800
screen_height = 600
terrain_width = screen_width
terrain_height_scale = screen_height * 0.6
scale = 230.0
speed = 200.0

heightmap = deque([0.0] * terrain_width, maxlen=terrain_width)
x_view_offset = 0
terrain_surface = pygame.Surface((terrain_width, screen_height))

def generate_initial_terrain():
    global x_view_offset
    x_view_offset = 0
    _gradient_memo.clear()

    for i in range(terrain_width):
        world_x = x_view_offset + i
        sx = world_x / scale
        noise_val = (pnoise1d(sx,
                              octaves=octaves_value,
                              persistence=persistence_value,
                              lacunarity=lacunarity_value,
                              base_seed=seed_value) + 1) / 2.0
        heightmap[i] = noise_val

def move_terrain_window(direction_steps):
    global x_view_offset
    
    if direction_steps == 0:
        return

    x_view_offset += direction_steps

    if direction_steps > 0:
        for _ in range(direction_steps):
            world_coord_for_new_val = x_view_offset + terrain_width - 1
            sx = world_coord_for_new_val / scale
            new_val = (pnoise1d(sx, octaves_value, persistence_value, lacunarity_value, seed_value) + 1) / 2.0
            heightmap.append(new_val)
    
    elif direction_steps < 0:
        new_values_to_add_left = []
        for i in range(abs(direction_steps)):
            world_coord_for_new_val = x_view_offset + i
            sx = world_coord_for_new_val / scale
            new_val = (pnoise1d(sx, octaves_value, persistence_value, lacunarity_value, seed_value) + 1) / 2.0
            new_values_to_add_left.append(new_val)
        
        for val in reversed(new_values_to_add_left):
            heightmap.appendleft(val)

def get_color(noise_val):
    if noise_val < 0.35: return (210, 180, 140)
    elif noise_val < 0.6: return (34, 139, 34)
    elif noise_val < 0.8: return (130, 130, 130)
    else: return (255, 255, 255)

def draw_terrain_on_surface(target_surf, current_heightmap_deque):
    SURF_H = target_surf.get_height()
    
    target_surf.fill((135, 206, 235))

    water_level_normalized = 0.3 
    y_water_surface_on_screen = math.floor((1 - water_level_normalized) * terrain_height_scale)

    for x_col, h_val_normalized in enumerate(current_heightmap_deque):
        y_ground_top_on_screen = math.floor(SURF_H - (h_val_normalized * terrain_height_scale))
        
        column_terrain_color = get_color(h_val_normalized)

        pygame.draw.line(target_surf, column_terrain_color,
                         (x_col, y_ground_top_on_screen), (x_col, SURF_H - 1))

        y_water_top_on_screen_fixed = math.floor(SURF_H - (water_level_normalized * terrain_height_scale))

        if y_water_top_on_screen_fixed < y_ground_top_on_screen :
            pygame.draw.line(target_surf, (0, 105, 148),
                             (x_col, y_water_top_on_screen_fixed), (x_col, y_ground_top_on_screen -1 ))

def main():
    pygame.init()
    screen = pygame.display.set_mode((screen_width, screen_height))
    pygame.display.set_caption("Optimized Perlin Terrain")
    clock = pygame.time.Clock()
    font = pygame.font.Font(None, 36)

    generate_initial_terrain()
    draw_terrain_on_surface(terrain_surface, heightmap)

    running = True
    terrain_needs_redraw = False

    global x_view_offset

    while running:
        dt = clock.tick(60) / 1000.0

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        
        keys = pygame.key.get_pressed()
        
        movement_amount_world_units = speed * dt
        num_steps_to_move = 0

        if keys[pygame.K_RIGHT]:
            num_steps_to_move = math.floor(movement_amount_world_units)
            if num_steps_to_move > 0:
                for _ in range(num_steps_to_move):
                    x_view_offset += 1
                    world_coord_for_new_val = x_view_offset + terrain_width - 1
                    sx = world_coord_for_new_val / scale
                    new_val = (pnoise1d(sx, octaves_value, persistence_value, lacunarity_value, seed_value) + 1) / 2.0
                    heightmap.append(new_val)
                terrain_needs_redraw = True
        
        if keys[pygame.K_LEFT]:
            num_steps_to_move = math.floor(movement_amount_world_units)
            if num_steps_to_move > 0:
                new_vals_buffer = []
                for i in range(num_steps_to_move):
                    current_new_column_world_offset = (x_view_offset - num_steps_to_move) + i
                    sx = current_new_column_world_offset / scale
                    new_val = (pnoise1d(sx, octaves_value, persistence_value, lacunarity_value, seed_value) + 1) / 2.0
                    new_vals_buffer.append(new_val)
                
                x_view_offset -= num_steps_to_move

                for val in reversed(new_vals_buffer):
                    heightmap.appendleft(val)
                terrain_needs_redraw = True
        
        if terrain_needs_redraw:
            draw_terrain_on_surface(terrain_surface, heightmap)
            terrain_needs_redraw = False

        screen.blit(terrain_surface, (0, 0))
        
        fps_val = clock.get_fps()
        fps_text_str = f"FPS: {fps_val:.0f}"
        fps_text_surface = font.render(fps_text_str, True, (255, 255, 0))
        screen.blit(fps_text_surface, (10, 10))
        
        pygame.display.flip()

    pygame.quit()

if __name__ == "__main__":
    main()