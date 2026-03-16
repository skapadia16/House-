import pygame
import random
import math

# Initialize Pygame
pygame.init()

# ---------------- CONFIG ----------------
WIDTH, HEIGHT = 800, 600
FPS = 60

# 3D / Perspective Constants
FOV = 500
CAMERA_HEIGHT = 100
HORIZON_Y = HEIGHT // 2 - 20

# Road Config
ROAD_WIDTH_3D = 800
LANE_WIDTH = ROAD_WIDTH_3D // 4
SEGMENT_LENGTH = 100

# Gameplay Config
PLAYER_SPEED_MAX = 20
PLAYER_SPEED_ACCEL = 0.2
PLAYER_SPEED_DECEL = 0.5
OFF_ROAD_DECEL = 0.8
MAX_Z_VISIBLE = 3000

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (100, 100, 100)
DARK_GRAY = (50, 50, 50)
GREEN = (34, 139, 34)       # Grass
DARK_GREEN = (0, 100, 0)
SKY_BLUE = (135, 206, 235)
RED = (220, 20, 60)
BLUE = (60, 120, 220)
YELLOW = (255, 210, 0)

# Setup Display
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Realistic 3D Car Simulation")
clock = pygame.time.Clock()
font = pygame.font.SysFont("Arial", 20, bold=True)
large_font = pygame.font.SysFont("Arial", 40, bold=True)

# ---------------- HELPERS ----------------

def project_3d(x, y, z):
    if z <= 1: return 0, 0, 0
    scale = FOV / z
    sx = (WIDTH // 2) + (x * scale)
    sy = HORIZON_Y + (CAMERA_HEIGHT - y) * scale
    return int(sx), int(sy), scale

def draw_polygon(surface, color, points):
    pygame.draw.polygon(surface, color, points)

def draw_pseudo_3d_box(surface, color, x, z, w, h, d, y_offset=0):
    """
    Draws a simple 3D box at world x,z with width w, height h, depth d.
    y_offset lifts the object off the ground.
    """
    # Front Face
    # Bottom Left, Bottom Right, Top Right, Top Left
    fl = project_3d(x - w//2, y_offset, z)
    fr = project_3d(x + w//2, y_offset, z)
    br = project_3d(x + w//2, y_offset, z + d)
    bl = project_3d(x - w//2, y_offset, z + d)
    
    fl_t = project_3d(x - w//2, y_offset + h, z)
    fr_t = project_3d(x + w//2, y_offset + h, z)
    br_t = project_3d(x + w//2, y_offset + h, z + d)
    bl_t = project_3d(x - w//2, y_offset + h, z + d)
    
    if fl[2] <= 0: return # Behind camera
    
    # Draw Top Scale (Roof)
    draw_polygon(surface, color, [fl_t[:2], fr_t[:2], br_t[:2], bl_t[:2]])
    
    # Side (assuming we see right side if x > 0 or left if x < 0 relative to cam)
    # Actually just draw all sides back to front?
    # Simple painter: Top last.
    
    # Back Face (Darker)
    dark_c = [c//2 for c in color]
    draw_polygon(surface, dark_c, [bl[:2], br[:2], br_t[:2], bl_t[:2]])
    
    # Side Faces
    draw_polygon(surface, dark_c, [fl[:2], bl[:2], bl_t[:2], fl_t[:2]]) # Left
    draw_polygon(surface, dark_c, [fr[:2], br[:2], br_t[:2], fr_t[:2]]) # Right
    
    # Front Face (True Color)
    draw_polygon(surface, color, [fl[:2], fr[:2], fr_t[:2], fl_t[:2]])


# ---------------- CLASSES ----------------

class Car:
    def __init__(self, x=0, z=0, color=RED, is_player=False):
        self.x = x
        self.z = z
        self.color = color
        self.is_player = is_player
        
        self.width = 160
        self.height = 60
        self.depth = 250
        
        self.speed = 0
        self.lane = 0 # 0, 1, 2, 3?
        
    def update(self, dt):
        self.z += self.speed
        
    def draw(self, surface, relative_z=0):
        # relative_z is how far in front of camera the object is
        # For player, camera is behind. For traffic, relative to camera.
        
        # If player, we draw at fixed Z usually, or we move world around player.
        # Let's say Player is at z=300 relative to camera "lens"
        
        draw_z = self.z
        if self.is_player:
            draw_z = 300 # Fixed distance from camera
            
        final_z = draw_z
        if not self.is_player:
            # Traffic position relative to player (camera at player.z - 300)
            # relative_z passed in is (obj.z - camera.z)
            final_z = relative_z
            
        if final_z < 10: return
        
        sx, sy, scale = project_3d(self.x, 0, final_z)
        
        w = self.width * scale
        h = self.height * scale
        
        # Draw Car Body (Box)
        # Main Body
        rect = pygame.Rect(sx - w//2, sy - h, w, h)
        pygame.draw.rect(surface, self.color, rect)
        
        # Roof / Cabin (Smaller Box on Top)
        roof_w = w * 0.7
        roof_h = h * 0.6
        pygame.draw.rect(surface, [c + 20 if c < 235 else 255 for c in self.color], 
                         (sx - roof_w//2, sy - h - roof_h, roof_w, roof_h))
        
        # Windows
        pygame.draw.rect(surface, (200, 200, 255), 
                         (sx - roof_w//2 + 5, sy - h - roof_h + 5, roof_w - 10, roof_h - 10))

        # Wheels
        wheel_r = h * 0.4
        pygame.draw.circle(surface, BLACK, (int(sx - w*0.3), int(sy)), int(wheel_r))
        pygame.draw.circle(surface, BLACK, (int(sx + w*0.3), int(sy)), int(wheel_r))
        
        # Lights
        if self.is_player:
            # Tail lights
            pygame.draw.rect(surface, (255, 0, 0), (sx - w*0.4, sy - h*0.8, w*0.15, h*0.2))
            pygame.draw.rect(surface, (255, 0, 0), (sx + w*0.25, sy - h*0.8, w*0.15, h*0.2))
        else:
             # Just solid color simple
             pass

class PlayerCar(Car):
    def __init__(self):
        super().__init__(0, 0, RED, True)
        self.world_z = 0
        self.speed = 0
        self.steer_x = 0
        
    def control(self):
        keys = pygame.key.get_pressed()
        
        # Accelerate / Brake
        if keys[pygame.K_UP]:
            self.speed += PLAYER_SPEED_ACCEL
        elif keys[pygame.K_DOWN]:
            self.speed -= PLAYER_SPEED_DECEL
        else:
            self.speed *= 0.98 # Friction
            
        # Cap speed
        self.speed = max(0, min(self.speed, PLAYER_SPEED_MAX))
        
        # Steering
        if self.speed > 0.5:
            if keys[pygame.K_LEFT]:
                self.x -= 8 * (self.speed / PLAYER_SPEED_MAX) + 2
                self.steer_x = -1
            elif keys[pygame.K_RIGHT]:
                self.x += 8 * (self.speed / PLAYER_SPEED_MAX) + 2
                self.steer_x = 1
            else:
                self.steer_x = 0
        
        # Off-road slowdown
        if abs(self.x) > ROAD_WIDTH_3D // 2:
            self.speed *= OFF_ROAD_DECEL
            
        self.world_z += self.speed * 8 # World movement multiplier

# ---------------- MAIN ----------------

player = PlayerCar()
traffic = []

# Generate some traffic
for i in range(10):
    z_pos = 1000 + i * 800
    lane = random.choice([-1.5, -0.5, 0.5, 1.5])
    t_car = Car(lane * (ROAD_WIDTH_3D//4), z_pos, random.choice([BLUE, GREEN, YELLOW]))
    t_car.speed = random.uniform(5, 15)
    traffic.append(t_car)

# Background Trees
trees = []
for i in range(100):
    side = 1 if random.random() > 0.5 else -1
    x = (ROAD_WIDTH_3D//2 + random.randint(200, 1000)) * side
    z = random.randint(0, 10000)
    trees.append((x, z)) 


running = True
camera_z = 0

while running:
    # Event
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            
    # Update Player
    player.control()
    camera_z = player.world_z - 300 # Camera lags behind player
    
    # Update Traffic
    for t in traffic:
        t.z += t.speed
        # Recycle traffic
        if t.z < camera_z - 500:
            t.z = camera_z + MAX_Z_VISIBLE + random.randint(0, 1000)
            t.x = random.choice([-1.5, -0.5, 0.5, 1.5]) * (ROAD_WIDTH_3D//4)
            t.color = random.choice([BLUE, GREEN, YELLOW])
            
    # Update Trees
    # Just loop logic for infinite road?
    # Or just spawn new ones? Let's keep existing list but move ones that fall behind
    for i in range(len(trees)):
        tx, tz = trees[i]
        if tz < camera_z - 100:
            trees[i] = (tx, camera_z + MAX_Z_VISIBLE + random.randint(0, 500))

    # Draw
    screen.fill(SKY_BLUE)
    pygame.draw.rect(screen, GREEN, (0, HORIZON_Y, WIDTH, HEIGHT - HORIZON_Y))
    
    # Draw Road
    # Main Asphalt
    p1 = project_3d(-ROAD_WIDTH_3D//2, 0, 10) # Clip near
    p2 = project_3d(ROAD_WIDTH_3D//2, 0, 10)
    p3 = project_3d(ROAD_WIDTH_3D//2, 0, MAX_Z_VISIBLE)
    p4 = project_3d(-ROAD_WIDTH_3D//2, 0, MAX_Z_VISIBLE)
    pygame.draw.polygon(screen, GRAY, [p1[:2], p2[:2], p3[:2], p4[:2]])
    
    # Stripes
    # Calculate offset based on camera_z
    stripe_gap = SEGMENT_LENGTH * 2
    offset = camera_z % stripe_gap
    
    first_stripe_z = (camera_z // stripe_gap) * stripe_gap
    
    # Draw from camera_z to camera_z + max
    # We iterate relative positions
    for z in range(int(stripe_gap - offset), MAX_Z_VISIBLE, stripe_gap):
        # Center Line
        sp1 = project_3d(-5, 0, z)
        sp2 = project_3d(5, 0, z)
        sp3 = project_3d(5, 0, z + SEGMENT_LENGTH)
        sp4 = project_3d(-5, 0, z + SEGMENT_LENGTH)
        if sp1[2] > 0 and sp4[2] > 0:
             pygame.draw.polygon(screen, WHITE, [sp1[:2], sp2[:2], sp3[:2], sp4[:2]])
             
        # Lane Dividers?
        # Left Lane
        lp1 = project_3d(-ROAD_WIDTH_3D//4 - 2, 0, z)
        lp2 = project_3d(-ROAD_WIDTH_3D//4 + 2, 0, z)
        lp3 = project_3d(-ROAD_WIDTH_3D//4 + 2, 0, z + SEGMENT_LENGTH)
        lp4 = project_3d(-ROAD_WIDTH_3D//4 - 2, 0, z + SEGMENT_LENGTH)
        pygame.draw.polygon(screen, WHITE, [lp1[:2], lp2[:2], lp3[:2], lp4[:2]])
        
        # Right Lane
        rp1 = project_3d(ROAD_WIDTH_3D//4 - 2, 0, z)
        rp2 = project_3d(ROAD_WIDTH_3D//4 + 2, 0, z)
        rp3 = project_3d(ROAD_WIDTH_3D//4 + 2, 0, z + SEGMENT_LENGTH)
        rp4 = project_3d(ROAD_WIDTH_3D//4 - 2, 0, z + SEGMENT_LENGTH)
        pygame.draw.polygon(screen, WHITE, [rp1[:2], rp2[:2], rp3[:2], rp4[:2]])

    # Draw Objects (Painters)
    # Collect all drawables
    drawables = []
    
    # Traffic
    for t in traffic:
        rel_z = t.z - camera_z
        if rel_z > 10 and rel_z < MAX_Z_VISIBLE:
            drawables.append((rel_z, t))
            
    # Trees
    for tx, tz in trees:
        rel_z = tz - camera_z
        if rel_z > 10 and rel_z < MAX_Z_VISIBLE:
             drawables.append((rel_z, ("TREE", tx)))
             
    # Sort far to near
    drawables.sort(key=lambda x: x[0], reverse=True)
    
    for dist, obj in drawables:
        if isinstance(obj, Car):
            obj.draw(screen, dist)
        elif isinstance(obj, tuple) and obj[0] == "TREE":
            # Draw Tree
            tx = obj[1]
            sx, sy, scale = project_3d(tx, 0, dist)
            tr_w = 100 * scale
            tr_h = 150 * scale
            
            # Simple Tree
            pygame.draw.rect(screen, (139, 69, 19), (sx - tr_w//4, sy - tr_h, tr_w//2, tr_h))
            pygame.draw.circle(screen, DARK_GREEN, (int(sx), int(sy - tr_h*0.8)), int(tr_w))
            
    # Player Always Last (closest)
    player.draw(screen)
    
    # UI
    spd_txt = font.render(f"Speed: {int(player.speed * 10)} km/h", True, WHITE)
    screen.blit(spd_txt, (10, 10))
    
    dist_txt = font.render(f"Distance: {int(player.world_z / 100)} m", True, WHITE)
    screen.blit(dist_txt, (10, 35))

    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()
