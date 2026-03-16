import pygame
import math
import random

# Initialize Pygame
pygame.init()

# ---------------- CONFIG ----------------
WIDTH, HEIGHT = 800, 600
FPS = 60

# 3D Config
FOV = 400
CAMERA_HEIGHT = 200
HORIZON_Y = HEIGHT // 2 - 50

# Water Config
GRID_SIZE = 100        # Distance between grid points
GRID_COLS = 20         # Number of columns (WIDTH / GRID_SIZE + buffer)
GRID_ROWS = 40         # Number of rows (depth)
WAVE_HEIGHT = 30
WAVE_SPEED = 0.05

# Colors
SKY_DAY = (135, 206, 235)
SKY_NIGHT = (25, 25, 112)
WATER_BASE = (0, 105, 148)
WATER_HIGHLIGHT = (0, 150, 200)
FOAM = (240, 248, 255)
BROWN = (139, 69, 19)
WHITE = (255, 255, 255)
SUN_YELLOW = (255, 255, 0)
MOON_WHITE = (240, 240, 255)

# Setup Display
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("3D Sea Sailing")
clock = pygame.time.Clock()
font = pygame.font.SysFont("Arial", 20, bold=True)

# ---------------- HELPERS ----------------

def project_3d(x, y, z):
    if z <= 1: return 0, 0, 0
    scale = FOV / z
    sx = (WIDTH // 2) + (x * scale)
    sy = HORIZON_Y + (CAMERA_HEIGHT - y) * scale
    return int(sx), int(sy), scale

# ---------------- OBJECTS ----------------

class Sea:
    def __init__(self):
        self.time = 0
        self.polys = []
        
    def update(self):
        self.time += WAVE_SPEED
        # We don't store polys, we generate them every frame for the grid
        
    def get_wave_y(self, x, z):
        # Generate Y based on simple sine waves
        # Combine a few waves for irregularity
        y = math.sin(x * 0.01 + self.time) * WAVE_HEIGHT * 0.5
        y += math.sin(z * 0.015 + self.time * 0.8) * WAVE_HEIGHT * 0.5
        # Add some "chop"
        y += math.sin((x+z) * 0.05 + self.time * 2) * WAVE_HEIGHT * 0.2
        return y

    def draw(self, surface, camera_z):
        # Draw grid from back to front? Or just front to back with painters?
        # Actually back to front is safer for painters if no Z-buffer.
        
        # We need to render points relative to camera_z
        # Grid moves with camera_z but snaps to grid size to look infinite?
        
        # Snap camera to grid
        start_z = (int(camera_z) // GRID_SIZE) * GRID_SIZE
        z_offset = camera_z % GRID_SIZE
        
        # We want to draw rows from far (high Z) to near (low Z)
        # Max visibility
        max_row = 30
        
        # Generate points first?
        # Optimization: Strip primitive
        
        # Let's iterate rows from far to near
        for r in range(max_row, 0, -1):
            z_far = start_z + r * GRID_SIZE
            z_near = start_z + (r - 1) * GRID_SIZE
            
            # Relative Z for projection
            rz_far = z_far - camera_z
            rz_near = z_near - camera_z
            
            if rz_near < 1: continue
            
            # Points for strip
            points_far = []
            points_near = []
            
            # Cols centered around 0
            for c in range(-GRID_COLS//2, GRID_COLS//2 + 1):
                gx = c * GRID_SIZE
                
                # Far Point
                gy_far = self.get_wave_y(gx, z_far)
                p_far = project_3d(gx, gy_far, rz_far)
                points_far.append(p_far)
                
                # Near Point
                gy_near = self.get_wave_y(gx, z_near)
                p_near = project_3d(gx, gy_near, rz_near)
                points_near.append(p_near)
                
            # Draw Quads
            for i in range(len(points_far) - 1):
                p1 = points_far[i]
                p2 = points_far[i+1]
                p3 = points_near[i+1]
                p4 = points_near[i]
                
                # Check bounds
                if p1[2] <= 0 or p4[2] <= 0: continue
                
                # Color based on height? or checkerboard?
                # Let's do simple water color with slight lighting
                # Lighting: wave slope?
                # Simple: alternatve slightly
                col = WATER_BASE
                if (r + i) % 2 == 0:
                     col = WATER_HIGHLIGHT
                     
                pygame.draw.polygon(surface, col, [p1[:2], p2[:2], p3[:2], p4[:2]])
                # Wireframe or foam?
                # pygame.draw.lines(surface, FOAM, True, [p1[:2], p2[:2], p3[:2], p4[:2]], 1)


class Boat:
    def __init__(self):
        self.x = 0
        self.z = 0
        self.speed = 0
        self.angle_y = 0 # Rotation / Tilt
        
    def update(self, sea):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_UP]:
            self.speed += 0.1
        elif keys[pygame.K_DOWN]:
            self.speed -= 0.05
        else:
             self.speed *= 0.98
             
        self.speed = max(0, min(self.speed, 10))
        
        if self.speed > 0.1:
            if keys[pygame.K_LEFT]:
                self.x -= 2
            elif keys[pygame.K_RIGHT]:
                self.x += 2
                
        self.z += self.speed * 5
        
        # Calculate Tilt based on waves
        # Sample points around boat
        y_center = sea.get_wave_y(self.x, self.z)
        y_left = sea.get_wave_y(self.x - 20, self.z)
        y_right = sea.get_wave_y(self.x + 20, self.z)
        y_front = sea.get_wave_y(self.x, self.z + 20)
        y_back = sea.get_wave_y(self.x, self.z - 20)
        
        self.y = y_center
        # Roll (Left/Right tilt)
        self.roll = (y_left - y_right) * 0.5
        # Pitch (Front/Back tilt)
        self.pitch = (y_back - y_front) * 0.5

    def draw(self, surface):
        # Draw boat slightly "in front" of camera (fixed position on screen mostly)
        # But we want to see it bobbing
        
        # Screen Pos fixed X, Y depends on wave
        sx = WIDTH // 2
        sy = HEIGHT - 100 - (self.y * 1) # Visualize wave height
        
        # Simple Boat Shape
        # Hull
        hull_w = 120
        hull_h = 40
        
        # Apply roll
        # Rotate rectangle points?
        # Simple: draw primitive relative to center
        
        boat_surf = pygame.Surface((200, 200), pygame.SRCALPHA)
        # Center of surf is 100, 100
        
        # Hull
        pygame.draw.polygon(boat_surf, BROWN, [(40, 120), (160, 120), (140, 160), (60, 160)])
        # Mast
        pygame.draw.rect(boat_surf, BROWN, (95, 40, 10, 80))
        # Sail
        pygame.draw.polygon(boat_surf, WHITE, [(105, 45), (155, 100), (105, 100)])
        
        # Rotate
        rot_boat = pygame.transform.rotate(boat_surf, self.roll)
        rect = rot_boat.get_rect(center=(sx, sy))
        surface.blit(rot_boat, rect)


class Obstacle:
    def __init__(self, x, z, type="ROCK"):
        self.x = x
        self.z = z
        self.type = type
        
    def draw(self, surface, camera_z):
        rz = self.z - camera_z
        if rz < 10: return
        
        sx, sy, scale = project_3d(self.x, 0, rz)
        
        w = 100 * scale
        h = 100 * scale
        
        if self.type == "ROCK":
            pygame.draw.circle(surface, (100, 100, 100), (int(sx), int(sy)), int(w//2))
        elif self.type == "ISLAND":
             pygame.draw.ellipse(surface, (210, 180, 140), (sx - w, sy - h//4, w*2, h//2))
             # Palm tree?
             pygame.draw.rect(surface, BROWN, (sx - 5*scale, sy - h, 10*scale, h))
             pygame.draw.circle(surface, (0, 100, 0), (int(sx), int(sy - h)), int(w//2))

# ---------------- MAIN ----------------

sea = Sea()
boat = Boat()
obstacles = []

# Generate obstacles
for i in range(20):
    z = 1000 + i * 500
    x = random.randint(-500, 500)
    t = "ROCK" if random.random() < 0.7 else "ISLAND"
    obstacles.append(Obstacle(x, z, t))

running = True
day_time = 0

while running:
    # Event
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            
    # Update
    sea.update()
    boat.update(sea)
    
    # Recycle obstacles
    for o in obstacles:
        if o.z < boat.z - 100:
            o.z = boat.z + 5000 + random.randint(0, 1000)
            o.x = boat.x + random.randint(-800, 800) # Relative to boat X
            
    # Day/Night Cycle
    day_time += 0.05
    intensity = (math.sin(day_time * 0.01) + 1) / 2 # 0 to 1
    # Interpolate Sky Color
    curr_sky = (
        int(SKY_NIGHT[0] + (SKY_DAY[0]-SKY_NIGHT[0])*intensity),
        int(SKY_NIGHT[1] + (SKY_DAY[1]-SKY_NIGHT[1])*intensity),
        int(SKY_NIGHT[2] + (SKY_DAY[2]-SKY_NIGHT[2])*intensity)
    )
    
    # Draw
    screen.fill(curr_sky)
    
    # Sun / Moon
    sun_x = WIDTH//2 + math.sin(day_time*0.01)*400
    sun_y = HORIZON_Y - math.cos(day_time*0.01)*200
    if sun_y < HEIGHT:
        color = SUN_YELLOW if intensity > 0.2 else MOON_WHITE
        pygame.draw.circle(screen, color, (int(sun_x), int(sun_y)), 40)
    
    # Sea
    sea.draw(screen, boat.z)
    
    # Obstacles
    # Sort
    obstacles.sort(key=lambda o: o.z, reverse=True)
    for o in obstacles:
        if o.z > boat.z + 10:
             # Fix Y based on wave at that point?
             # For simplicity, render at y=0 (water level)
             # To make them bob, we'd need to update their Y logic
             o.draw(screen, boat.z)
             
    # Boat
    boat.draw(screen)
    
    # UI
    info = font.render(f"Speed: {int(boat.speed)} | Distance: {int(boat.z)}", True, WHITE)
    screen.blit(info, (10, 10))
    
    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()
