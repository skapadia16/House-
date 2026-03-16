import pygame
import random
import math

# Initialize Pygame
pygame.init()

# ---------------- CONFIG ----------------
WIDTH, HEIGHT = 800, 600
FPS = 60

# 3D / Perspective Constants
FOV = 500              # Field of View
CAMERA_HEIGHT = 150    # How high the camera is off the ground
CAMERA_DIST = 400      # Distance from camera to screen plane (affects scaling)
HORIZON_Y = HEIGHT // 2 - 50 # Where the sky meets the ground

# Road Config
ROAD_WIDTH_3D = 600    # Width of road in world units at z=0
SEGMENT_LENGTH = 100   # Length of road segments for striping

# Gameplay Config
SCROLL_SPEED = 5
TOTAL_DISTANCE = 10000 # Distance to reach home
HOME_Z_TRIGGER = 50    # When home is close enough to end game

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (100, 100, 100)
DARK_GRAY = (50, 50, 50)
GREEN = (34, 139, 34)       # Grass
DARK_GREEN = (0, 100, 0)
BLUE = (65, 105, 225)       # College / Sky
SKY_BLUE = (135, 206, 235)
RED = (220, 20, 60)         # Market
PURPLE = (147, 112, 219)    # Shopping Center
SKIN = (255, 224, 189)
CLOTHES = (0, 0, 128)
YELLOW = (255, 215, 0)
BROWN = (139, 69, 19)


# Setup Display
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Boy Walk Simulation 3D")
clock = pygame.time.Clock()
font = pygame.font.SysFont("Arial", 20, bold=True)
large_font = pygame.font.SysFont("Arial", 40, bold=True)

# ---------------- HELPERS ----------------

def project_3d(x, y, z):
    """
    Project world (x, y, z) coordinates to screen (sx, sy) and return scale factor.
    World system:
    x: 0 is center, -ve left, +ve right
    y: 0 is ground, +ve up
    z: distance from camera, +ve is forward (into screen)
    """
    if z <= 1: 
        return 0, 0, 0 # Behind or at camera
        
    scale = FOV / (z)
    
    # Project X: 0 is center of screen
    sx = (WIDTH // 2) + (x * scale)
    
    # Project Y: 0 is HORIZON_Y, y grows UP in world but DOWN in pygame screen 
    # (relative to horizon) logic needs adjustment.
    # Typically: screen_y = Horizon - (world_y - camera_height) * scale
    # But for a simple floor drawing:
    # Floor objects have y=0. 
    # screen_y = Horizon + (Camera_Height * scale)
    
    sy = HORIZON_Y + (CAMERA_HEIGHT - y) * scale
    
    return int(sx), int(sy), scale

# ---------------- CLASSES ----------------

class GameObject:
    def __init__(self, x, z):
        self.x = x      # World X
        self.y = 0      # World Y (Ground)
        self.z = z      # World Z (Depth)
        self.width = 0  # To be set by subclass
        self.height = 0 # To be set by subclass

    def update(self, speed):
        self.z -= speed
        
    def get_screen_pos(self):
        return project_3d(self.x, self.y, self.z)

class Tree(GameObject):
    def __init__(self, x, z):
        super().__init__(x, z)
        self.width = 80
        self.height = 120
        self.type = "TREE"

    def draw(self, surface):
        sx, sy, scale = self.get_screen_pos()
        if scale <= 0: return

        # Dimensions on screen
        w = self.width * scale
        h = self.height * scale
        
        # Trunk
        trunk_w = w * 0.3
        trunk_h = h * 0.4
        pygame.draw.rect(surface, BROWN, (sx - trunk_w//2, sy - trunk_h, trunk_w, trunk_h))
        
        # Leaves (Triangle or Circle)
        # Main foliage
        pygame.draw.circle(surface, GREEN, (int(sx), int(sy - h * 0.8)), int(w * 0.6))
        pygame.draw.circle(surface, DARK_GREEN, (int(sx - w*0.2), int(sy - h * 0.7)), int(w * 0.4))
        pygame.draw.circle(surface, DARK_GREEN, (int(sx + w*0.2), int(sy - h * 0.7)), int(w * 0.4))


class Building(GameObject):
    def __init__(self, x, z, b_type, side):
        super().__init__(x, z)
        self.width = 150
        self.height = 120
        self.type = b_type
        self.side = side
        self.visited = False
        self.depth = 100 # How deep the building is in Z
        
        if self.type == "MARKET":
            self.color = RED
            self.label = "Market"
            self.action_text = "Buying Veggies..."
            self.duration = 180
        elif self.type == "MALL":
            self.color = PURPLE
            self.label = "Mall"
            self.action_text = "Shopping..."
            self.duration = 240
        elif self.type == "COLLEGE":
            self.color = BLUE
            self.label = "College"
            self.action_text = "Studying..."
            self.duration = 300
    
    def draw(self, surface):
        # We need to draw a 3D box primarily
        # Front face
        sx, sy, scale = self.get_screen_pos()
        if scale <= 0: return
        
        w = self.width * scale
        h = self.height * scale
        
        # Simple Front Face
        rect = pygame.Rect(sx - w//2, sy - h, w, h)
        pygame.draw.rect(surface, self.color, rect)
        pygame.draw.rect(surface, BLACK, rect, 2)
        
        # Side Face (Pseudo-3D)
        # If on LEFT, show RIGHT side. If on RIGHT, show LEFT side.
        side_width = 20 * scale # Arbitrary depth visual
        roof_poly = []
        side_poly = []
        
        if self.side == "LEFT":
            # Right side visible
            side_poly = [
                (rect.right, rect.top),
                (rect.right + side_width, rect.top - side_width),
                (rect.right + side_width, rect.bottom - side_width),
                (rect.right, rect.bottom)
            ]
            roof_poly = [
                (rect.left, rect.top),
                (rect.right, rect.top),
                (rect.right + side_width, rect.top - side_width),
                (rect.left + side_width, rect.top - side_width)
            ]
        else:
            # Left side visible
            side_poly = [
                (rect.left, rect.top),
                (rect.left - side_width, rect.top - side_width),
                (rect.left - side_width, rect.bottom - side_width),
                (rect.left, rect.bottom)
            ]
             # Roof same logic just shifted? 
            roof_poly = [
                (rect.left, rect.top),
                (rect.right, rect.top),
                (rect.right - side_width, rect.top - side_width),
                (rect.left - side_width, rect.top - side_width)
            ]
            
        pygame.draw.polygon(surface, [c//2 for c in self.color], side_poly)
        pygame.draw.polygon(surface, DARK_GRAY, roof_poly)
        
        # Door
        door_w = w * 0.3
        door_h = h * 0.4
        pygame.draw.rect(surface, (50, 50, 50), (sx - door_w//2, sy - door_h, door_w, door_h))
        
        # Text
        text = font.render(self.label, True, WHITE)
        t_w, t_h = text.get_size()
        # Scale text? simpler to just blit centered
        # Ideally scale text, but pygame font scaling is expensive. 
        # We'll just draw it if building is close enough
        if scale > 0.5:
            surface.blit(text, (sx - t_w//2, sy - h - 30))

class Home(GameObject):
    def __init__(self, z):
        super().__init__(0, z) # Centered
        self.width = 200
        self.height = 150
        self.type = "HOME"
        
    def draw(self, surface):
        sx, sy, scale = self.get_screen_pos()
        if scale <= 0: return
        w = self.width * scale
        h = self.height * scale
        
        # House Body
        pygame.draw.rect(surface, (255, 228, 196), (sx - w//2, sy - h, w, h)) # Bisque
        
        # Roof (Triangle)
        roof_pts = [
            (sx - w//2 - 10*scale, sy - h),
            (sx + w//2 + 10*scale, sy - h),
            (sx, sy - h - 50*scale)
        ]
        pygame.draw.polygon(surface, (139, 0, 0), roof_pts)
        
        # Door
        door_w = w * 0.25
        door_h = h * 0.5
        pygame.draw.rect(surface, (101, 67, 33), (sx - door_w//2, sy - door_h, door_w, door_h))
        
        # Label
        if scale > 0.5:
            lbl = font.render("HOME", True, WHITE)
            surface.blit(lbl, (sx - lbl.get_width()//2, sy - h - 60*scale))


class Boy:
    def __init__(self):
        # The boy stays at a fixed Z screen-wise, but we animate his sprite
        # We simulate "walking" by moving world Z.
        # But for interactions, he might move X.
        
        # Screen position (fixed mostly)
        self.screen_x = WIDTH // 2
        self.screen_y = HEIGHT - 50
        
        # World X (for lateral movement)
        self.world_x = 0 
        
        self.state = "WALKING" # WALKING, TO_BUILDING, INTERACTING, FROM_BUILDING, AT_HOME
        self.target_building = None
        self.interaction_timer = 0
        self.anim_frame = 0
        
    def update(self, buildings, speed):
        self.anim_frame += 0.2
        
        if self.state == "WALKING":
            # Check for buildings to visit
            # In 3D, we check when they get close (low Z)
            for b in buildings:
                if not b.visited and b.z < 600 and b.z > 200: # Approaching
                     # Random chance or logic to visit
                     if random.random() < 0.02: # Small chance per frame while in range
                        self.state = "TO_BUILDING"
                        self.target_building = b
                        break

        elif self.state == "TO_BUILDING":
            # Move Boy World X towards Building World X
            # Also world continues to approach (Z decreases) until we are parallel?
            # Or we pause Z movement and walk over?
            # Let's pause Z scroll for interaction in 3D to keep it simple.
            
            target_x = self.target_building.x
            dx = target_x - self.world_x
            
            move_speed = 5
            if abs(dx) < move_speed:
                self.world_x = target_x
                self.state = "INTERACTING"
                self.interaction_timer = self.target_building.duration
            else:
                self.world_x += math.copysign(move_speed, dx)

        elif self.state == "INTERACTING":
            self.interaction_timer -= 1
            if self.interaction_timer <= 0:
                self.target_building.visited = True
                self.state = "FROM_BUILDING"

        elif self.state == "FROM_BUILDING":
            # Return to center (world_x = 0)
            target_x = 0
            dx = target_x - self.world_x
            
            move_speed = 5
            if abs(dx) < move_speed:
                self.world_x = target_x
                self.state = "WALKING"
                self.target_building = None
            else:
                self.world_x += math.copysign(move_speed, dx)
                
    def draw(self, surface):
        # Simple Boy Sprite
        # Based on animation frame for legs
        
        sx, sy, scale = project_3d(self.world_x, 0, 150) # Z=150 is "camera distance" visual
        # Actually boy is always at screen bottom, so let's just use fixed screen Y
        # but modify scale slightly
        
        # Override project_3d for boy to keep him grounded nicely at bottom
        sx = (WIDTH // 2) + (self.world_x * 1.5) # 1.5 arbitrary scale for lateral
        sy = HEIGHT - 80
        scale = 1.0
        
        # Bounding box for reference
        # pygame.draw.rect(surface, WHITE, (sx-20, sy-80, 40, 80), 1)
        
        # Colors
        head_c = SKIN
        body_c = CLOTHES
        
        # Bobbing
        bob = math.sin(self.anim_frame) * 5 if self.state != "INTERACTING" else 0
        
        # Head
        pygame.draw.circle(surface, head_c, (int(sx), int(sy - 70 + bob)), 15)
        
        # Body
        pygame.draw.rect(surface, body_c, (sx - 10, sy - 55 + bob, 20, 30))
        
        # Legs
        if self.state == "INTERACTING":
            pygame.draw.line(surface, BLACK, (sx-5, sy-25), (sx-5, sy), 3)
            pygame.draw.line(surface, BLACK, (sx+5, sy-25), (sx+5, sy), 3)
        else:
            # Walking legs
            l_off = math.sin(self.anim_frame) * 10
            r_off = math.sin(self.anim_frame + math.pi) * 10
            pygame.draw.line(surface, BLACK, (sx-5, sy-25+bob), (sx-5-l_off, sy+10), 3)
            pygame.draw.line(surface, BLACK, (sx+5, sy-25+bob), (sx+5-r_off, sy+10), 3)

        # Interaction Text
        if self.state == "INTERACTING":
            msg = self.target_building.action_text
            text = font.render(msg, True, BLACK)
            rect = text.get_rect(center=(sx, sy - 100))
            surface.blit(text, rect)
            
            # Bar
            pct = self.interaction_timer / self.target_building.duration
            pygame.draw.rect(surface, RED, (sx-30, sy-90, 60, 5))
            pygame.draw.rect(surface, GREEN, (sx-30, sy-90, 60*pct, 5))

# ---------------- GENERATOR & MAIN ----------------

objects = []
z_cursor = 200 # Start spawning objects from here
distance_travelled = 0
home_spawned = False
home_object = None

def spawn_objects(start_z, end_z):
    z = start_z
    while z < end_z:
        # Spawn interval
        z += random.randint(150, 300)
        
        if random.random() < 0.4:
            # Building
            side = "LEFT" if random.random() < 0.5 else "RIGHT"
            x_pos = -250 if side == "LEFT" else 250
            b_type = random.choice(["MARKET", "MALL", "COLLEGE"])
            objects.append(Building(x_pos, z, b_type, side))
        else:
            # Trees (clumps?)
            side = "LEFT" if random.random() < 0.5 else "RIGHT"
            x_base = -300 if side == "LEFT" else 300
            objects.append(Tree(x_base + random.randint(-50, 50), z))
            if random.random() < 0.5:
                 objects.append(Tree(x_base + random.randint(-50, 50), z + 50))

# Initial Spawn
spawn_objects(200, 2000)
z_cursor = 2000

boy = Boy()

running = True
while running:
    # 1. Event Handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            
    # 2. Update Logic
    if boy.state != "INTERACTING" and boy.state != "AT_HOME":
        move_speed = SCROLL_SPEED
        # Slow down interactions
        if boy.state == "TO_BUILDING" or boy.state == "FROM_BUILDING":
            move_speed = 1
            
        distance_travelled += move_speed
        
        # Move objects
        for obj in objects:
            obj.update(move_speed)
            
        # Spawn new objects
        # We need to spawn ahead. The furthest object defines horizon filling.
        # Check max z
        if objects:
            max_z = max(o.z for o in objects)
        else:
            max_z = 0
            
        if max_z < 2000 and not home_spawned:
            spawn_objects(max_z, 2000)
        
        # Check Home condition
        if distance_travelled > TOTAL_DISTANCE and not home_spawned:
            home_spawned = True
            # Spawn home far away
            h_z = 2000
            home_object = Home(h_z)
            objects.append(home_object)
            
        # Clean up behind camera
        objects = [o for o in objects if o.z > -100]
        
    # Check if Home Reached
    if home_object and home_object.z < HOME_Z_TRIGGER:
        boy.state = "AT_HOME"

    # Boy Update
    buildings = [o for o in objects if isinstance(o, Building)]
    boy.update(buildings, SCROLL_SPEED)

    # 3. Draw
    # Sky
    screen.fill(SKY_BLUE)
    pygame.draw.rect(screen, GREEN, (0, HORIZON_Y, WIDTH, HEIGHT - HORIZON_Y)) # Ground
    
    # Road (Trapezoid for perspective)
    # At horizon, road is narrow. As screen bottom, full width.
    # z=infinity -> width=0 at horizon. z=0 -> width=ROAD_WIDTH at bottom.
    
    # Project 4 points of road segment
    # Let's draw road as one big polygon or segments?
    # Simple polygon for main road
    road_poly = [
        project_3d(-ROAD_WIDTH_3D//2, 0, 10)[0:2], # Near Left
        project_3d(ROAD_WIDTH_3D//2, 0, 10)[0:2],  # Near Right
        project_3d(ROAD_WIDTH_3D//2, 0, 3000)[0:2],# Far Right
        project_3d(-ROAD_WIDTH_3D//2, 0, 3000)[0:2]# Far Left
    ]
    pygame.draw.polygon(screen, GRAY, road_poly)
    
    # Stripes
    # Animate texture offset
    tex_offset = (distance_travelled % (SEGMENT_LENGTH * 2))
    
    # Draw stripes from z_min to z_max
    for z in range(int(10 - tex_offset), 2000, SEGMENT_LENGTH * 2):
        if z < 1: continue
        p1 = project_3d(-10, 0, z)
        p2 = project_3d(10, 0, z)
        p3 = project_3d(10, 0, z + SEGMENT_LENGTH)
        p4 = project_3d(-10, 0, z + SEGMENT_LENGTH)
        if p1[2] > 0 and p4[2] > 0:
             pygame.draw.polygon(screen, WHITE, [p1[0:2], p2[0:2], p3[0:2], p4[0:2]])

    # Draw Objects (Painters Algorithm: High Z first)
    objects.sort(key=lambda o: o.z, reverse=True)
    for obj in objects:
        obj.draw(screen)
        
    # Draw Boy
    boy.draw(screen)
    
    # UI
    # Distance Bar
    pygame.draw.rect(screen, BLACK, (10, 10, 200, 20), 2)
    progress = min(distance_travelled / TOTAL_DISTANCE, 1.0)
    pygame.draw.rect(screen, GREEN, (12, 12, 196 * progress, 16))
    
    if boy.state == "AT_HOME":
        txt = large_font.render("REACHED HOME!", True, YELLOW)
        # Shadow
        screen.blit(large_font.render("REACHED HOME!", True, BLACK), (WIDTH//2 - txt.get_width()//2 + 2, HEIGHT//2 - 50 + 2))
        screen.blit(txt, (WIDTH//2 - txt.get_width()//2, HEIGHT//2 - 50))
        
        sub = font.render("Press SPACE to Exit", True, WHITE)
        screen.blit(sub, (WIDTH//2 - sub.get_width()//2, HEIGHT//2 + 10))
        
        keys = pygame.key.get_pressed()
        if keys[pygame.K_SPACE]:
            running = False
            
    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()
