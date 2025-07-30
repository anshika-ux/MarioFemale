import pygame
import math
import random
import colorsys

# Initialize Pygame
pygame.init()
pygame.mixer.init()  # Initialize the mixer for audio

# Load audio files
jump_sound = pygame.mixer.Sound('jump.wav')
coin_sound = pygame.mixer.Sound('coin.wav')
losing_sound = pygame.mixer.Sound('losing.wav')
# Set volume levels
jump_sound.set_volume(0.5)
coin_sound.set_volume(0.4)
losing_sound.set_volume(0.6)

# Background music
pygame.mixer.music.load('retro-song.mp3')
pygame.mixer.music.set_volume(0.3)  # Lower volume for background music
pygame.mixer.music.play(-1)  # -1 means loop indefinitely
pygame.mixer.init()  # Initialize the mixer for audio

# Load audio files
jump_sound = pygame.mixer.Sound('jump.wav')
coin_sound = pygame.mixer.Sound('coin.wav')
losing_sound = pygame.mixer.Sound('losing.wav')
# Set volume levels
jump_sound.set_volume(0.5)
coin_sound.set_volume(0.4)
losing_sound.set_volume(0.6)

# Background music
pygame.mixer.music.load('retro-song.mp3')
pygame.mixer.music.set_volume(0.3)  # Lower volume for background music
pygame.mixer.music.play(-1)  # -1 means loop indefinitely

# Helper function for rainbow colors
def hsv_to_rgb(h, s, v):
    r, g, b = colorsys.hsv_to_rgb(h, s, v)
    return int(r * 255), int(g * 255), int(b * 255)

# Constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60
GRAVITY = 0.6
TERMINAL_VELOCITY = 12

# Enhanced Colors with more arcade-like vibrant tones
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
PINK = (255, 105, 180)  # Hot pink - more vibrant
SOFT_PINK = (255, 182, 193)
BROWN = (160, 82, 45)
LIGHT_BROWN = (205, 133, 63)
GREEN = (0, 255, 0)  # Bright arcade green
DARK_GREEN = (0, 180, 0)
BLUE = (0, 191, 255)  # Deep sky blue - more vibrant
LIGHT_BLUE = (135, 206, 250)
YELLOW = (255, 255, 0)  # Bright arcade yellow
GOLD = (255, 215, 0)
RED = (255, 0, 0)  # Pure arcade red
SKIN = (255, 220, 177)
SHADOW_COLOR = (0, 0, 0, 80)
PURPLE = (170, 0, 255)  # Vibrant arcade purple
ORANGE = (255, 165, 0)
GRAY = (169, 169, 169)
LAVA_RED = (255, 69, 0)
ICE_BLUE = (176, 224, 230)
NEON_GREEN = (57, 255, 20)  # Arcade neon green
NEON_PINK = (255, 20, 147)  # Arcade neon pink
NEON_BLUE = (0, 191, 255)   # Arcade neon blue
NEON_YELLOW = (255, 255, 0) # Arcade neon yellow
NEON_RED = (255, 0, 0)      # Arcade neon red

def create_3d_surface(width, height, top_color, bottom_color, alpha=255):
    """Create a surface with 3D gradient effect"""
    surface = pygame.Surface((width, height), pygame.SRCALPHA)
    for y in range(height):
        ratio = y / height
        r = int(top_color[0] * (1 - ratio) + bottom_color[0] * ratio)
        g = int(top_color[1] * (1 - ratio) + bottom_color[1] * ratio)
        b = int(top_color[2] * (1 - ratio) + bottom_color[2] * ratio)
        pygame.draw.line(surface, (r, g, b, alpha), (0, y), (width, y))
    return surface

def draw_3d_rect(surface, rect, top_color, bottom_color, border_color=None):
    """Draw a 3D rectangle with gradient and optional border"""
    # Main gradient
    gradient_surf = create_3d_surface(rect.width, rect.height, top_color, bottom_color)
    surface.blit(gradient_surf, rect)
    
    # Arcade-style bold border
    if border_color:
        pygame.draw.rect(surface, border_color, rect, 2)
        
        # Add pixel-art style corners for arcade feel
        pygame.draw.rect(surface, border_color, (rect.x, rect.y, 4, 4))
        pygame.draw.rect(surface, border_color, (rect.x + rect.width - 4, rect.y, 4, 4))
        pygame.draw.rect(surface, border_color, (rect.x, rect.y + rect.height - 4, 4, 4))
        pygame.draw.rect(surface, border_color, (rect.x + rect.width - 4, rect.y + rect.height - 4, 4, 4))

def draw_3d_circle(surface, center, radius, inner_color, outer_color, glow=False):
    """Draw a 3D circle with depth and optional glow"""
    if glow:
        # Arcade-style neon glow effect
        for i in range(radius + 15, radius, -2):
            alpha = max(0, 60 - (i - radius) * 4)
            glow_surf = pygame.Surface((i*2, i*2), pygame.SRCALPHA)
            pygame.draw.circle(glow_surf, (*outer_color, alpha), (i, i), i)
            surface.blit(glow_surf, (center[0] - i, center[1] - i))
    
    # Main circle with gradient rings
    for i in range(radius, 0, -1):
        ratio = (radius - i) / radius
        r = int(outer_color[0] * (1 - ratio) + inner_color[0] * ratio)
        g = int(outer_color[1] * (1 - ratio) + inner_color[1] * ratio)
        b = int(outer_color[2] * (1 - ratio) + inner_color[2] * ratio)
        pygame.draw.circle(surface, (r, g, b), center, i)
    
    # Arcade-style highlight
    highlight_pos = (center[0] - radius//3, center[1] - radius//3)
    pygame.draw.circle(surface, tuple(min(255, c + 100) for c in inner_color), 
                      highlight_pos, radius//3)
                      
    # Add pixel-art style border for arcade feel
    pygame.draw.circle(surface, BLACK, center, radius, 1)

class Camera:
    def __init__(self):
        self.x = 0
        self.y = 0
        self.target_x = 0
        self.shake_x = 0
        self.shake_y = 0
        self.shake_duration = 0
        self.smoothness = 0.03  # Even smoother camera movement
        self.deadzone_width = 200  # Camera only moves when player exits this central zone
    
    def update(self, target):
        # Calculate the center of the screen in world coordinates
        screen_center_x = self.x + SCREEN_WIDTH // 2
        
        # Only move camera if player exits the deadzone
        if target.x < screen_center_x - self.deadzone_width // 2:
            # Player is too far left - move camera left
            self.target_x = target.x - SCREEN_WIDTH // 2 + self.deadzone_width // 2
        elif target.x > screen_center_x + self.deadzone_width // 2:
            # Player is too far right - move camera right
            self.target_x = target.x - SCREEN_WIDTH // 2 - self.deadzone_width // 2
        
        # Very smooth camera movement
        self.x += (self.target_x - self.x) * self.smoothness
        
        # Vertical camera only follows for significant height changes
        target_y = max(0, target.y - SCREEN_HEIGHT // 2)
        if abs(target_y - self.y) > 100:  # Only adjust Y for big jumps/falls
            self.y += (target_y - self.y) * (self.smoothness * 0.5)  # Even slower vertical adjustment
        
        # Reduced camera shake effect
        if self.shake_duration > 0:
            self.shake_x = random.randint(-2, 2)  # Further reduced from -3, 3
            self.shake_y = random.randint(-1, 1)  # Further reduced from -2, 2
            self.shake_duration -= 1
        else:
            self.shake_x = 0
            self.shake_y = 0
    
    def add_shake(self, duration=3):  # Further reduced default duration
        self.shake_duration = duration

class Player:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = 30
        self.height = 42
        self.vel_x = 0
        self.vel_y = 0
        self.speed = 6.0  # Slightly reduced from 6.5
        self.jump_power = 15  # Slightly reduced from 16
        self.on_ground = False
        self.direction = 1
        self.animation_frame = 0
        self.ground_y = SCREEN_HEIGHT - 60  # Fixed ground level
        self.trail_positions = []
        self.invulnerable = 0
        self.double_jump = True  # Allow double jump
        self.health = 2  # Player can take two hits
        
        # Power-up effects
        self.speed_boost = 0
        self.jump_boost = 0
        self.shield_active = 0
        self.star_power = 0
        
        # Trail settings
        self.max_trail_length = 5  # Reduced from 8 for less visual clutter
        
    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)
    
    def update(self, platforms):
        # Handle input
        keys = pygame.key.get_pressed()
        self.vel_x = 0
        
        # Apply speed boost if active
        current_speed = self.speed
        if self.speed_boost > 0:
            current_speed *= 1.4  # Reduced from 1.5
            self.speed_boost -= 1
        
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.vel_x = -current_speed
            self.direction = -1
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.vel_x = current_speed
            self.direction = 1
        if (keys[pygame.K_SPACE] or keys[pygame.K_UP] or keys[pygame.K_w]):
            # Apply jump boost if active
            current_jump_power = self.jump_power
            if self.jump_boost > 0:
                current_jump_power *= 1.2  # Reduced from 1.3
            
            if self.on_ground:
                self.vel_y = -current_jump_power
                self.on_ground = False
                self.double_jump = True
                # Play jump sound
                jump_sound.play()
            elif self.double_jump:  # Allow double jump if available
                self.vel_y = -current_jump_power * 0.8
                self.double_jump = False
                # Play jump sound for double jump too
                jump_sound.play()
                # Create jump effect particles
                for _ in range(3):  # Reduced from 5
                    particle = {
                        'x': self.x + self.width//2,
                        'y': self.y + self.height,
                        'vel_x': random.uniform(-1.5, 1.5),  # Reduced from -2, 2
                        'vel_y': random.uniform(0, 1.5),     # Reduced from 0, 2
                        'life': 15,                          # Reduced from 20
                        'color': (255, 255, 255)
                    }
                    if 'particles' in globals():
                        particle.append(particle)
        
        # Apply gravity
        if not self.on_ground:
            self.vel_y += GRAVITY
        if self.vel_y > TERMINAL_VELOCITY:
            self.vel_y = TERMINAL_VELOCITY
        
        # Update horizontal position
        self.x += self.vel_x
        
        # Update vertical position
        self.y += self.vel_y
        
        # Check ground collision first
        if self.y + self.height >= self.ground_y:
            self.y = self.ground_y - self.height
            self.vel_y = 0
            self.on_ground = True
        else:
            self.on_ground = False
        
        # Check platform collisions
        player_rect = self.get_rect()
        for platform in platforms:
            if player_rect.colliderect(platform.get_rect()):
                # Landing on top of platform
                if self.vel_y > 0 and self.y < platform.y:
                    self.y = platform.y - self.height
                    self.vel_y = 0
                    self.on_ground = True
                # Hitting platform from below
                elif self.vel_y < 0 and self.y > platform.y:
                    self.y = platform.y + platform.height
                    self.vel_y = 0
                # Side collisions
                elif self.vel_x > 0:  # Moving right
                    self.x = platform.x - self.width
                elif self.vel_x < 0:  # Moving left
                    self.x = platform.x + platform.width
        
        # Keep player on screen horizontally
        if self.x < 0:
            self.x = 0
        
        # Animation and effects - slower animation for less dizziness
        if self.vel_x != 0:
            self.animation_frame += 0.15  # Reduced from 0.25
        else:
            self.animation_frame = 0
        
        # Trail effect - fewer positions for less visual clutter
        if len(self.trail_positions) > self.max_trail_length:
            self.trail_positions.pop(0)
        self.trail_positions.append((self.x + self.width//2, self.y + self.height//2))
        
        # Invulnerability countdown
        if self.invulnerable > 0:
            self.invulnerable -= 1
            
        # Power-up countdowns
        if self.shield_active > 0:
            self.shield_active -= 1
            
        if self.star_power > 0:
            self.star_power -= 1
    
    def draw(self, screen, camera):
        x = self.x - camera.x + camera.shake_x
        y = self.y - camera.y + camera.shake_y
        
        # Draw trail effect with enhanced colors - reduced opacity and size
        for i, (trail_x, trail_y) in enumerate(self.trail_positions[:-1]):
            alpha = (i / len(self.trail_positions)) * 60  # Reduced from 80
            trail_size = 6 + i  # Reduced from 8 + i
            trail_surf = pygame.Surface((trail_size, trail_size), pygame.SRCALPHA)
            
            # Rainbow trail effect or star power effect - less intense colors
            if self.star_power > 0:
                # Star power rainbow effect - slower color change
                hue = (i * 20 + pygame.time.get_ticks() // 50) % 360  # Slower change
                r, g, b = hsv_to_rgb(hue/360, 0.7, 0.9)  # Less saturated
            else:
                # Normal rainbow trail - slower color change
                hue = (i * 20) % 360  # Reduced from 30
                r, g, b = hsv_to_rgb(hue/360, 0.7, 0.9)  # Less saturated
                
            pygame.draw.circle(trail_surf, (r, g, b, int(alpha)), (trail_size//2, trail_size//2), trail_size//2)
            screen.blit(trail_surf, (trail_x - camera.x - trail_size//2, trail_y - camera.y - trail_size//2))
        
        # Invulnerability flashing - less frequent
        if self.invulnerable > 0 and self.invulnerable % 8 < 4 and self.star_power <= 0:  # Changed from 6/3 to 8/4
            return
        
        # Enhanced shadow with blur effect
        shadow_size = max(self.width + 8, 20)
        shadow_surf = pygame.Surface((shadow_size, 12), pygame.SRCALPHA)
        for i in range(3):
            alpha = 80 - i * 20
            pygame.draw.ellipse(shadow_surf, (0, 0, 0, alpha), 
                              (i, i, shadow_size - i*2, 12 - i*2))
        screen.blit(shadow_surf, (x - 4, y + self.height + 2))
        
        # Body (dress with enhanced 3D effect and sparkles)
        dress_rect = pygame.Rect(x - 5, y + 20, self.width + 10, 22)
        
        # Star power effect changes dress color - less intense
        if self.star_power > 0:
            hue = (pygame.time.get_ticks() // 100) % 360  # Slower change
            r, g, b = hsv_to_rgb(hue/360, 0.7, 0.9)  # Less saturated
            draw_3d_rect(screen, dress_rect, (r, g, b), (r*0.8, g*0.8, b*0.8), (r, g, b))
        else:
            draw_3d_rect(screen, dress_rect, (255, 180, 255), SOFT_PINK, PINK)
        
        # Dress shine and details
        pygame.draw.ellipse(screen, (255, 255, 255, 150), (x - 2, y + 22, self.width + 4, 8))
        
        # Dress pattern with animated sparkles - fewer sparkles
        for i in range(3):  # Reduced from 4
            sparkle_x = x + 8 + i * 7
            sparkle_y = y + 30
            sparkle_size = 1.5 + math.sin(self.animation_frame + i) * 0.5  # Reduced size and animation
            pygame.draw.circle(screen, (255, 255, 255), (int(sparkle_x), int(sparkle_y)), int(sparkle_size))
        
        # Head with enhanced 3D effect and glow
        head_center = (int(x + self.width//2), int(y + 12))
        
        # Star power effect changes head color - less intense
        if self.star_power > 0:
            hue = (pygame.time.get_ticks() // 100 + 120) % 360  # Slower change
            r, g, b = hsv_to_rgb(hue/360, 0.5, 0.9)  # Less saturated
            draw_3d_circle(screen, head_center, 14, (r, g, b), (r*0.8, g*0.8, b*0.8), glow=False)  # No glow
        else:
            draw_3d_circle(screen, head_center, 14, (255, 240, 200), SKIN, glow=False)  # No glow
        
        # Hair with volume and animation - reduced bounce
        hair_bounce = int(math.sin(self.animation_frame) * 1) if self.vel_x != 0 else 0  # Reduced from 2
        
        # Main hair with 3D effect and shine
        hair_rect = pygame.Rect(x + 4, y - 5, self.width - 8, 20)
        draw_3d_rect(screen, hair_rect, (180, 100, 255), (140, 80, 200), (160, 90, 220))
        
        # Hair shine
        pygame.draw.ellipse(screen, (200, 150, 255, 150), (x + 6, y - 3, self.width - 12, 6))
        
        # Animated pigtails with enhanced 3D and ribbons - reduced bounce
        left_pigtail = (int(x + 2), int(y + 6) + hair_bounce)
        right_pigtail = (int(x + self.width - 2), int(y + 6) - hair_bounce)
        
        draw_3d_circle(screen, left_pigtail, 9, (180, 100, 255), (140, 80, 200))
        draw_3d_circle(screen, right_pigtail, 9, (180, 100, 255), (140, 80, 200))
        
        # Ribbons
        pygame.draw.circle(screen, (255, 100, 150), (left_pigtail[0] - 4, left_pigtail[1] - 2), 4)
        pygame.draw.circle(screen, (255, 100, 150), (right_pigtail[0] + 4, right_pigtail[1] - 2), 4)
        
        # Enhanced eyes with shine, depth and expression
        eye_y = y + 11
        
        # Eyebrows that show emotion - reduced movement
        brow_offset = 0
        if self.vel_y < 0:  # Jumping - surprised
            brow_offset = -1  # Reduced from -2
        elif self.vel_x != 0:  # Moving - determined
            brow_offset = 1
            
        if self.direction == 1:
            # Right-facing eyes
            pygame.draw.circle(screen, WHITE, (int(x + 9), int(eye_y)), 4)
            pygame.draw.circle(screen, WHITE, (int(x + 18), int(eye_y)), 4)
            pygame.draw.circle(screen, BLACK, (int(x + 10), int(eye_y)), 2)
            pygame.draw.circle(screen, BLACK, (int(x + 19), int(eye_y)), 2)
            # Eye shine
            pygame.draw.circle(screen, WHITE, (int(x + 11), int(eye_y - 1)), 1)
            pygame.draw.circle(screen, WHITE, (int(x + 20), int(eye_y - 1)), 1)
            # Eyebrows
            pygame.draw.line(screen, (140, 80, 200), (x + 6, eye_y - 5 + brow_offset), (x + 12, eye_y - 4), 2)
            pygame.draw.line(screen, (140, 80, 200), (x + 15, eye_y - 4), (x + 21, eye_y - 5 + brow_offset), 2)
        else:
            # Left-facing eyes
            pygame.draw.circle(screen, WHITE, (int(x + 9), int(eye_y)), 4)
            pygame.draw.circle(screen, WHITE, (int(x + 18), int(eye_y)), 4)
            pygame.draw.circle(screen, BLACK, (int(x + 8), int(eye_y)), 2)
            pygame.draw.circle(screen, BLACK, (int(x + 17), int(eye_y)), 2)
            pygame.draw.circle(screen, WHITE, (int(x + 7), int(eye_y - 1)), 1)
            pygame.draw.circle(screen, WHITE, (int(x + 16), int(eye_y - 1)), 1)
            # Eyebrows
            pygame.draw.line(screen, (140, 80, 200), (x + 6, eye_y - 4), (x + 12, eye_y - 5 + brow_offset), 2)
            pygame.draw.line(screen, (140, 80, 200), (x + 15, eye_y - 5 + brow_offset), (x + 21, eye_y - 4), 2)
        
        # Cute smile
        smile_y = eye_y + 5
        if self.vel_x != 0 or self.vel_y < 0:  # Happy when moving or jumping
            pygame.draw.arc(screen, (255, 150, 150), (x + 10, smile_y, 10, 6), 0, math.pi, 2)
        else:  # Neutral when standing
            pygame.draw.line(screen, (255, 150, 150), (x + 12, smile_y + 3), (x + 18, smile_y + 3), 2)
        
        # Arms with enhanced movement and 3D - reduced swing
        arm_swing = int(math.sin(self.animation_frame) * 3) if self.vel_x != 0 else 0  # Reduced from 4
        left_arm = (int(x - 6), int(y + 25) + arm_swing)
        right_arm = (int(x + self.width + 6), int(y + 25) - arm_swing)
        
        draw_3d_circle(screen, left_arm, 7, (255, 230, 190), SKIN)
        draw_3d_circle(screen, right_arm, 7, (255, 230, 190), SKIN)
        
        # Legs with enhanced walking animation - reduced offset
        leg_offset = int(math.sin(self.animation_frame) * 3) if self.vel_x != 0 else 0  # Reduced from 5
        
        # Left leg with 3D effect
        leg_rect1 = pygame.Rect(x + 6, y + 38, 7, 12)
        draw_3d_rect(screen, leg_rect1, (255, 230, 190), SKIN)
        
        # Right leg with 3D effect
        leg_rect2 = pygame.Rect(x + 17, y + 38, 7, 12)
        draw_3d_rect(screen, leg_rect2, (255, 230, 190), SKIN)
        
        # Enhanced shoes with 3D effect, animation and sparkles
        shoe1_center = (int(x + 9), int(y + 50) + leg_offset//2)
        shoe2_center = (int(x + 21), int(y + 50) - leg_offset//2)
        
        draw_3d_circle(screen, shoe1_center, 8, (255, 150, 255), (255, 100, 200), glow=False)  # No glow
        draw_3d_circle(screen, shoe2_center, 8, (255, 150, 255), (255, 100, 200), glow=False)  # No glow
        
        # Shoe sparkles - reduced frequency
        if random.randint(1, 15) == 1:  # Reduced from 1 in 10
            sparkle_x = shoe1_center[0] + random.randint(-3, 3)
            sparkle_y = shoe1_center[1] + random.randint(-3, 3)
            pygame.draw.circle(screen, WHITE, (sparkle_x, sparkle_y), 1)
            
            sparkle_x = shoe2_center[0] + random.randint(-3, 3)
            sparkle_y = shoe2_center[1] + random.randint(-3, 3)
            pygame.draw.circle(screen, WHITE, (sparkle_x, sparkle_y), 1)
            
        # Health indicator
        for i in range(self.health):
            heart_x = x + self.width//2 - 5 + i * 10
            heart_y = y - 10
            pygame.draw.circle(screen, (255, 100, 100), (heart_x - 2, heart_y), 3)
            pygame.draw.circle(screen, (255, 100, 100), (heart_x + 2, heart_y), 3)
            pygame.draw.polygon(screen, (255, 100, 100), [(heart_x, heart_y + 4), (heart_x - 4, heart_y), (heart_x + 4, heart_y)])
        
        # Shield effect if active - less intense pulsing
        if self.shield_active > 0:
            shield_radius = self.width + 8  # Reduced from 10
            shield_surf = pygame.Surface((shield_radius * 2, shield_radius * 2), pygame.SRCALPHA)
            
            # Pulsing shield effect - reduced intensity
            pulse = int(math.sin(pygame.time.get_ticks() / 300) * 30)  # Slower, less intense
            shield_color = (100, 150, 255, 80 + pulse)  # Lower base opacity
            
            pygame.draw.circle(shield_surf, shield_color, (shield_radius, shield_radius), shield_radius)
            screen.blit(shield_surf, (x + self.width//2 - shield_radius, y + self.height//2 - shield_radius))

class Platform:
    def __init__(self, x, y, width, height, color=GREEN, platform_type="grass"):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.color = color
        self.platform_type = platform_type
        self.animation = 0
        self.pixel_pattern = []
        
        # Create arcade-style pixel pattern
        for i in range(0, width, 8):
            for j in range(0, height, 8):
                if random.random() > 0.8:
                    self.pixel_pattern.append((i, j))
        
    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)
    
    def update(self):
        self.animation += 0.02
    
    def draw(self, screen, camera):
        x = self.x - camera.x + camera.shake_x
        y = self.y - camera.y + camera.shake_y
        
        # Platform shadow
        shadow_surf = pygame.Surface((self.width + 8, 8), pygame.SRCALPHA)
        pygame.draw.ellipse(shadow_surf, (0, 0, 0, 100), (0, 0, self.width + 8, 8))
        screen.blit(shadow_surf, (x - 4, y + self.height + 3))
        
        # Main platform with enhanced arcade-style gradient and type-specific effects
        platform_rect = pygame.Rect(x, y, self.width, self.height)
        
        if self.platform_type == "grass":
            top_color = (0, 220, 0)  # Softer green
            bottom_color = (0, 180, 0)  # Darker green
            draw_3d_rect(screen, platform_rect, top_color, bottom_color, BLACK)
            
            # Arcade-style grass texture
            for i in range(0, self.width, 10):
                grass_height = 5 + int(math.sin(self.animation * 5 + i * 0.1) * 2)
                pygame.draw.line(screen, DARK_GREEN, 
                               (x + i, y), 
                               (x + i, y + grass_height), 2)
        
        elif self.platform_type == "ice":
            top_color = (100, 200, 255)  # Softer blue
            bottom_color = (80, 150, 220)  # Darker blue
            draw_3d_rect(screen, platform_rect, top_color, bottom_color, BLACK)
            
            # Arcade-style ice shine
            for i in range(0, self.width, 15):
                shine_x = x + i + int(math.sin(self.animation * 3) * 5)
                shine_y = y + 3
                pygame.draw.circle(screen, WHITE, (shine_x, shine_y), 2)
        
        elif self.platform_type == "lava":
            # Pulsing lava color for arcade feel
            pulse = int(math.sin(self.animation * 8) * 50)
            top_color = (255, 100, 50)  # Softer red
            bottom_color = (200, 50, 0)  # Darker red
            draw_3d_rect(screen, platform_rect, top_color, bottom_color, BLACK)
            
            # Arcade-style lava bubbles
            for i in range(3):
                if random.randint(1, 20) == 1:
                    bubble_x = x + random.randint(5, self.width - 5)
                    bubble_y = y + random.randint(2, self.height - 2)
                    bubble_size = random.randint(2, 4)
                    pygame.draw.circle(screen, YELLOW, (bubble_x, bubble_y), bubble_size)
        
        # Arcade-style pixel pattern overlay
        for pixel in self.pixel_pattern:
            pixel_x = x + pixel[0]
            pixel_y = y + pixel[1]
            if 0 <= pixel_x < SCREEN_WIDTH and 0 <= pixel_y < SCREEN_HEIGHT:
                pygame.draw.rect(screen, tuple(min(255, c + 50) for c in self.color), 
                               (pixel_x, pixel_y, 2, 2))

class PowerUp:
    def __init__(self, x, y, power_type="speed"):
        self.x = x
        self.y = y
        self.radius = 15
        self.collected = False
        self.rotation = 0
        self.bob = 0
        self.glow = 0
        self.power_type = power_type
        self.particle_timer = 0
        self.pixel_size = 3  # For arcade-style pixelated look
        
    def get_rect(self):
        return pygame.Rect(self.x - self.radius, self.y - self.radius, 
                          self.radius * 2, self.radius * 2)
    
    def update(self):
        self.rotation += 0.15
        self.bob += 0.1
        self.glow += 0.2
        self.particle_timer += 1
    
    def draw(self, screen, camera):
        if self.collected:
            return
        
        x = self.x - camera.x + camera.shake_x
        y = self.y - camera.y + camera.shake_y + math.sin(self.bob) * 4
        
        # Arcade-style power-up colors
        colors = {
            "speed": NEON_BLUE,    # Neon blue for speed
            "jump": NEON_GREEN,    # Neon green for jump
            "shield": NEON_PINK,   # Neon pink for shield
            "star": NEON_YELLOW    # Neon yellow for star (invincibility)
        }
        power_color = colors.get(self.power_type, colors["speed"])
        
        # Arcade-style pulsing glow effect
        glow_size = 25 + int(math.sin(self.glow) * 8)
        glow_surf = pygame.Surface((glow_size * 2, glow_size * 2), pygame.SRCALPHA)
        
        # Multiple glow layers for arcade neon effect
        for i in range(4):
            alpha = 100 - i * 20
            pygame.draw.circle(glow_surf, (*power_color, alpha), 
                             (glow_size, glow_size), glow_size - i*4)
        screen.blit(glow_surf, (x - glow_size, y - glow_size))
        
        # Arcade-style pixelated power-up
        for px in range(-self.radius, self.radius, self.pixel_size):
            for py in range(-self.radius, self.radius, self.pixel_size):
                # Calculate distance from center to determine if pixel is part of the circle
                distance = math.sqrt(px**2 + py**2)
                
                if distance <= self.radius:
                    # Arcade-style shading
                    shade = 1.0 - (distance / self.radius) * 0.3
                    pixel_color = tuple(min(255, int(c * shade)) for c in power_color)
                    
                    # Add highlight to top-left pixels
                    if px < 0 and py < 0:
                        pixel_color = tuple(min(255, c + 70) for c in pixel_color)
                        
                    pygame.draw.rect(screen, pixel_color, 
                                   (x + px, y + py, self.pixel_size, self.pixel_size))
        
        # Arcade-style power-up icon based on type
        if self.power_type == "speed":
            # Lightning bolt - pixelated
            points = [(x, y-8), (x-4, y), (x, y+2), (x+4, y)]
            pygame.draw.polygon(screen, WHITE, points)
            # Pixel outline
            pygame.draw.polygon(screen, BLACK, points, 1)
            
        elif self.power_type == "jump":
            # Up arrow - pixelated
            points = [(x, y-8), (x-6, y), (x-2, y), (x-2, y+6), (x+2, y+6), (x+2, y), (x+6, y)]
            pygame.draw.polygon(screen, WHITE, points)
            # Pixel outline
            pygame.draw.polygon(screen, BLACK, points, 1)
            
        elif self.power_type == "shield":
            # Shield shape - pixelated
            shield_rect = pygame.Rect(x-8, y-8, 16, 16)
            pygame.draw.arc(screen, WHITE, shield_rect, math.pi/4, math.pi*7/4, 3)
            # Pixel details
            for i in range(3):
                pygame.draw.rect(screen, WHITE, (x-6+i*6, y+4, 2, 2))
                
        elif self.power_type == "star":
            # Star shape - pixelated
            points = []
            for i in range(5):
                angle = math.pi/2 + i * 2*math.pi/5
                outer_x = x + 8 * math.cos(angle)
                outer_y = y + 8 * math.sin(angle)
                points.append((outer_x, outer_y))
                
                inner_angle = angle + math.pi/5
                inner_x = x + 4 * math.cos(inner_angle)
                inner_y = y + 4 * math.sin(inner_angle)
                points.append((inner_x, inner_y))
                
            pygame.draw.polygon(screen, WHITE, points)
            # Pixel outline
            pygame.draw.polygon(screen, BLACK, points, 1)
        
        # Arcade-style particle effects
        if self.particle_timer % 5 == 0:
            for _ in range(2):
                particle_x = x + random.randint(-12, 12)
                particle_y = y + random.randint(-12, 12)
                particle_size = random.randint(1, 3)
                pygame.draw.rect(screen, power_color, 
                               (particle_x, particle_y, particle_size, particle_size))

class Coin:
    def __init__(self, x, y, coin_type="gold"):
        self.x = x
        self.y = y
        self.radius = 12
        self.collected = False
        self.rotation = 0
        self.bob = 0
        self.glow = 0
        self.coin_type = coin_type
        self.particle_timer = 0
        self.pixel_size = 2  # For arcade-style pixelated look
        
    def get_rect(self):
        return pygame.Rect(self.x - self.radius, self.y - self.radius, 
                          self.radius * 2, self.radius * 2)
    
    def update(self):
        self.rotation += 0.12
        self.bob += 0.08
        self.glow += 0.15
        self.particle_timer += 1
    
    def draw(self, screen, camera):
        if self.collected:
            return
        
        x = self.x - camera.x + camera.shake_x
        y = self.y - camera.y + camera.shake_y + math.sin(self.bob) * 3
        
        # Arcade-style coin colors
        colors = {
            "gold": NEON_YELLOW,
            "silver": (220, 220, 220),
            "ruby": NEON_PINK
        }
        coin_color = colors.get(self.coin_type, colors["gold"])
        
        # Arcade-style glow effect
        glow_size = 20 + int(math.sin(self.glow) * 5)
        glow_surf = pygame.Surface((glow_size * 2, glow_size * 2), pygame.SRCALPHA)
        for i in range(3):
            alpha = 100 - i * 30
            pygame.draw.circle(glow_surf, (*coin_color, alpha), 
                             (glow_size, glow_size), glow_size - i*3)
        screen.blit(glow_surf, (x - glow_size, y - glow_size))
        
        # Arcade-style pixelated coin
        width_scale = abs(math.cos(self.rotation))
        coin_width = int(self.radius * 2 * width_scale)
        
        if width_scale > 0.1:
            # Draw pixelated coin shape
            for px in range(0, coin_width, self.pixel_size):
                for py in range(0, self.radius * 2, self.pixel_size):
                    # Calculate distance from center to determine if pixel is part of the circle
                    center_x = coin_width / 2
                    center_y = self.radius
                    pixel_x = px + self.pixel_size / 2
                    pixel_y = py + self.pixel_size / 2
                    
                    distance = math.sqrt((pixel_x - center_x)**2 + (pixel_y - center_y)**2)
                    
                    if distance <= self.radius:
                        # Arcade-style shading
                        shade = 1.0 - (distance / self.radius) * 0.5
                        pixel_color = tuple(min(255, int(c * shade)) for c in coin_color)
                        
                        # Add highlight to top-left pixels
                        if pixel_x < center_x and pixel_y < center_y:
                            pixel_color = tuple(min(255, c + 50) for c in pixel_color)
                            
                        pygame.draw.rect(screen, pixel_color, 
                                       (x - self.radius * width_scale + px, 
                                        y - self.radius + py, 
                                        self.pixel_size, self.pixel_size))
            
            # Arcade-style coin symbol
            if width_scale > 0.7:
                if self.coin_type == "gold":
                    symbol_color = (255, 220, 0)
                    symbol = "$"
                elif self.coin_type == "silver":
                    symbol_color = (200, 200, 200)
                    symbol = "S"
                else:  # ruby
                    symbol_color = (255, 100, 100)
                    symbol = "R"
                
                font = pygame.font.Font(None, 20)
                symbol_surf = font.render(symbol, True, symbol_color)
                symbol_rect = symbol_surf.get_rect(center=(x, y))
                screen.blit(symbol_surf, symbol_rect)
                
        # Arcade-style particle effects
        if self.particle_timer % 10 == 0:
            for _ in range(1):
                particle_x = x + random.randint(-10, 10)
                particle_y = y + random.randint(-10, 10)
                particle_size = random.randint(1, 3)
                pygame.draw.rect(screen, coin_color, 
                               (particle_x, particle_y, particle_size, particle_size))

class Enemy:
    def __init__(self, x, y, enemy_type="goomba", vel_x=-1.8):
        self.x = x
        self.y = y
        self.width = 24
        self.height = 24
        self.vel_x = vel_x  # Allow custom velocity and direction
        self.start_x = x
        self.animation = 0
        self.enemy_type = enemy_type
        self.health = 1
        self.pixel_size = 2  # For arcade-style pixelated look
        
    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)
    
    def update(self, platforms):
        self.x += self.vel_x
        self.animation += 0.15
        
        # Bounce between boundaries
        if abs(self.x - self.start_x) > 100:
            self.vel_x *= -1
    
    def draw(self, screen, camera):
        x = self.x - camera.x + camera.shake_x
        y = self.y - camera.y + camera.shake_y
        
        # Arcade-style shadow
        shadow_surf = pygame.Surface((self.width + 8, 8), pygame.SRCALPHA)
        pygame.draw.ellipse(shadow_surf, (0, 0, 0, 100), (0, 0, self.width + 8, 8))
        screen.blit(shadow_surf, (x - 4, y + self.height + 3))
        
        if self.enemy_type == "goomba":
            # Arcade-style pixelated body
            bounce = int(math.sin(self.animation * 2.5) * 2)
            
            # Body pixels
            for px in range(-12, 12, self.pixel_size):
                for py in range(-12, 12, self.pixel_size):
                    # Calculate distance from center to determine if pixel is part of the circle
                    distance = math.sqrt(px**2 + py**2)
                    
                    if distance <= 11:
                        # Arcade-style shading
                        shade = 1.0 - (distance / 11) * 0.3
                        
                        # Different colors for body parts
                        if py < -2:  # Head area
                            pixel_color = tuple(min(255, int(c * shade)) for c in LIGHT_BROWN)
                        else:  # Body area
                            pixel_color = tuple(min(255, int(c * shade)) for c in BROWN)
                            
                        pygame.draw.rect(screen, pixel_color, 
                                       (x + self.width//2 + px, 
                                        y + 12 + py + bounce, 
                                        self.pixel_size, self.pixel_size))
            
            # Arcade-style pixelated eyes
            eye_y = y + 7 + bounce
            
            # Left eye
            pygame.draw.rect(screen, BLACK, (x + 6, eye_y - 2, 4, 4))
            pygame.draw.rect(screen, RED, (x + 7, eye_y - 1, 2, 2))
            
            # Right eye
            pygame.draw.rect(screen, BLACK, (x + 14, eye_y - 2, 4, 4))
            pygame.draw.rect(screen, RED, (x + 15, eye_y - 1, 2, 2))
            
            # Arcade-style pixelated eyebrows
            pygame.draw.rect(screen, BLACK, (x + 5, eye_y - 4, 5, 2))
            pygame.draw.rect(screen, BLACK, (x + 14, eye_y - 4, 5, 2))
            
            # Arcade-style pixelated feet
            foot_bounce = int(math.sin(self.animation * 5) * 2)
            pygame.draw.rect(screen, (100, 60, 30), (x + 2, y + 20 + foot_bounce, 6, 6))
            pygame.draw.rect(screen, (100, 60, 30), (x + 16, y + 20 - foot_bounce, 6, 6))
            
            # Arcade-style angry mouth
            pygame.draw.rect(screen, BLACK, (x + 9, y + 14 + bounce, 6, 2))

class GameMap:
    def __init__(self, map_id=1):
        self.map_id = map_id
        self.platforms = []
        self.coins = []
        self.enemies = []
        self.pipes = []
        self.clouds = []
        self.power_ups = []  # Add power-ups list
        self.gate = {}  # Add gate for level completion
        self.background_color = LIGHT_BLUE
        self.ground_color = GREEN
        self.generate_map()
    
    def generate_map(self):
        if self.map_id == 1:  # Grassland
            self.create_grassland_map()
        elif self.map_id == 2:  # Ice World
            self.create_ice_map()
        elif self.map_id == 3:  # Lava World
            self.create_lava_map()
        elif self.map_id == 4:  # Sky World
            self.create_sky_map()
        elif self.map_id == 5:  # Underground
            self.create_underground_map()
    
    def create_grassland_map(self):
        # Platforms - all positioned just above the ground level
        ground_level = SCREEN_HEIGHT - 80  # Just above the ground
        self.platforms = [
            # Ground level platforms
            Platform(180, ground_level, 100, 20, GREEN, "grass"),
            Platform(350, ground_level, 80, 20, GREEN, "grass"),
            Platform(500, ground_level, 120, 20, GREEN, "grass"),
            Platform(700, ground_level, 90, 20, GREEN, "grass"),
            Platform(870, ground_level, 110, 20, GREEN, "grass"),
            Platform(1050, ground_level, 130, 20, GREEN, "grass"),
            Platform(1250, ground_level, 100, 20, GREEN, "grass"),
            Platform(1420, ground_level, 150, 20, GREEN, "grass"),
            
            # Upper bricks for jumping and catching coins
            Platform(230, ground_level - 120, 60, 20, GREEN, "grass"),
            Platform(400, ground_level - 150, 60, 20, GREEN, "grass"),
            Platform(550, ground_level - 130, 60, 20, GREEN, "grass"),
            Platform(750, ground_level - 140, 60, 20, GREEN, "grass"),
            Platform(900, ground_level - 160, 60, 20, GREEN, "grass"),
            Platform(1100, ground_level - 130, 60, 20, GREEN, "grass"),
            Platform(1300, ground_level - 150, 60, 20, GREEN, "grass"),
            
            # Additional bricks for more platforms
            Platform(300, ground_level - 200, 50, 20, GREEN, "grass"),
            Platform(480, ground_level - 220, 50, 20, GREEN, "grass"),
            Platform(650, ground_level - 180, 50, 20, GREEN, "grass"),
            Platform(820, ground_level - 240, 50, 20, GREEN, "grass"),
            Platform(980, ground_level - 200, 50, 20, GREEN, "grass"),
            Platform(1150, ground_level - 220, 50, 20, GREEN, "grass"),
            Platform(1380, ground_level - 190, 50, 20, GREEN, "grass"),
        ]
        
        # Coins - reduced overall but added some on ground level
        self.coins = [
            # Ground level coins
            Coin(250, ground_level - 30, "gold"),
            Coin(450, ground_level - 30, "silver"),
            Coin(650, ground_level - 30, "gold"),
            Coin(850, ground_level - 30, "silver"),
            Coin(1050, ground_level - 30, "gold"),
            Coin(1250, ground_level - 30, "ruby"),
            
            # Some coins on middle platforms
            Coin(230, ground_level - 170, "gold"),
            Coin(550, ground_level - 180, "silver"),
            Coin(900, ground_level - 210, "ruby"),
            
            # A few coins on highest platforms
            Coin(300, ground_level - 250, "gold"),
            Coin(820, ground_level - 290, "ruby"),
        ]
        
        # Power-ups - positioned higher above the platforms
        self.power_ups = [
            PowerUp(450, ground_level - 180, "speed"),
            PowerUp(1000, ground_level - 180, "jump"),
            PowerUp(1350, ground_level - 200, "shield"),
            PowerUp(820, ground_level - 290, "star"),  # Additional power-up
        ]
        
        # Enemies - positioned on top of platforms with different directions
        self.enemies = [
            Enemy(220, ground_level - 24, "goomba", -1.8),  # Moving left
            Enemy(540, ground_level - 24, "goomba", 1.8),   # Moving right
            Enemy(900, ground_level - 24, "goomba", -1.5),  # Moving left, slower
            Enemy(1300, ground_level - 24, "goomba", 2.0),  # Moving right, faster
            # Additional enemies on upper platforms
            Enemy(230, ground_level - 120 - 24, "goomba", 1.7),  # On upper platform
            Enemy(550, ground_level - 130 - 24, "goomba", -1.6), # On upper platform
            Enemy(1100, ground_level - 130 - 24, "goomba", 1.9), # On upper platform
            Enemy(300, ground_level - 200 - 24, "goomba", -1.7), # On highest platform
        ]
        
        # End gate
        self.gate = {
            'x': 1550,
            'y': ground_level - 100,
            'width': 50,
            'height': 100,
            'color': (255, 215, 0)  # Gold color
        }
        
        # Clouds
        self.clouds = [
            Cloud(100, 80, 30),
            Cloud(400, 60, 35),
            Cloud(750, 100, 32),
            Cloud(1100, 70, 40),
            Cloud(1450, 90, 28),
        ]
    
    def create_ice_map(self):
        self.background_color = (200, 230, 255)
        self.ground_color = ICE_BLUE
        
        # Ice platforms - all positioned just above the ground level
        ground_level = SCREEN_HEIGHT - 80  # Just above the ground
        self.platforms = [
            # Ground level platforms
            Platform(150, ground_level, 120, 15, ICE_BLUE, "ice"),
            Platform(320, ground_level, 80, 15, ICE_BLUE, "ice"),
            Platform(480, ground_level, 100, 15, ICE_BLUE, "ice"),
            Platform(650, ground_level, 90, 15, ICE_BLUE, "ice"),
            Platform(820, ground_level, 110, 15, ICE_BLUE, "ice"),
            Platform(1000, ground_level, 140, 15, ICE_BLUE, "ice"),
            Platform(1200, ground_level, 90, 15, ICE_BLUE, "ice"),
            Platform(1380, ground_level, 160, 15, ICE_BLUE, "ice"),
            
            # Upper bricks for jumping and catching coins
            Platform(200, ground_level - 130, 60, 15, ICE_BLUE, "ice"),
            Platform(370, ground_level - 140, 60, 15, ICE_BLUE, "ice"),
            Platform(520, ground_level - 120, 60, 15, ICE_BLUE, "ice"),
            Platform(680, ground_level - 150, 60, 15, ICE_BLUE, "ice"),
            Platform(850, ground_level - 130, 60, 15, ICE_BLUE, "ice"),
            Platform(1050, ground_level - 140, 60, 15, ICE_BLUE, "ice"),
            Platform(1230, ground_level - 160, 60, 15, ICE_BLUE, "ice"),
            
            # Additional bricks for more platforms
            Platform(250, ground_level - 210, 50, 15, ICE_BLUE, "ice"),
            Platform(420, ground_level - 190, 50, 15, ICE_BLUE, "ice"),
            Platform(600, ground_level - 220, 50, 15, ICE_BLUE, "ice"),
            Platform(780, ground_level - 200, 50, 15, ICE_BLUE, "ice"),
            Platform(950, ground_level - 230, 50, 15, ICE_BLUE, "ice"),
            Platform(1120, ground_level - 210, 50, 15, ICE_BLUE, "ice"),
            Platform(1300, ground_level - 240, 50, 15, ICE_BLUE, "ice"),
        ]
        
        # Coins - reduced overall but added some on ground level
        self.coins = [
            # Ground level coins
            Coin(180, ground_level - 30, "silver"),
            Coin(400, ground_level - 30, "silver"),
            Coin(600, ground_level - 30, "ruby"),
            Coin(800, ground_level - 30, "silver"),
            Coin(1000, ground_level - 30, "ruby"),
            Coin(1200, ground_level - 30, "silver"),
            
            # Some coins on middle platforms
            Coin(200, ground_level - 180, "silver"),
            Coin(520, ground_level - 170, "ruby"),
            Coin(850, ground_level - 180, "silver"),
            
            # A few coins on highest platforms
            Coin(600, ground_level - 270, "ruby"),
            Coin(950, ground_level - 280, "silver"),
        ]
        
        # Ice enemies - positioned on top of platforms with different directions
        self.enemies = [
            Enemy(190, ground_level - 24, "goomba", 1.6),   # Moving right
            Enemy(520, ground_level - 24, "goomba", -1.7),  # Moving left
            Enemy(860, ground_level - 24, "goomba", 1.9),   # Moving right, faster
            Enemy(1320, ground_level - 24, "goomba", -1.4), # Moving left, slower
            # Additional enemies on upper platforms
            Enemy(200, ground_level - 130 - 24, "goomba", -1.5),  # On upper platform
            Enemy(680, ground_level - 150 - 24, "goomba", 1.8),   # On upper platform
            Enemy(1230, ground_level - 160 - 24, "goomba", -1.6), # On upper platform
            Enemy(600, ground_level - 220 - 24, "goomba", 1.7),   # On highest platform
        ]
        
        # End gate
        self.gate = {
            'x': 1550,
            'y': ground_level - 100,
            'width': 50,
            'height': 100,
            'color': (176, 224, 230)  # Ice blue color
        }
        
        # Ice clouds
        self.clouds = [
            Cloud(80, 60, 25),
            Cloud(350, 40, 30),
            Cloud(680, 80, 28),
            Cloud(980, 50, 35),
            Cloud(1280, 70, 32),
        ]
    
    def create_lava_map(self):
        self.background_color = (255, 100, 50)
        self.ground_color = LAVA_RED
        
        # Lava platforms - all positioned just above the ground level
        ground_level = SCREEN_HEIGHT - 80  # Just above the ground
        self.platforms = [
            Platform(140, ground_level, 100, 20, LAVA_RED, "lava"),
            Platform(300, ground_level, 90, 20, LAVA_RED, "lava"),
            Platform(460, ground_level, 80, 20, LAVA_RED, "lava"),
            Platform(620, ground_level, 100, 20, LAVA_RED, "lava"),
            Platform(780, ground_level, 90, 20, LAVA_RED, "lava"),
            Platform(940, ground_level, 120, 20, LAVA_RED, "lava"),
            Platform(1120, ground_level, 80, 20, LAVA_RED, "lava"),
            Platform(1280, ground_level, 140, 20, LAVA_RED, "lava"),
            # Upper bricks for jumping and catching coins
            Platform(180, ground_level - 140, 60, 20, LAVA_RED, "lava"),
            Platform(340, ground_level - 120, 60, 20, LAVA_RED, "lava"),
            Platform(490, ground_level - 150, 60, 20, LAVA_RED, "lava"),
            Platform(660, ground_level - 130, 60, 20, LAVA_RED, "lava"),
            Platform(820, ground_level - 160, 60, 20, LAVA_RED, "lava"),
            Platform(990, ground_level - 140, 60, 20, LAVA_RED, "lava"),
            Platform(1150, ground_level - 120, 60, 20, LAVA_RED, "lava"),
        ]
        
        # Ruby and gold coins - positioned higher above the platforms
        self.coins = [
            Coin(190, ground_level - 190, "ruby"),
            Coin(345, ground_level - 170, "gold"),
            Coin(500, ground_level - 200, "ruby"),
            Coin(670, ground_level - 180, "ruby"),
            Coin(825, ground_level - 210, "ruby"),
            Coin(1000, ground_level - 190, "gold"),
            Coin(1160, ground_level - 170, "ruby"),
            Coin(1350, ground_level - 70, "ruby"),
        ]
        
        # Lava enemies - positioned on top of platforms with different directions
        self.enemies = [
            Enemy(180, ground_level - 24, "goomba", 2.0),   # Moving right, faster
            Enemy(490, ground_level - 24, "goomba", -2.0),  # Moving left, faster
            Enemy(810, ground_level - 24, "goomba", 1.7),   # Moving right
            Enemy(1200, ground_level - 24, "goomba", -1.7), # Moving left
        ]
        
        # End gate
        self.gate = {
            'x': 1550,
            'y': ground_level - 100,
            'width': 50,
            'height': 100,
            'color': (255, 69, 0)  # Lava red color
        }
        
        # Dark clouds
        self.clouds = [
            Cloud(120, 90, 20),
            Cloud(380, 70, 25),
            Cloud(640, 110, 22),
            Cloud(900, 80, 28),
            Cloud(1160, 100, 24),
        ]
    
    def create_sky_map(self):
        self.background_color = (135, 206, 250)
        self.ground_color = (255, 255, 255)
        
        # Cloud platforms - all positioned just above the ground level
        ground_level = SCREEN_HEIGHT - 80  # Just above the ground
        self.platforms = [
            Platform(160, ground_level, 80, 25, (255, 255, 255), "grass"),
            Platform(300, ground_level, 90, 25, (255, 255, 255), "grass"),
            Platform(450, ground_level, 70, 25, (255, 255, 255), "grass"),
            Platform(580, ground_level, 85, 25, (255, 255, 255), "grass"),
            Platform(720, ground_level, 95, 25, (255, 255, 255), "grass"),
            Platform(860, ground_level, 100, 25, (255, 255, 255), "grass"),
            Platform(1020, ground_level, 75, 25, (255, 255, 255), "grass"),
            Platform(1150, ground_level, 120, 25, (255, 255, 255), "grass"),
            # Upper bricks for jumping and catching coins
            Platform(190, ground_level - 150, 60, 25, (255, 255, 255), "grass"),
            Platform(330, ground_level - 130, 60, 25, (255, 255, 255), "grass"),
            Platform(470, ground_level - 160, 60, 25, (255, 255, 255), "grass"),
            Platform(610, ground_level - 140, 60, 25, (255, 255, 255), "grass"),
            Platform(750, ground_level - 120, 60, 25, (255, 255, 255), "grass"),
            Platform(890, ground_level - 150, 60, 25, (255, 255, 255), "grass"),
            Platform(1040, ground_level - 130, 60, 25, (255, 255, 255), "grass"),
        ]
        
        # All types of coins - positioned higher above the platforms
        self.coins = [
            Coin(200, ground_level - 200, "gold"),
            Coin(345, ground_level - 180, "silver"),
            Coin(485, ground_level - 210, "ruby"),
            Coin(625, ground_level - 190, "gold"),
            Coin(765, ground_level - 170, "ruby"),
            Coin(910, ground_level - 200, "silver"),
            Coin(1055, ground_level - 180, "ruby"),
            Coin(1210, ground_level - 70, "gold"),
        ]
        
        # Flying enemies - positioned on top of platforms with different directions
        self.enemies = [
            Enemy(230, ground_level - 24, "goomba", -1.5),  # Moving left, slower
            Enemy(470, ground_level - 24, "goomba", 1.8),   # Moving right
            Enemy(750, ground_level - 24, "goomba", -1.9),  # Moving left, faster
            Enemy(1080, ground_level - 24, "goomba", 1.6),  # Moving right
        ]
        
        # End gate
        self.gate = {
            'x': 1550,
            'y': ground_level - 100,
            'width': 50,
            'height': 100,
            'color': (135, 206, 250)  # Sky blue color
        }
        
        # Many clouds
        self.clouds = [
            Cloud(50, 120, 35),
            Cloud(250, 80, 40),
            Cloud(450, 140, 32),
            Cloud(650, 60, 45),
            Cloud(850, 120, 38),
            Cloud(1050, 90, 42),
            Cloud(1250, 130, 35),
        ]
    
    def create_underground_map(self):
        self.background_color = (40, 20, 60)
        self.ground_color = (80, 60, 40)
        
        # Stone platforms - all positioned just above the ground level
        ground_level = SCREEN_HEIGHT - 80  # Just above the ground
        self.platforms = [
            Platform(130, ground_level, 110, 30, GRAY, "grass"),
            Platform(280, ground_level, 100, 30, GRAY, "grass"),
            Platform(420, ground_level, 90, 30, GRAY, "grass"),
            Platform(560, ground_level, 120, 30, GRAY, "grass"),
            Platform(720, ground_level, 80, 30, GRAY, "grass"),
            Platform(850, ground_level, 110, 30, GRAY, "grass"),
            Platform(1000, ground_level, 90, 30, GRAY, "grass"),
            Platform(1140, ground_level, 150, 30, GRAY, "grass"),
            # Upper bricks for jumping and catching coins
            Platform(170, ground_level - 140, 70, 30, GRAY, "grass"),
            Platform(320, ground_level - 160, 70, 30, GRAY, "grass"),
            Platform(450, ground_level - 130, 70, 30, GRAY, "grass"),
            Platform(600, ground_level - 150, 70, 30, GRAY, "grass"),
            Platform(750, ground_level - 170, 70, 30, GRAY, "grass"),
            Platform(880, ground_level - 140, 70, 30, GRAY, "grass"),
            Platform(1030, ground_level - 160, 70, 30, GRAY, "grass"),
        ]
        
        # Lots of coins underground - positioned higher above the platforms
        self.coins = [
            Coin(185, ground_level - 190, "gold"),
            Coin(330, ground_level - 210, "ruby"),
            Coin(465, ground_level - 180, "silver"),
            Coin(620, ground_level - 200, "gold"),
            Coin(765, ground_level - 220, "ruby"),
            Coin(905, ground_level - 190, "gold"),
            Coin(1045, ground_level - 210, "ruby"),
            Coin(1215, ground_level - 70, "silver"),
        ]
        
        # Underground enemies - positioned on top of platforms with different directions
        self.enemies = [
            Enemy(170, ground_level - 24, "goomba", 1.7),   # Moving right
            Enemy(450, ground_level - 24, "goomba", -1.8),  # Moving left
            Enemy(740, ground_level - 24, "goomba", 2.0),   # Moving right, faster
            Enemy(1080, ground_level - 24, "goomba", -1.6), # Moving left
        ]
        
        # End gate
        self.gate = {
            'x': 1550,
            'y': ground_level - 100,
            'width': 50,
            'height': 100,
            'color': (169, 169, 169)  # Gray color
        }
        
        # No clouds underground
        self.clouds = []

class Cloud:
    def __init__(self, x, y, size):
        self.x = x
        self.y = y
        self.size = size
        self.speed = random.uniform(0.2, 0.5)
        self.puff_offsets = [(random.randint(-15, 15), random.randint(-8, 8)) for _ in range(8)]
        self.alpha = random.randint(180, 255)
    
    def update(self):
        self.x += self.speed
        if self.x > 2500:
            self.x = -300
    
    def draw(self, screen, camera):
        x = self.x - camera.x * 0.3  # Enhanced parallax
        y = self.y
        
        # Draw enhanced cloud puffs with varying sizes
        for i, (offset_x, offset_y) in enumerate(self.puff_offsets):
            puff_x = int(x + offset_x)
            puff_y = int(y + offset_y)
            puff_size = self.size + random.randint(-2, 4)
            
            # Multi-layer cloud puffs for depth
            for layer in range(3):
                layer_alpha = self.alpha - layer * 60
                if layer_alpha > 0:
                    puff_surf = pygame.Surface((puff_size * 2, puff_size * 2), pygame.SRCALPHA)
                    color = (255 - layer * 20, 255 - layer * 20, 255 - layer * 10, layer_alpha)
                    pygame.draw.circle(puff_surf, color, (puff_size, puff_size), puff_size - layer * 2)
                    screen.blit(puff_surf, (puff_x - puff_size, puff_y - puff_size))

def draw_enhanced_background(screen, camera, current_map):
    # Solid color background instead of starfield
    if current_map.map_id == 1:  # Grassland
        bg_color = (50, 100, 200)  # Softer blue
    elif current_map.map_id == 2:  # Ice world
        bg_color = (100, 150, 220)  # Light blue
    elif current_map.map_id == 3:  # Lava world
        bg_color = (150, 50, 50)  # Dark red
    else:
        bg_color = (80, 80, 120)  # Default purple-blue
        
    screen.fill(bg_color)
    
    # Draw fewer stars that move more slowly
    for i in range(30):  # Reduced from 100
        star_x = (i * 73 + int(camera.x * 0.05)) % SCREEN_WIDTH  # Reduced parallax
        star_y = (i * 47) % SCREEN_HEIGHT  # No vertical movement
        star_size = random.randint(1, 2)  # Smaller stars
        
        # Less twinkling
        brightness = 180 + int(math.sin(pygame.time.get_ticks() / 1000 + i) * 50)  # Slower, less intense
        star_color = (brightness, brightness, brightness)
        
        pygame.draw.circle(screen, star_color, (star_x, star_y), star_size)
    
    # Enhanced ground with arcade-style pattern
    ground_rect = pygame.Rect(-camera.x, SCREEN_HEIGHT - 60, SCREEN_WIDTH * 3, 60)
    
    # Arcade-style ground with bright colors but less intense
    if current_map.map_id == 1:  # Grassland
        ground_color = (0, 180, 0)  # Green grass
        # Add grass details - more dense grass at player's feet level
        ground_surf = create_3d_surface(SCREEN_WIDTH * 3, 60, 
                                   tuple(min(255, c + 40) for c in ground_color),
                                   ground_color)
        screen.blit(ground_surf, ground_rect)
        
        # Add a full line of grass at player's feet
        grass_line_y = SCREEN_HEIGHT - 60
        for i in range(int(-camera.x), int(-camera.x) + SCREEN_WIDTH * 3, 3):  # Very dense grass (every 3 pixels)
            grass_height = random.randint(8, 20)  # Taller grass
            grass_x = i + random.randint(-1, 1)  # Slight x variation for natural look
            pygame.draw.line(screen, (0, 220, 0), (grass_x, grass_line_y), 
                           (grass_x, grass_line_y - grass_height), 2)
            
            # Add some darker grass for depth
            if random.random() > 0.6:
                dark_grass_height = random.randint(5, 15)
                pygame.draw.line(screen, (0, 150, 0), (grass_x + 1, grass_line_y), 
                               (grass_x + 1, grass_line_y - dark_grass_height), 2)
                               
            # Add some flower details occasionally
            if random.random() > 0.95:
                flower_y = grass_line_y - grass_height - 3
                flower_color = random.choice([(255, 255, 100), (255, 150, 150), (255, 255, 255)])
                pygame.draw.circle(screen, flower_color, (grass_x, flower_y), 2)
    elif current_map.map_id == 2:  # Ice world
        ground_color = (100, 200, 220)  # Softer blue
        ground_surf = create_3d_surface(SCREEN_WIDTH * 3, 60, 
                                   tuple(min(255, c + 40) for c in ground_color),
                                   ground_color)
        screen.blit(ground_surf, ground_rect)
        
        # Add ice crystals at player's feet
        grass_line_y = SCREEN_HEIGHT - 60
        for i in range(int(-camera.x), int(-camera.x) + SCREEN_WIDTH * 3, 15):
            crystal_height = random.randint(5, 12)
            crystal_x = i + random.randint(-5, 5)
            pygame.draw.polygon(screen, (220, 240, 255), [
                (crystal_x, grass_line_y),
                (crystal_x - 3, grass_line_y - crystal_height),
                (crystal_x, grass_line_y - crystal_height - 5),
                (crystal_x + 3, grass_line_y - crystal_height)
            ])
    elif current_map.map_id == 3:  # Lava world
        ground_color = (200, 100, 100)  # Softer red
        ground_surf = create_3d_surface(SCREEN_WIDTH * 3, 60, 
                                   tuple(min(255, c + 40) for c in ground_color),
                                   ground_color)
        screen.blit(ground_surf, ground_rect)
        
        # Add lava bubbles at player's feet
        grass_line_y = SCREEN_HEIGHT - 60
        for i in range(int(-camera.x), int(-camera.x) + SCREEN_WIDTH * 3, 20):
            if random.random() > 0.7:
                bubble_size = random.randint(3, 8)
                bubble_x = i + random.randint(-10, 10)
                pygame.draw.circle(screen, (255, 200, 100), (bubble_x, grass_line_y - bubble_size//2), bubble_size)
                pygame.draw.circle(screen, (255, 255, 150), (bubble_x - bubble_size//3, grass_line_y - bubble_size), bubble_size//3)
    else:
        ground_color = current_map.ground_color
        ground_surf = create_3d_surface(SCREEN_WIDTH * 3, 60, 
                                   tuple(min(255, c + 40) for c in ground_color),
                                   ground_color)
        screen.blit(ground_surf, ground_rect)
        
    # Simplified ground pattern - larger squares, less contrast
    pattern_size = 30  # Larger pattern
    for x in range(int(-camera.x), int(-camera.x) + SCREEN_WIDTH * 3, pattern_size):
        for y in range(SCREEN_HEIGHT - 60, SCREEN_HEIGHT, pattern_size):
            # Checkerboard pattern with less contrast
            if (x // pattern_size + y // pattern_size) % 2 == 0:
                pygame.draw.rect(screen, tuple(max(0, c - 20) for c in ground_color), 
                               (x, y, pattern_size, pattern_size), 1)

class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Enhanced 3D Mario-Style Platformer - Multiple Worlds")
        self.clock = pygame.time.Clock()
        
        # Game state
        self.current_map_id = 1
        self.current_map = GameMap(self.current_map_id)
        self.camera = Camera()
        self.player = Player(50, SCREEN_HEIGHT - 120)  # Start on ground level
        self.score = 0
        self.lives = 3
        self.level_complete = False
        self.game_over = False
        
        # Fonts
        self.font = pygame.font.Font(None, 36)
        self.small_font = pygame.font.Font(None, 24)
        
        # Particles for effects
        self.particles = []
        
    def create_particles(self, x, y, color, count=10):
        """Create particle effect"""
        for _ in range(count):
            particle = {
                'x': x + random.randint(-10, 10),
                'y': y + random.randint(-10, 10),
                'vel_x': random.uniform(-3, 3),
                'vel_y': random.uniform(-5, -1),
                'life': 30,
                'color': color
            }
            self.particles.append(particle)
    
    def update_particles(self):
        """Update and remove dead particles"""
        for particle in self.particles[:]:
            particle['x'] += particle['vel_x']
            particle['y'] += particle['vel_y']
            particle['vel_y'] += 0.2  # Gravity
            particle['life'] -= 1
            
            if particle['life'] <= 0:
                self.particles.remove(particle)
    
    def draw_particles(self):
        """Draw all particles"""
        for particle in self.particles:
            alpha = int((particle['life'] / 30) * 255)
            particle_surf = pygame.Surface((4, 4), pygame.SRCALPHA)
            color_with_alpha = (*particle['color'], alpha)
            pygame.draw.circle(particle_surf, color_with_alpha, (2, 2), 2)
            self.screen.blit(particle_surf, (particle['x'] - self.camera.x, particle['y'] - self.camera.y))
    
    def next_level(self):
        """Move to next map"""
        self.current_map_id += 1
        if self.current_map_id > 5:
            self.current_map_id = 1  # Loop back to first map
        
        self.current_map = GameMap(self.current_map_id)
        self.player.x = 50
        self.player.y = SCREEN_HEIGHT - 120  # Start on ground level
        self.player.vel_x = 0
        self.player.vel_y = 0
        self.level_complete = False
        
        # Play coin sound for level completion
        coin_sound.play()
        
        # Add level completion bonus
        self.score += 1000
        self.create_particles(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2, GOLD, 20)
    
    def reset_player(self):
        """Reset player position after death"""
        self.player.x = 50
        self.player.y = SCREEN_HEIGHT - 120  # Reset to ground level
        self.player.vel_x = 0
        self.player.vel_y = 0
        self.player.invulnerable = 120  # 2 seconds of invulnerability
        self.camera.add_shake(15)
        
        # Play losing sound
        losing_sound.play()
        
        # Reduce health instead of lives directly
        self.player.health -= 1
        if self.player.health <= 0:
            self.lives -= 1
            self.player.health = 2  # Reset health if a life is lost
            
        if self.lives <= 0:
            self.game_over = True
    
    def update(self):
        """Main game update loop"""
        if self.game_over:
            return
        
        # Update map platforms
        for platform in self.current_map.platforms:
            platform.update()
        
        # Update player
        self.player.update(self.current_map.platforms)
        self.camera.update(self.player)
        
        # Coin collection
        for coin in self.current_map.coins:
            coin.update()
            if not coin.collected and self.player.get_rect().colliderect(coin.get_rect()):
                coin.collected = True
                coin_values = {"gold": 100, "silver": 200, "ruby": 500}
                points = coin_values.get(coin.coin_type, 100)
                self.score += points
                # Play coin sound
                coin_sound.play()
                self.create_particles(coin.x, coin.y, GOLD if coin.coin_type == "gold" else 
                                    (192, 192, 192) if coin.coin_type == "silver" else (255, 0, 127), 8)
        
        # Power-up collection
        for power_up in self.current_map.power_ups:
            power_up.update()
            if not power_up.collected and self.player.get_rect().colliderect(power_up.get_rect()):
                power_up.collected = True
                
                # Apply power-up effect
                if power_up.power_type == "speed":
                    self.player.speed_boost = 300  # 5 seconds at 60 FPS
                    self.score += 150
                elif power_up.power_type == "jump":
                    self.player.jump_boost = 300
                    self.score += 150
                elif power_up.power_type == "shield":
                    self.player.shield_active = 600  # 10 seconds
                    self.score += 200
                elif power_up.power_type == "star":
                    self.player.star_power = 600  # 10 seconds
                    self.score += 300
                
                # Create power-up particles
                colors = {
                    "speed": (50, 200, 255),
                    "jump": (100, 255, 100),
                    "shield": (255, 100, 255),
                    "star": (255, 255, 100)
                }
                self.create_particles(power_up.x, power_up.y, colors.get(power_up.power_type, (255, 255, 255)), 12)
                self.camera.add_shake(5)  # Small screen shake for feedback
        
        # Enemy collision
        if self.player.invulnerable == 0 and self.player.shield_active == 0 and self.player.star_power == 0:
            for enemy in self.current_map.enemies:
                enemy.update(self.current_map.platforms)
                if self.player.get_rect().colliderect(enemy.get_rect()):
                    self.reset_player()
                    self.create_particles(self.player.x, self.player.y, RED, 15)
                    break
        elif self.player.star_power > 0:
            # With star power, defeat enemies on contact
            for enemy in self.current_map.enemies[:]:
                enemy.update(self.current_map.platforms)
                if self.player.get_rect().colliderect(enemy.get_rect()):
                    self.current_map.enemies.remove(enemy)
                    self.score += 300
                    self.create_particles(enemy.x, enemy.y, (255, 255, 0), 15)
                    self.camera.add_shake(8)
        else:
            # Just update enemies
            for enemy in self.current_map.enemies:
                enemy.update(self.current_map.platforms)
        
        # Update clouds
        for cloud in self.current_map.clouds:
            cloud.update()
        
        # Update particles
        self.update_particles()
        
        # Check level completion (reached gate)
        if 'x' in self.current_map.gate:
            gate_rect = pygame.Rect(
                self.current_map.gate['x'], 
                self.current_map.gate['y'], 
                self.current_map.gate['width'], 
                self.current_map.gate['height']
            )
            if self.player.get_rect().colliderect(gate_rect):
                self.level_complete = True
                self.next_level()
        
        # Check if player fell off the world
        if self.player.y > SCREEN_HEIGHT + 100:
            self.reset_player()
    
    def draw_ui(self):
        """Draw user interface"""
        # Arcade-style UI background - made wider to fit level names
        ui_bg = pygame.Rect(5, 5, 250, 180)
        pygame.draw.rect(self.screen, (0, 0, 0, 150), ui_bg)
        pygame.draw.rect(self.screen, NEON_PINK, ui_bg, 2)  # Changed to pink border
        
        # Simple pixelated corners (no hearts)
        pygame.draw.rect(self.screen, NEON_PINK, (5, 5, 4, 4))
        pygame.draw.rect(self.screen, NEON_PINK, (251, 5, 4, 4))
        pygame.draw.rect(self.screen, NEON_PINK, (5, 181, 4, 4))
        pygame.draw.rect(self.screen, NEON_PINK, (251, 181, 4, 4))
        
        # Cute score with shadow effect - smaller font
        small_font = pygame.font.Font(None, 28)  # Smaller font
        score_text = f"SCORE: "
        shadow_surf = small_font.render(score_text, True, BLACK)
        score_surf = small_font.render(score_text, True, NEON_GREEN)
        self.screen.blit(shadow_surf, (17, 17))
        self.screen.blit(score_surf, (15, 15))
        
        # Draw score as simple numbers without boxes
        score_str = str(self.score)
        score_digits = small_font.render(score_str, True, NEON_GREEN)
        score_shadow = small_font.render(score_str, True, BLACK)
        self.screen.blit(score_shadow, (92, 17))
        self.screen.blit(score_digits, (90, 15))
        
        # Lives with cute pink hearts
        lives_text = f"LIVES: "
        lives_shadow = small_font.render(lives_text, True, BLACK)
        lives_surf = small_font.render(lives_text, True, NEON_PINK)
        self.screen.blit(lives_shadow, (17, 57))
        self.screen.blit(lives_surf, (15, 55))
        
        # Draw cute animated hearts for lives
        heart_bounce = math.sin(pygame.time.get_ticks() / 500) * 2  # Gentle bouncing hearts
        for i in range(self.lives):
            heart_x = 90 + i * 30
            heart_y = 55 + int(heart_bounce) if i % 2 == 0 else 55 - int(heart_bounce)
            
            # Draw cute heart
            heart_size = 12
            # Draw the two circles of the heart
            pygame.draw.circle(self.screen, NEON_PINK, (heart_x - heart_size//4, heart_y - heart_size//4), heart_size//2)
            pygame.draw.circle(self.screen, NEON_PINK, (heart_x + heart_size//4, heart_y - heart_size//4), heart_size//2)
            
            # Draw the bottom triangle of the heart
            pygame.draw.polygon(self.screen, NEON_PINK, [
                (heart_x - heart_size//2, heart_y - heart_size//4),
                (heart_x + heart_size//2, heart_y - heart_size//4),
                (heart_x, heart_y + heart_size//2)
            ])
            
            # Add a cute shine to the heart
            pygame.draw.circle(self.screen, WHITE, (heart_x - heart_size//4, heart_y - heart_size//4), 2)
        
        # Current world with arcade-style text - smaller font to fit in box
        world_names = ["", "GRASSLAND", "ICE WORLD", "LAVA WORLD", "SKY WORLD", "UNDERGROUND"]
        world_text = f"WORLD: {world_names[self.current_map_id]}"
        world_shadow = small_font.render(world_text, True, BLACK)
        world_surf = small_font.render(world_text, True, NEON_YELLOW)
        self.screen.blit(world_shadow, (17, 97))
        self.screen.blit(world_surf, (15, 95))
        
        # Level number with arcade-style text
        level_text = f"LEVEL: {self.current_map_id}"
        level_shadow = small_font.render(level_text, True, BLACK)
        level_surf = small_font.render(level_text, True, NEON_BLUE)
        self.screen.blit(level_shadow, (17, 127))
        self.screen.blit(level_surf, (15, 125))
        
        # Active power-ups with arcade-style icons - smaller font
        power_up_y = 155
        if self.player.speed_boost > 0:
            power_text = f"SPEED: {self.player.speed_boost // 60 + 1}s"
            power_shadow = small_font.render(power_text, True, BLACK)
            power_surf = small_font.render(power_text, True, NEON_BLUE)
            self.screen.blit(power_shadow, (17, power_up_y + 2))
            self.screen.blit(power_surf, (15, power_up_y))
            
            # Speed icon
            pygame.draw.rect(self.screen, NEON_BLUE, (150, power_up_y, 10, 10))
            pygame.draw.rect(self.screen, BLACK, (150, power_up_y, 10, 10), 1)
            power_up_y += 25
            
        if self.player.jump_boost > 0:
            power_text = f"JUMP: {self.player.jump_boost // 60 + 1}s"
            power_shadow = small_font.render(power_text, True, BLACK)
            power_surf = small_font.render(power_text, True, NEON_GREEN)
            self.screen.blit(power_shadow, (17, power_up_y + 2))
            self.screen.blit(power_surf, (15, power_up_y))
            
            # Jump icon
            pygame.draw.rect(self.screen, NEON_GREEN, (150, power_up_y, 10, 10))
            pygame.draw.rect(self.screen, BLACK, (150, power_up_y, 10, 10), 1)
            power_up_y += 25
            
        if self.player.shield_active > 0:
            power_text = f"SHIELD: {self.player.shield_active // 60 + 1}s"
            power_shadow = small_font.render(power_text, True, BLACK)
            power_surf = small_font.render(power_text, True, NEON_PINK)
            self.screen.blit(power_shadow, (17, power_up_y + 2))
            self.screen.blit(power_surf, (15, power_up_y))
            
            # Shield icon
            pygame.draw.rect(self.screen, NEON_PINK, (150, power_up_y, 10, 10))
            pygame.draw.rect(self.screen, BLACK, (150, power_up_y, 10, 10), 1)
            power_up_y += 25
            
        if self.player.star_power > 0:
            power_text = f"STAR: {self.player.star_power // 60 + 1}s"
            power_shadow = small_font.render(power_text, True, BLACK)
            
            # Rainbow text for star power - arcade style
            hue = (pygame.time.get_ticks() // 100) % 360
            r, g, b = hsv_to_rgb(hue/360, 0.8, 1.0)
            power_surf = small_font.render(power_text, True, (r, g, b))
            
            self.screen.blit(power_shadow, (17, power_up_y + 2))
            self.screen.blit(power_surf, (15, power_up_y))
            
            # Star icon
            pygame.draw.rect(self.screen, NEON_YELLOW, (150, power_up_y, 10, 10))
            pygame.draw.rect(self.screen, BLACK, (150, power_up_y, 10, 10), 1)
        
        # Arcade-style instructions
        instructions = "ARROWS/WASD: MOVE • SPACE/UP: JUMP • M: MUTE • COLLECT COINS & POWER-UPS!"
        inst_shadow = self.small_font.render(instructions, True, BLACK)
        inst_surf = self.small_font.render(instructions, True, NEON_GREEN)
        self.screen.blit(inst_shadow, (12, SCREEN_HEIGHT - 28))
        self.screen.blit(inst_surf, (10, SCREEN_HEIGHT - 30))
        
        # Game Over screen with arcade-style
        if self.game_over:
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 200))
            self.screen.blit(overlay, (0, 0))
            
            # Arcade-style game over text
            game_over_text = "GAME OVER"
            final_score_text = f"FINAL SCORE: {self.score}"
            restart_text = "PRESS R TO RESTART"
            
            # Pixelated border for game over box
            border_rect = pygame.Rect(SCREEN_WIDTH//2 - 200, SCREEN_HEIGHT//2 - 120, 400, 240)
            pygame.draw.rect(self.screen, NEON_PINK, border_rect, 4)
            
            # Pixelated corners
            corner_size = 8
            pygame.draw.rect(self.screen, NEON_PINK, (border_rect.left, border_rect.top, corner_size, corner_size))
            pygame.draw.rect(self.screen, NEON_PINK, (border_rect.right - corner_size, border_rect.top, corner_size, corner_size))
            pygame.draw.rect(self.screen, NEON_PINK, (border_rect.left, border_rect.bottom - corner_size, corner_size, corner_size))
            pygame.draw.rect(self.screen, NEON_PINK, (border_rect.right - corner_size, border_rect.bottom - corner_size, corner_size, corner_size))
            
            # Arcade-style text with shadow
            go_font = pygame.font.Font(None, 72)
            go_shadow = go_font.render(game_over_text, True, BLACK)
            go_surf = go_font.render(game_over_text, True, NEON_RED)
            
            fs_shadow = self.font.render(final_score_text, True, BLACK)
            fs_surf = self.font.render(final_score_text, True, NEON_YELLOW)
            
            r_shadow = self.font.render(restart_text, True, BLACK)
            r_surf = self.font.render(restart_text, True, NEON_GREEN)
            
            self.screen.blit(go_shadow, (SCREEN_WIDTH//2 - go_surf.get_width()//2 + 2, SCREEN_HEIGHT//2 - 100 + 2))
            self.screen.blit(go_surf, (SCREEN_WIDTH//2 - go_surf.get_width()//2, SCREEN_HEIGHT//2 - 100))
            
            self.screen.blit(fs_shadow, (SCREEN_WIDTH//2 - fs_surf.get_width()//2 + 2, SCREEN_HEIGHT//2 - 20 + 2))
            self.screen.blit(fs_surf, (SCREEN_WIDTH//2 - fs_surf.get_width()//2, SCREEN_HEIGHT//2 - 20))
            
            self.screen.blit(r_shadow, (SCREEN_WIDTH//2 - r_surf.get_width()//2 + 2, SCREEN_HEIGHT//2 + 20 + 2))
            self.screen.blit(r_surf, (SCREEN_WIDTH//2 - r_surf.get_width()//2, SCREEN_HEIGHT//2 + 20))
    
    def restart_game(self):
        """Restart the game"""
        self.current_map_id = 1
        self.current_map = GameMap(self.current_map_id)
        self.player = Player(50, SCREEN_HEIGHT - 120)  # Start on ground level
        self.camera = Camera()
        self.score = 0
        self.lives = 3
        self.level_complete = False
        self.game_over = False
        self.particles = []
        
        # Restart music
        pygame.mixer.music.rewind()
    
    def run(self):
        """Main game loop"""
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_r and self.game_over:
                        self.restart_game()
                    # Add mute/unmute functionality with M key
                    elif event.key == pygame.K_m:
                        if pygame.mixer.music.get_volume() > 0:
                            pygame.mixer.music.set_volume(0)
                            jump_sound.set_volume(0)
                            coin_sound.set_volume(0)
                            losing_sound.set_volume(0)
                        else:
                            pygame.mixer.music.set_volume(0.3)
                            jump_sound.set_volume(0.5)
                            coin_sound.set_volume(0.4)
                            losing_sound.set_volume(0.6)
            
            self.update()
            
            # Draw everything
            draw_enhanced_background(self.screen, self.camera, self.current_map)
            
            # Draw clouds first (background)
            for cloud in self.current_map.clouds:
                cloud.draw(self.screen, self.camera)
            
            # Draw platforms
            for platform in self.current_map.platforms:
                platform.draw(self.screen, self.camera)
            
            # Draw coins
            for coin in self.current_map.coins:
                coin.draw(self.screen, self.camera)
                
            # Draw power-ups
            for power_up in self.current_map.power_ups:
                power_up.draw(self.screen, self.camera)
            
            # Draw enemies
            for enemy in self.current_map.enemies:
                enemy.draw(self.screen, self.camera)
            
            # Draw gate
            if 'x' in self.current_map.gate:
                gate_x = self.current_map.gate['x'] - self.camera.x + self.camera.shake_x
                gate_y = self.current_map.gate['y'] - self.camera.y + self.camera.shake_y
                gate_width = self.current_map.gate['width']
                gate_height = self.current_map.gate['height']
                gate_color = self.current_map.gate['color']
                
                # Draw gate with arcade-style effects
                pygame.draw.rect(self.screen, gate_color, (gate_x, gate_y, gate_width, gate_height))
                pygame.draw.rect(self.screen, BLACK, (gate_x, gate_y, gate_width, gate_height), 2)
                
                # Draw gate details
                pygame.draw.rect(self.screen, BLACK, (gate_x + 10, gate_y + 20, 30, 60))
                pygame.draw.rect(self.screen, WHITE, (gate_x + 12, gate_y + 22, 26, 56))
                
                # Draw level number on gate
                level_font = pygame.font.Font(None, 36)
                level_text = str(self.current_map_id + 1)  # Show next level
                level_surf = level_font.render(level_text, True, BLACK)
                level_rect = level_surf.get_rect(center=(gate_x + gate_width//2, gate_y + gate_height//2))
                self.screen.blit(level_surf, level_rect)
                
                # Draw some sparkles around the gate
                if random.randint(1, 10) == 1:
                    sparkle_x = gate_x + random.randint(0, gate_width)
                    sparkle_y = gate_y + random.randint(0, gate_height)
                    sparkle_size = random.randint(1, 3)
                    pygame.draw.circle(self.screen, WHITE, (sparkle_x, sparkle_y), sparkle_size)
            
            # Draw player
            self.player.draw(self.screen, self.camera)
            
            # Draw particles
            self.draw_particles()
            
            # Draw UI
            self.draw_ui()
            
            pygame.display.flip()
            self.clock.tick(FPS)
        
        pygame.quit()

def main():
    game = Game()
    game.run()

if __name__ == "__main__":
    main()
