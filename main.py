import pygame
import noise
import random
octaves_value = 8
persistence_value = 0.6
lacunarity_value = 1.7
seed_value = 7#random.randint(1,1000)
terrain_height = 600
screen_width = 800
screen_height = 600
terrain_width = 800
scale = 200.0
heightmap = [0.0 for x in range(terrain_width)]

for x in range(terrain_width):
    sx = x/scale
    heightmap[x] = (noise.pnoise1(sx,
                    octaves=octaves_value,
                    persistence=persistence_value,
                    lacunarity=lacunarity_value,
                    base=seed_value)+1)/2.0
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
print(heightmap)
def main():
    pygame.init()

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


        screen.fill((0,0,0))
        screen.blit(terrain, (0, 0))
        pygame.display.flip()

        pygame.time.Clock().tick(60)

    pygame.quit()

if __name__ == "__main__":
    main()
