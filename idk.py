import pygame
import noise
import random
octaves_value = 6
persistence_value = 0.5
lacunarity_value = 2.0
seed_value = random.randint(1,1000)
terrain_height = 600
screen_width = 800
screen_height = 600
terrain_width = 800
scale = 100.0
heightmap = [[0.0 for x in range(terrain_width)] for y in range(terrain_height)]

for y in range(terrain_height):
    for x in range(terrain_width):
        sx = x/scale
        sy = y/scale
        heightmap[y][x] = (noise.pnoise2(sx, sy,
                        octaves=octaves_value,
                        persistence=persistence_value,
                        lacunarity=lacunarity_value,
                        base=seed_value)+1)/2.0
def get_color(noise_val):
    if noise_val < 0.2: return (0, 0, 128)    # Deep Water
    elif noise_val < 0.3: return (0, 0, 255)  # Shallow Water
    elif noise_val < 0.35: return (210, 180, 140) # Sand
    elif noise_val < 0.6: return (34, 139, 34) # Grass
    elif noise_val < 0.8: return (130, 130, 130) # Rock
    else: return (255, 255, 255)     
# print(noise.pnoise2(sx, sy,
#                         octaves=octaves_value,
#                         persistence=persistence_value,
#                         lacunarity=lacunarity_value,
#                         base=seed_value))
terrain = pygame.Surface((terrain_width,terrain_height))
def main():
    pygame.init()

    screen_size = (screen_width, screen_height)
    screen = pygame.display.set_mode(screen_size)

    pygame.display.set_caption("Pygame Window")
    for y in range(terrain_height):
        for x in range(terrain_width):
            color = get_color(heightmap[y][x])
            terrain.set_at((x, y), color)

    running = True

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False


        screen.fill((0,0,0))
        screen.blit(terrain, (0, 0))
        pygame.display.flip()

        pygame.time.Clock().tick(60)

    pygame.quit()

if __name__ == "__main__":
    main()
