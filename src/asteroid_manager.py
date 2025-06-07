import pygame
import random
from src.game_entities import Asteroid as GameEntityAsteroid

# This would be passed from asteroids.py or defined here if constant
# For now, let's assume they are passed to functions.
# SCREEN_WIDTH, SCREEN_HEIGHT
# asteroid_semaphore
# all_sprites, asteroids_group

ASTEROID_SPAWN_RATE = 60 # Gera um novo asteroide (se houver espaço) a cada segundo a 60 FPS
asteroid_spawn_timer = 0

def setup_initial_asteroids(all_sprites, asteroids_group, asteroid_semaphore, screen_width, screen_height):
    """
    Generates the initial set of asteroids for the game.
    """
    initial_asteroids_config = [
        {'type': 'LG', 'count': 2},
        {'type': 'MD', 'count': 3},
        {'type': 'SM', 'count': 3}
    ]

    for config in initial_asteroids_config:
        for _ in range(config['count']):
            if asteroid_semaphore.acquire(blocking=False):
                start_x = random.randrange(0, screen_width)
                if random.choice([True, False]):
                    start_y = random.choice([-100, screen_height + 100])
                    start_x = random.randrange(0, screen_width)
                else:
                    start_x = random.choice([-100, screen_width + 100])
                    start_y = random.randrange(0, screen_height)
                
                new_asteroid = GameEntityAsteroid(position=(start_x, start_y), size_type=config['type'], 
                                                  all_sprites_ref=all_sprites, asteroids_group_ref=asteroids_group, 
                                                  asteroid_semaphore_ref=asteroid_semaphore, 
                                                  screen_width=screen_width, screen_height=screen_height)
                all_sprites.add(new_asteroid)
                asteroids_group.add(new_asteroid)
            else:
                print(f"Could not acquire semaphore for initial asteroid {config['type']}. Stopping initial generation.")
                break 
        else: 
            continue
        break

def spawn_periodic_asteroids(all_sprites, asteroids_group, asteroid_semaphore, screen_width, screen_height):
    """
    Periodically spawns new asteroids during gameplay.
    Manages its own timer.
    """
    global asteroid_spawn_timer
    asteroid_spawn_timer += 1
    if asteroid_spawn_timer >= ASTEROID_SPAWN_RATE:
        asteroid_spawn_timer = 0
        if asteroid_semaphore.acquire(blocking=False):
            new_asteroid_type = 'LG' # For now, only LG as per original code's testing state
            
            if random.choice([True, False]):
                start_y = random.choice([-100, screen_height + 100])
                start_x = random.randrange(0, screen_width)
            else:
                start_x = random.choice([-100, screen_width + 100])
                start_y = random.randrange(0, screen_height)
            
            new_asteroid = GameEntityAsteroid(position=(start_x, start_y), size_type=new_asteroid_type, 
                                              all_sprites_ref=all_sprites, asteroids_group_ref=asteroids_group, 
                                              asteroid_semaphore_ref=asteroid_semaphore, 
                                              screen_width=screen_width, screen_height=screen_height)
            all_sprites.add(new_asteroid)
            asteroids_group.add(new_asteroid)
        # else:
            # print("Semaphore full, no new periodic asteroid created.")
            # pass # Semaphore full
