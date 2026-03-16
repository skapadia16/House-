
import pygame
import math

def draw_vertical_gradient(surface, rect, top_color, bottom_color):
    """Draws a vertical gradient explicitly on a surface."""
    color_rect = pygame.Surface((2, 2))
    pygame.draw.line(color_rect, top_color, (0, 0), (1, 0))
    pygame.draw.line(color_rect, bottom_color, (0, 1), (1, 1))
    color_rect = pygame.transform.smoothscale(color_rect, (rect.width, rect.height))
    surface.blit(color_rect, rect)

def create_soft_shadow(width, height, color, spread=10, radius=20):
    """Creates a surface with a soft, blurred shadow."""
    # Create a larger surface to hold the blur
    s_width = width + spread * 2
    s_height = height + spread * 2
    shadow_surf = pygame.Surface((s_width, s_height), pygame.SRCALPHA)
    
    # Draw the base shadow shape (ellipse for perspective)
    rect = pygame.Rect(spread, spread, width, height)
    pygame.draw.ellipse(shadow_surf, color, rect)
    
    # To simulate blur without heavy dependencies (like numpy/scipy),
    # we can scale down and scale up
    small_shadow = pygame.transform.smoothscale(shadow_surf, (s_width // 4, s_height // 4))
    blurred_shadow = pygame.transform.smoothscale(small_shadow, (s_width, s_height))
    
    return blurred_shadow

def draw_rounded_rect(surface, color, rect, radius=0.4):
    """
    Draws a rectangle with rounded corners.
    rect: pygame.Rect or tuple (x, y, w, h)
    radius: float, 0 to 1, relative to shortest side
    """
    rect = pygame.Rect(rect)
    color = pygame.Color(*color)
    alpha = color.a
    color.a = 0
    pos = rect.topleft
    rect.topleft = 0,0
    rectangle = pygame.Surface(rect.size,pygame.SRCALPHA)

    circle_radius = min(rect.width, rect.height) * radius * 0.5
    circle_radius = int(circle_radius)

    if circle_radius <= 0:
        pygame.draw.rect(surface, color, rect)
        return

    pygame.draw.circle(rectangle, color, (circle_radius, circle_radius), circle_radius)
    pygame.draw.circle(rectangle, color, (rect.width - circle_radius, circle_radius), circle_radius)
    pygame.draw.circle(rectangle, color, (circle_radius, rect.height - circle_radius), circle_radius)
    pygame.draw.circle(rectangle, color, (rect.width - circle_radius, rect.height - circle_radius), circle_radius)

    rectangle.fill(color, pygame.Rect(circle_radius, 0, rect.width - 2 * circle_radius, rect.height))
    rectangle.fill(color, pygame.Rect(0, circle_radius, rect.width, rect.height - 2 * circle_radius))

    surface.blit(rectangle, pos)
