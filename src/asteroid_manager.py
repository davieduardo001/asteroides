import pygame
import random
from src.game_entities import Asteroid as GameEntityAsteroid

# Isso seria passado de asteroids.py ou definido aqui se fosse constante
# Por enquanto, vamos assumir que são passados para as funções.
# SCREEN_WIDTH, SCREEN_HEIGHT
# asteroid_semaphore
# all_sprites, asteroids_group

ASTEROID_SPAWN_RATE = 60 # Gera um novo asteroide (se houver espaço) a cada segundo a 60 FPS
asteroid_spawn_timer = 0

def setup_initial_asteroids(all_sprites, asteroids_group, asteroid_semaphore, screen_width, screen_height):
    """
    Gera o conjunto inicial de asteroides para o jogo.
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
                print(f"Não foi possível adquirir o semáforo para o asteroide inicial {config['type']}. Interrompendo a geração inicial.")
                break 
        else: 
            continue
        break

def spawn_periodic_asteroids(all_sprites, asteroids_group, asteroid_semaphore, screen_width, screen_height):
    """
    Gera periodicamente novos asteroides durante o jogo.
    Gerencia seu próprio temporizador.
    """
    global asteroid_spawn_timer
    asteroid_spawn_timer += 1
    if asteroid_spawn_timer >= ASTEROID_SPAWN_RATE:
        asteroid_spawn_timer = 0
        if asteroid_semaphore.acquire(blocking=False):
            new_asteroid_type = 'LG' # Por enquanto, apenas LG conforme o estado de teste do código original
            
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
        # senão:
            # print("Semáforo cheio, nenhum novo asteroide periódico criado.")
            # pass # Semáforo cheio
