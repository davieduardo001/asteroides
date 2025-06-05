import pygame
import sys
import random
import math
import threading
import queue # Keep queue for now, might be needed by other parts if game expands
from src.input_handler import input_queue, shared_input_state, input_lock, stop_input_thread_event, input_processing_thread_func
from src.game_entities import Asteroid as GameEntityAsteroid # Alias to avoid confusion if any local 'Asteroid' var exists


# Initialize Pygame
pygame.init()

# Screen dimensions (will be set to full screen)
SCREEN_WIDTH = 0
SCREEN_HEIGHT = 0


# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
DARK_BLUE = (20, 20, 60) # For the space background
RED = (255, 0, 0)
GREY = (128, 128, 128)

# Set up the display for full screen
infoObject = pygame.display.Info() # Get display info
SCREEN_WIDTH = infoObject.current_w
SCREEN_HEIGHT = infoObject.current_h
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.FULLSCREEN)
pygame.display.set_caption("Asteroides")

# Load background image
try:
    background_image = pygame.image.load('static/images/wllp.jpg').convert()
    background_image = pygame.transform.scale(background_image, (SCREEN_WIDTH, SCREEN_HEIGHT))
except pygame.error as e:
    print(f"Error loading background image: {e}")
    background_image = None # Fallback if image loading fails

# Asteroid control semaphore
asteroid_semaphore = threading.Semaphore(4)

# Game clock
clock = pygame.time.Clock()
FPS = 60

# --- Player Class ---
class Player(pygame.sprite.Sprite):
    def __init__(self, all_sprites_ref, bullets_group_ref):
        super().__init__()
        try:
            loaded_image = pygame.image.load('static/images/spaceship.png').convert_alpha()
            desired_width = 65 # Increased size
            desired_height = 78 # Increased size
            self.original_image = pygame.transform.scale(loaded_image, (desired_width, desired_height))
        except pygame.error as e:
            print(f"Error loading player image: {e}. Using fallback shape.")
            self.original_image = pygame.Surface([52, 65], pygame.SRCALPHA) # Adjusted fallback size
            pygame.draw.polygon(self.original_image, WHITE, [(26, 0), (0, 65), (52, 65)]) # Adjusted fallback shape
        
        self.image = self.original_image.copy()
        self.rect = self.image.get_rect()
        self.rect.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
        
        self.angle = 0  # 0 degrees is pointing UP, positive is CCW rotation
        self.rotation_speed = 4.5
        self.thrust_power = 0.25
        self.vx = 0.0
        self.vy = 0.0
        self.max_speed = 6.0
        self.drag = 0.99 # Higher value = less drag
        self.last_shot_time = 0 # For potential fire rate control
        self.shoot_delay = 250 # Milliseconds between shots (optional, can be adjusted)

        self.all_sprites_ref = all_sprites_ref
        self.bullets_group_ref = bullets_group_ref

    def update(self):
        # Read shared input state
        with input_lock:
            is_rotating_left = shared_input_state['rotate_left']
            is_rotating_right = shared_input_state['rotate_right']
            is_thrusting = shared_input_state['thrust_on']
            wants_to_shoot = shared_input_state['shoot_request']
            if wants_to_shoot:
                shared_input_state['shoot_request'] = False # Reset the request
        
        # Rotation
        if is_rotating_left:
            self.angle += self.rotation_speed
        if is_rotating_right:
            self.angle -= self.rotation_speed
        self.angle %= 360 # Keep angle between 0 and 360

        # Rotate image
        self.image = pygame.transform.rotate(self.original_image, self.angle)
        self.rect = self.image.get_rect(center=self.rect.center) # Update rect center after rotation

        # Thrust
        if is_thrusting:
            # Angle 0 is UP. Positive angle rotates CCW.
            # Thrust vector components:
            # dx = sin(-angle_rad), dy = -cos(-angle_rad)
            angle_rad = math.radians(self.angle)
            self.vx += self.thrust_power * math.sin(-angle_rad) 
            self.vy += self.thrust_power * -math.cos(-angle_rad)

        # Handle shooting
        if wants_to_shoot:
            bullet = self.shoot() # shoot method already exists
            if bullet:
                self.all_sprites_ref.add(bullet)
                self.bullets_group_ref.add(bullet)
            
        # Apply drag
        self.vx *= self.drag
        self.vy *= self.drag

        # Limit speed
        current_speed_sq = self.vx**2 + self.vy**2
        if current_speed_sq > self.max_speed**2:
            scale = self.max_speed / math.sqrt(current_speed_sq) if current_speed_sq > 0 else 0
            self.vx *= scale
            self.vy *= scale

        # Update position
        self.rect.x += self.vx
        self.rect.y += self.vy

        # Player screen wrapping
        if self.rect.left > SCREEN_WIDTH:
            self.rect.right = 0
        if self.rect.right < 0:
            self.rect.left = SCREEN_WIDTH
        if self.rect.top > SCREEN_HEIGHT:
            self.rect.bottom = 0
        if self.rect.bottom < 0:
            self.rect.top = SCREEN_HEIGHT

    def shoot(self):
        # Optional: Implement a fire rate limit
        # current_time = pygame.time.get_ticks()
        # if current_time - self.last_shot_time > self.shoot_delay:
        #     self.last_shot_time = current_time
        angle_rad = math.radians(self.angle)
        # Calculate bullet starting position (tip of the spaceship)
        # Offset from center to the tip of the ship (approx. half the ship's height)
        # Assuming original_image height is a good proxy for ship length
        ship_length = self.original_image.get_height() / 2
        start_x = self.rect.centerx + ship_length * math.sin(-angle_rad)
        start_y = self.rect.centery + ship_length * -math.cos(-angle_rad)
        
        bullet = Bullet(start_x, start_y, self.angle)
        return bullet
        # return None # If fire rate limit is active and not met

# --- Bullet Class ---
class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, angle):
        super().__init__()
        self.image = pygame.Surface([4, 10]) # Small rectangle for bullet
        self.image.fill(WHITE)
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.speed = 10
        
        # Rotate bullet image to match firing angle (optional, simple rect might be fine)
        # For simplicity, we'll keep the bullet as a non-rotated rectangle for now.
        # If rotation is desired, it's similar to player rotation but done once at creation.

        angle_rad = math.radians(angle)
        self.vx = self.speed * math.sin(-angle_rad)
        self.vy = self.speed * -math.cos(-angle_rad)

    def update(self):
        self.rect.x += self.vx
        self.rect.y += self.vy

        # Remove bullet if it goes off screen
        if not screen.get_rect().colliderect(self.rect):
            self.kill()

# --- Game Variables (to be expanded) ---
score = 0
game_paused = False
asteroid_spawn_timer = 0
ASTEROID_SPAWN_RATE = 60 # Spawn a new asteroid (if space available) every second at 60 FPS



# --- Font for Score ---
try:
    score_font = pygame.font.Font(None, 50) # Default font, size 50
except Exception as e:
    print(f"Could not load default font: {e}")
    score_font = pygame.font.SysFont('arial', 50) # Fallback system font

# --- Game Loop ---
def game_loop():
    running = True
    global score # Allow modification of global score

    # Initialize sprite groups first
    all_sprites = pygame.sprite.Group()
    asteroids_group = pygame.sprite.Group() # Asteroids currently disabled
    bullets_group = pygame.sprite.Group()

    # Create player instance, passing sprite group references
    player = Player(all_sprites, bullets_group)
    all_sprites.add(player)

    # Start the input processing thread
    input_thread = threading.Thread(target=input_processing_thread_func, daemon=True)
    input_thread.start()

    # Initial asteroid spawning - using new GameEntityAsteroid
    for _ in range(4):
        if asteroid_semaphore.acquire(blocking=False):
            start_x = random.randrange(0, SCREEN_WIDTH)
            start_y = random.randrange(-150, -50) # Start above screen
            new_asteroid = GameEntityAsteroid(position=(start_x, start_y), size_type='LG', 
                                              all_sprites_ref=all_sprites, asteroids_group_ref=asteroids_group, 
                                              asteroid_semaphore_ref=asteroid_semaphore, 
                                              screen_width=SCREEN_WIDTH, screen_height=SCREEN_HEIGHT)
            all_sprites.add(new_asteroid)
            asteroids_group.add(new_asteroid)
            # print(f"Initial LG asteroid spawned. Semaphore count: {asteroid_semaphore._value}") # Debug
        else:
            print("Error: Could not acquire semaphore for initial LG asteroid spawn.")
            break # Stop trying if semaphore is unexpectedly unavailable



    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False # Quit on ESC
                elif event.key == pygame.K_p: # Placeholder for pause
                    global game_paused
                    game_paused = not game_paused
                    print(f"Game Paused: {game_paused}")
                # Player input commands to queue
                elif event.key == pygame.K_LEFT:
                    input_queue.put(('rotate_left', True))
                elif event.key == pygame.K_RIGHT:
                    input_queue.put(('rotate_right', True))
                elif event.key == pygame.K_UP:
                    input_queue.put(('thrust_on', True))
                elif event.key == pygame.K_SPACE:
                    input_queue.put(('shoot_request', True))
            
            elif event.type == pygame.KEYUP:
                if event.key == pygame.K_LEFT:
                    input_queue.put(('rotate_left', False))
                elif event.key == pygame.K_RIGHT:
                    input_queue.put(('rotate_right', False))
                elif event.key == pygame.K_UP:
                    input_queue.put(('thrust_on', False))
                # No KEYUP for shoot_request as it's a single event

        if not game_paused:
            # --- Game Logic (to be added) ---
            # Star movement logic removed as we are using a static background image now
            
            # Update all sprites (player, bullets, asteroids)
            all_sprites.update() 
            # asteroids_group.update() is implicitly called by all_sprites.update() if asteroids are in all_sprites

            # Spawn new asteroids periodically
            global asteroid_spawn_timer
            asteroid_spawn_timer += 1
            if asteroid_spawn_timer >= ASTEROID_SPAWN_RATE:
                asteroid_spawn_timer = 0
                if asteroid_semaphore.acquire(blocking=False):
                    start_x = random.choice([random.randrange(-100, -50), random.randrange(SCREEN_WIDTH + 50, SCREEN_WIDTH + 100)])
                    start_y = random.randrange(0, SCREEN_HEIGHT)
                    # Alternate starting from top/bottom if preferred for periodic spawns
                    # start_x = random.randrange(0, SCREEN_WIDTH)
                    # start_y = random.choice([random.randrange(-100, -50), random.randrange(SCREEN_HEIGHT + 50, SCREEN_HEIGHT + 100)])
                    
                    new_asteroid = GameEntityAsteroid(position=(start_x, start_y), size_type='LG', 
                                                      all_sprites_ref=all_sprites, asteroids_group_ref=asteroids_group, 
                                                      asteroid_semaphore_ref=asteroid_semaphore, 
                                                      screen_width=SCREEN_WIDTH, screen_height=SCREEN_HEIGHT)
                    all_sprites.add(new_asteroid)
                    asteroids_group.add(new_asteroid)
                    # print(f"Periodic LG asteroid spawned. Semaphore count: {asteroid_semaphore._value}") # Debug
                # else:
                    # print(f"Max asteroids (LG) reached, not spawning. Semaphore count: {asteroid_semaphore._value}") # Debug


        # --- Drawing ---
        screen.fill(BLACK) # Set background to black
        # if background_image:
        #     screen.blit(background_image, (0,0))
        # else:
        #     screen.fill(DARK_BLUE) # Fallback background color

        # Star drawing logic removed

        # Draw all sprites (player)
        all_sprites.draw(screen) # Player is in all_sprites
        # asteroids_group.draw(screen) # Asteroid drawing disabled



        # Draw score
        score_text_surface = score_font.render(str(score), True, WHITE)
        score_text_rect = score_text_surface.get_rect(center=(SCREEN_WIDTH // 2, 50))
        screen.blit(score_text_surface, score_text_rect)

        # Draw Pause Button (placeholder)
        pause_button_margin = 20
        pause_button_size = 40
        pause_icon_line_length = 20
        pause_icon_line_width = 4
        pause_icon_spacing = 10

        pause_button_rect = pygame.Rect(SCREEN_WIDTH - pause_button_size - pause_button_margin, pause_button_margin, pause_button_size, pause_button_size)
        pygame.draw.rect(screen, GREY, pause_button_rect)
        # Pause icon (two vertical lines)
        line1_x = SCREEN_WIDTH - pause_button_margin - (pause_button_size // 2) - (pause_icon_spacing // 2)
        line2_x = SCREEN_WIDTH - pause_button_margin - (pause_button_size // 2) + (pause_icon_spacing // 2)
        icon_y_start = pause_button_margin + (pause_button_size - pause_icon_line_length) // 2
        icon_y_end = icon_y_start + pause_icon_line_length

        pygame.draw.line(screen, WHITE, (line1_x, icon_y_start), (line1_x, icon_y_end), pause_icon_line_width)
        pygame.draw.line(screen, WHITE, (line2_x, icon_y_start), (line2_x, icon_y_end), pause_icon_line_width)


        if game_paused:
            # Display Paused message
            pause_text_surface = score_font.render("PAUSED", True, WHITE)
            pause_text_rect = pause_text_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
            screen.blit(pause_text_surface, pause_text_rect)

        pygame.display.flip() # Update the full screen

        clock.tick(FPS) # Cap the frame rate

    # Signal the input thread to stop and wait for it to finish
    print("Main loop ending. Signaling input thread to stop.")
    stop_input_thread_event.set()
    input_queue.join() # Wait for all items in the queue to be processed
    input_thread.join()
    print("Input thread joined. Exiting game.")

    pygame.quit()
    sys.exit()

if __name__ == '__main__':
    game_loop()
