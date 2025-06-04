import pygame
import random
import math

import math
# LOW FPS
def _fade(t):
    return t * t * t * (t * (t * 6 - 15) + 10)

def _lerp(a, b, t):
    return a + t * (b - a)

def _gradient(seed, x):
    temp_seed = int(seed * 1000 + x * 731) % 1000000
    random.seed(temp_seed)
    return random.choice([-1, 1])

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
octaves_value = 8
persistence_value = 0.6
lacunarity_value = 1.7
seed_value = 7#random.randint(1,1000)
terrain_height = 600
screen_width = 800
screen_height = 600
terrain_width = 800
scale = 230.0
speed = 50

clock = pygame.time.Clock()
heightmap = [0.0 for x in range(terrain_width)]
def Generate_terrain():
    for x in range(terrain_width):
        sx = x/scale
        heightmap[x] = (pnoise1d(sx,
                        octaves=octaves_value,
                        persistence=persistence_value,
                        lacunarity=lacunarity_value,
                        base=seed_value)+1)/2.0

def Move(direction,x_coord):
    if direction == 1:
        heightmap.append(0.0)
        sx = x_coord/scale
        heightmap[-1] = (pnoise1d(sx,
                        octaves=octaves_value,
                        persistence=persistence_value,
                        lacunarity=lacunarity_value,
                        base=seed_value)+1)/2.0
        heightmap.pop(0)
    if direction == -1:
        heightmap.insert(0,0.0)
        sx = (x_coord-terrain_width)/scale
        heightmap[0] = (pnoise1d(sx,
                        octaves=octaves_value,
                        persistence=persistence_value,
                        lacunarity=lacunarity_value,
                        base=seed_value)+1)/2.0
        heightmap.pop(-1)
        
def get_color(noise_val):      
    if noise_val < 0.35: return (210, 180, 140) # Sand
    elif noise_val < 0.6: return (34, 139, 34) # Grass
    elif noise_val < 0.8: return (130, 130, 130) # Rock
    else: return (255, 255, 255) 
def get_elevation(noise):
    return noise*terrain_height    
# print(noise.pnoise2(sx, sy,
#                         octaves=octaves_value,
#                         persistence=persistence_value,
#                         lacunarity=lacunarity_value,
#                         base=seed_value))
terrain = pygame.Surface((terrain_width,terrain_height))
#print(heightmap)
def main():

    x_coord = 800
    pygame.init()
    font = pygame.font.Font(None, 36) # Default font, size 36
    Generate_terrain()
    screen_size = (screen_width, screen_height)
    screen = pygame.display.set_mode(screen_size)

    pygame.display.set_caption("Pygame Window")
    for x in range(terrain_width):
        color = get_color(heightmap[x])
        for y in range(terrain_height):
            if y < (1-heightmap[x])*terrain_height:
                terrain.set_at((x,y), (0,0,0))
                if y > (1-0.3)*terrain_height:
                    terrain.set_at((x,y), (0,0,255))
            else:
                terrain.set_at((x,y), color)

    running = True

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        keys = pygame.key.get_pressed()
        if keys[pygame.K_RIGHT]:
            print(x_coord)
            for i in range(math.floor(speed*dt)):
                x_coord += 1
                Move(1,x_coord)
        if keys[pygame.K_LEFT]:
            print(x_coord)
            for i in range(math.floor(speed*dt)):
                x_coord -= 1
                Move(-1,x_coord)
        for x in range(terrain_width):
            color = get_color(heightmap[x])
            for y in range(terrain_height):
                if y < (1-heightmap[x])*terrain_height:
                    terrain.set_at((x,y), (0,0,0))
                    if y > (1-0.3)*terrain_height:
                        terrain.set_at((x,y), (0,0,255))
                else:
                    terrain.set_at((x,y), color)

        screen.fill((0,0,0))
        screen.blit(terrain, (0, 0))
        fps = str(int(clock.get_fps())) # Get FPS, convert to int, then to string
        fps_text = font.render("FPS: " + fps, True, (255, 255, 0)) # Render text (text, antialias, color)
        screen.blit(fps_text, (10, 10)) # Blit the text to the screen at (10, 10)
        pygame.display.flip()

        dt = clock.tick(60)/1000

    pygame.quit()

if __name__ == "__main__":
    main()
