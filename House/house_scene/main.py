
import pygame
import sys
from config import Config, DAY_THEME
from utils import draw_vertical_gradient
from objects import Cloud, Tree, House

def main():
    pygame.init()
    screen = pygame.display.set_mode((Config.width, Config.height))
    pygame.display.set_caption(Config.title)
    clock = pygame.time.Clock()

    # --- Scene Setup ---
    
    # Calculate ground level
    ground_y = int(Config.height * Config.horizon_ratio)
    
    # Create Objects
    house_w = int(Config.width * Config.house_scale)
    house_h = int(house_w * 0.75) # Aspect ratio
    house_x = (Config.width - house_w) // 2
    house_y = ground_y - house_h + 50 # Small overlap with ground for perspective
    
    house = House(house_x, house_y, house_w, house_h)
    
    trees = []
    # Background trees
    trees.append(Tree(house_x - 150, ground_y - 200, 120, 250))
    trees.append(Tree(house_x + house_w + 30, ground_y - 180, 100, 220))
    
    # Foreground trees (slightly larger/lower)
    trees.append(Tree(100, ground_y - 50, 180, 350))
    trees.append(Tree(Config.width - 250, ground_y - 30, 200, 380))
    
    clouds = []
    for i in range(5):
        cx = (i * 250) % Config.width
        cy = (i * 50) % 200
        clouds.append(Cloud(cx, cy, 200, 100, speed=0.2 + (i * 0.1)))

    # --- Main Loop ---
    running = True
    while running:
        # Event Handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # Update
        for cloud in clouds:
            cloud.update()

        # Render
        # 1. Sky Gradient
        draw_vertical_gradient(screen, pygame.Rect(0, 0, Config.width, ground_y), 
                             DAY_THEME.sky_top, DAY_THEME.sky_bottom)
        
        # 2. Sun (Soft glow)
        sun_pos = (Config.width - 150, 100)
        # Outer glow
        glow_surf = pygame.Surface((200, 200), pygame.SRCALPHA)
        pygame.draw.circle(glow_surf, (*DAY_THEME.sun_moon, 50), (100, 100), 80)
        pygame.draw.circle(glow_surf, (*DAY_THEME.sun_moon, 100), (100, 100), 60)
        screen.blit(glow_surf, (sun_pos[0]-100, sun_pos[1]-100))
        # Core
        pygame.draw.circle(screen, DAY_THEME.sun_moon, sun_pos, 40)

        # 3. Clouds (Behind house)
        for cloud in clouds:
            cloud.draw(screen)

        # 4. Ground Gradient
        draw_vertical_gradient(screen, pygame.Rect(0, ground_y, Config.width, Config.height - ground_y),
                             DAY_THEME.ground_top, DAY_THEME.ground_bottom)
        
        # 5. Background Trees
        # Sort trees by Y mostly, but we manually layered them in setup. 
        # Rendering background ones first is safer if we didn't sort.
        # Let's just draw them in order of creation for now since we added BG ones first.
        # Actually, let's sort purely by bottom Y to be correct for pseudo-3D
        all_objects = [house] + trees
        all_objects.sort(key=lambda o: o.rect.bottom)
        
        for obj in all_objects:
            obj.draw(screen)

        pygame.display.flip()
        clock.tick(Config.fps)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
