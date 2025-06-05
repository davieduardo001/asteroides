import pygame
import random
import math

# Define asteroid sizes and their properties
ASTEROID_SIZES = {
    'LG': {'scale': 0.2, 'score': 20, 'speed_multiplier': 1.0, 'radius': 10},
    'MD': {'scale': 0.1, 'score': 50, 'speed_multiplier': 1.3, 'radius': 5},
    'SM': {'scale': 0.06, 'score': 100, 'speed_multiplier': 1.6, 'radius': 3}
}

# Global variable to store the loaded asteroid image to avoid reloading
_asteroid_original_image = None

def load_asteroid_image():
    global _asteroid_original_image
    if _asteroid_original_image is None:
        try:
            _asteroid_original_image = pygame.image.load('static/images/asteroid.png').convert_alpha()
        except pygame.error as e:
            print(f"Error loading asteroid image: {e}")
            # Create a fallback circular surface if image fails to load
            _asteroid_original_image = pygame.Surface((100, 100), pygame.SRCALPHA)
            pygame.draw.circle(_asteroid_original_image, (128, 128, 128), (50, 50), 50)
    return _asteroid_original_image

class Asteroid(pygame.sprite.Sprite):
    def __init__(self, position, size_type, all_sprites_ref, asteroids_group_ref, asteroid_semaphore_ref, screen_width, screen_height):
        super().__init__()
        
        self.size_type = size_type
        self.properties = ASTEROID_SIZES[size_type]
        self.original_image = load_asteroid_image() # Load base image (or get from cache)
        
        # Scale image
        scaled_width = int(self.original_image.get_width() * self.properties['scale'])
        scaled_height = int(self.original_image.get_height() * self.properties['scale'])
        self.base_image = pygame.transform.scale(self.original_image, (scaled_width, scaled_height)) # Store the scaled image before rotation
        self.image = self.base_image.copy() # Initial image is a copy of the base image
        self.rect = self.image.get_rect(center=position)
        self.radius = self.properties['radius'] # For collision detection

        # Rotation attributes
        self.angle = random.uniform(0, 360) # Visual rotation angle
        self.rotation_speed = random.uniform(-2.5, 2.5) # Degrees per frame
        while -0.5 < self.rotation_speed < 0.5: # Ensure it's not too slow or static
            self.rotation_speed = random.uniform(-2.5, 2.5)

        # Movement
        movement_angle_deg = random.uniform(0, 360) # Angle for initial movement direction
        movement_angle_rad = math.radians(movement_angle_deg)
        base_speed = random.uniform(1, 2.5) * self.properties['speed_multiplier']
        self.vx = base_speed * math.cos(movement_angle_rad)
        self.vy = base_speed * math.sin(movement_angle_rad)
        
        self.all_sprites_ref = all_sprites_ref
        self.asteroids_group_ref = asteroids_group_ref
        self.asteroid_semaphore_ref = asteroid_semaphore_ref
        self.SCREEN_WIDTH = screen_width
        self.SCREEN_HEIGHT = screen_height

    def update(self):
        # Rotation
        self.angle = (self.angle + self.rotation_speed) % 360
        self.image = pygame.transform.rotate(self.base_image, self.angle)
        self.rect = self.image.get_rect(center=self.rect.center)

        # Movement
        self.rect.x += self.vx
        self.rect.y += self.vy

        # Screen wrapping (simple version for now)
        if self.rect.left > self.SCREEN_WIDTH:
            self.rect.right = 0
        elif self.rect.right < 0:
            self.rect.left = self.SCREEN_WIDTH
        
        if self.rect.top > self.SCREEN_HEIGHT:
            # Instead of wrapping, if it goes off bottom, it should be destroyed and release semaphore
            self.kill_asteroid(spawn_children=False)
        elif self.rect.bottom < 0:
            # If it goes off top, also destroy and release (less common with initial spawn)
            self.kill_asteroid(spawn_children=False)

    def kill_asteroid(self, spawn_children=True):
        # Placeholder for breaking into smaller asteroids
        if spawn_children:
            if self.size_type == 'LG':
                self._spawn_children('MD', 2) # Spawn 2 medium asteroids
            elif self.size_type == 'MD':
                self._spawn_children('SM', 2) # Spawn 2 small asteroids
        
        self.kill() # Remove from sprite groups
        self.asteroid_semaphore_ref.release()
        # print(f"Asteroid ({self.size_type}) killed. Semaphore released. Count: {self.asteroid_semaphore_ref._value}")

    def _spawn_children(self, child_size_type, count):
        for _ in range(count):
            if self.asteroid_semaphore_ref.acquire(blocking=False):
                new_pos = (self.rect.centerx + random.randint(-10,10), self.rect.centery + random.randint(-10,10))
                child_asteroid = Asteroid(new_pos, child_size_type, 
                                          self.all_sprites_ref, self.asteroids_group_ref, 
                                          self.asteroid_semaphore_ref, self.SCREEN_WIDTH, self.SCREEN_HEIGHT)
                self.all_sprites_ref.add(child_asteroid)
                self.asteroids_group_ref.add(child_asteroid)
            else:
                # print(f"Could not acquire semaphore for child asteroid ({child_size_type})")
                break # Stop trying to spawn more children if semaphore limit is hit

# Example of how you might call this (for testing, not for final game loop)
if __name__ == '__main__':
    pygame.init()
    screen_width_test, screen_height_test = 800, 600
    screen = pygame.display.set_mode((screen_width_test, screen_height_test))
    pygame.display.set_caption("Game Entities Test")
    
    all_sprites = pygame.sprite.Group()
    asteroids = pygame.sprite.Group()
    # Dummy semaphore for testing
    import threading
    test_semaphore = threading.Semaphore(10) 

    # Try loading the image
    img = load_asteroid_image()
    if img:
        print("Asteroid image loaded successfully for testing.")

    # Create a large asteroid
    if test_semaphore.acquire(blocking=False):
        asteroid_lg = Asteroid((screen_width_test // 2, screen_height_test // 2), 'LG', all_sprites, asteroids, test_semaphore, screen_width_test, screen_height_test)
        all_sprites.add(asteroid_lg)
        asteroids.add(asteroid_lg)
    
    running = True
    clock = pygame.time.Clock()
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        
        all_sprites.update()
        
        screen.fill((0,0,0))
        all_sprites.draw(screen)
        pygame.display.flip()
        
        clock.tick(60)
    pygame.quit()
