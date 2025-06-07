import pygame

def handle_bullet_asteroid_collisions(bullets_group, asteroids_group, score_ref):
    """
    Handles collisions between bullets and asteroids.
    Updates the score.
    Returns the updated score.
    """
    # The first True removes bullets, False means asteroids are handled manually (e.g., for splitting)
    hit_dict = pygame.sprite.groupcollide(bullets_group, asteroids_group, True, False)
    
    current_score = score_ref # Use a local variable to accumulate score changes in this frame
    for bullet_hit, asteroids_hit_list in hit_dict.items():
        for asteroid_hit in asteroids_hit_list:
            if asteroid_hit.alive(): # Check if asteroid is still alive (not killed by another bullet in same frame)
                # Assuming asteroid_hit.properties['score'] exists from game_entities.Asteroid
                # If not, we might need to pass ASTEROID_SIZES or get score differently
                current_score += asteroid_hit.properties.get('score', 10) # Default score if not found
                asteroid_hit.kill_asteroid(spawn_children=True)
    return current_score

def handle_player_asteroid_collisions(player, asteroids_group):
    """
    Handles collisions between the player and asteroids.
    Returns True if the game should end, False otherwise.
    """
    if player.alive(): # Only check collision if player is alive
        if pygame.sprite.spritecollide(player, asteroids_group, False, pygame.sprite.collide_circle):
            print("\033[91mGAME OVER! JOGADOR ATINGIU UM ASTEROIDE!\033[0m")
            return True # Game should end
    return False # Game continues
