
import pygame
import random
import math
from config import Config, DAY_THEME
from utils import create_soft_shadow, draw_rounded_rect

class GameObject:
    def __init__(self, x, y, width, height):
        self.rect = pygame.Rect(x, y, width, height)

    def draw(self, surface):
        pass

class Cloud(GameObject):
    def __init__(self, x, y, width, height, speed=0.5):
        super().__init__(x, y, width, height)
        self.speed = speed
        self.particles = []
        # Generate random cloud puffs
        num_puffs = 5
        for i in range(num_puffs):
            px = random.randint(0, int(width * 0.6))
            py = random.randint(0, int(height * 0.4))
            pr = random.randint(int(height * 0.4), int(height * 0.8))
            self.particles.append((px, py, pr))

    def update(self):
        self.rect.x += self.speed
        if self.rect.left > Config.width:
            self.rect.right = 0

    def draw(self, surface):
        # Draw soft cloud puffs
        for px, py, pr in self.particles:
            center = (self.rect.x + px, self.rect.y + py)
            # Draw multiple transparent layers for softness
            for r in range(pr, 0, -5):
                alpha = int(255 * (r / pr) * 0.2)
                color = (*DAY_THEME.cloud_white[:3], alpha)
                gfx_surface = pygame.Surface((r*2, r*2), pygame.SRCALPHA)
                pygame.draw.circle(gfx_surface, color, (r, r), r)
                surface.blit(gfx_surface, (center[0] - r, center[1] - r))

class Tree(GameObject):
    def __init__(self, x, y, width, height):
        super().__init__(x, y, width, height)

    def draw(self, surface):
        # Trunk
        trunk_w = self.rect.width * 0.3
        trunk_h = self.rect.height * 0.4
        trunk_x = self.rect.centerx - trunk_w // 2
        trunk_y = self.rect.bottom - trunk_h
        
        trunk_rect = pygame.Rect(trunk_x, trunk_y, trunk_w, trunk_h)
        pygame.draw.rect(surface, DAY_THEME.tree_trunk, trunk_rect)
        
        # Foliage (Stacked triangles/circles for style)
        foliage_color = DAY_THEME.tree_foliage_light
        shadow_color = DAY_THEME.tree_foliage_dark
        
        levels = 3
        level_height = (self.rect.height - trunk_h) * 1.2
        start_y = trunk_y
        
        for i in range(levels):
            # Draw from bottom up
            w = self.rect.width * (1 - i * 0.2)
            h = level_height / levels * 1.5
            cx = self.rect.centerx
            cy = start_y - (i * h * 0.6)
            
            # Simple soft triangle shape using circles/ellipses for "cute" look
            # Actually let's use a triangle with rounded corners vibe
            # but standard triangles are easier and classic "flat" style
            
            points = [
                (cx, cy - h),
                (cx - w/2, cy),
                (cx + w/2, cy)
            ]
            
            # Draw shadow side (right)
            shadow_points = [
                (cx, cy - h),
                (cx, cy),
                (cx + w/2, cy)
            ]
            pygame.draw.polygon(surface, shadow_color, shadow_points)
            
            # Draw light side (left)
            light_points = [
                (cx, cy - h),
                (cx - w/2, cy),
                (cx, cy)
            ]
            pygame.draw.polygon(surface, foliage_color, light_points)


class House(GameObject):
    def __init__(self, x, y, width, height):
        super().__init__(x, y, width, height)
        
    def draw(self, surface):
        # 1. Main Body
        body_h = self.rect.height * 0.6
        body_y = self.rect.bottom - body_h
        body_rect = pygame.Rect(self.rect.x, body_y, self.rect.width, body_h)
        
        # Soft shadow under the house
        shadow_surf = create_soft_shadow(self.rect.width, 20, (0,0,0,50), spread=15)
        surface.blit(shadow_surf, (self.rect.x - 15, self.rect.bottom - 10))

        pygame.draw.rect(surface, DAY_THEME.house_body, body_rect)
        
        # 2. Roof
        roof_h = self.rect.height * 0.5 # Overlap slightly
        roof_overhang = 30
        
        # Roof Shadow on House
        shadow_h = 10
        pygame.draw.rect(surface, (0,0,0,30), (self.rect.x, body_y, self.rect.width, shadow_h))

        # Roof Triangle
        roof_points = [
            (self.rect.centerx, self.rect.y),
            (self.rect.x - roof_overhang, body_y),
            (self.rect.right + roof_overhang, body_y)
        ]
        pygame.draw.polygon(surface, DAY_THEME.house_roof, roof_points)
        
        # 3. Door
        door_w = self.rect.width * 0.25
        door_h = body_h * 0.6
        door_x = self.rect.centerx - door_w // 2
        door_y = self.rect.bottom - door_h
        
        door_rect = pygame.Rect(door_x, door_y, door_w, door_h)
        # Door Frame/Trim
        pygame.draw.rect(surface, DAY_THEME.house_trim, door_rect.inflate(6, 0))
        # Door
        pygame.draw.rect(surface, DAY_THEME.house_door, door_rect)
        # Knob
        pygame.draw.circle(surface, (255, 215, 0), (door_rect.right - 10, door_rect.centery), 3)

        # 4. Window
        win_size = self.rect.width * 0.2
        win_x = self.rect.x + (self.rect.width * 0.15)
        win_y = body_y + (body_h * 0.2)
        
        win_rect = pygame.Rect(win_x, win_y, win_size, win_size)
        pygame.draw.rect(surface, DAY_THEME.house_trim, win_rect.inflate(4, 4))
        pygame.draw.rect(surface, (173, 216, 230), win_rect) # Glass
        
        # Window panes
        pygame.draw.line(surface, DAY_THEME.house_trim, win_rect.midtop, win_rect.midbottom, 2)
        pygame.draw.line(surface, DAY_THEME.house_trim, win_rect.midleft, win_rect.midright, 2)
        
        # Second Window (Right side)
        win_x2 = self.rect.right - (self.rect.width * 0.15) - win_size
        win_rect2 = pygame.Rect(win_x2, win_y, win_size, win_size)
        pygame.draw.rect(surface, DAY_THEME.house_trim, win_rect2.inflate(4, 4))
        pygame.draw.rect(surface, (173, 216, 230), win_rect2)
        pygame.draw.line(surface, DAY_THEME.house_trim, win_rect2.midtop, win_rect2.midbottom, 2)
        pygame.draw.line(surface, DAY_THEME.house_trim, win_rect2.midleft, win_rect2.midright, 2)
