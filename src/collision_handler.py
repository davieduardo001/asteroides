import pygame

def handle_bullet_asteroid_collisions(bullets_group, asteroids_group, score_ref):
    """
    Lida com colisões entre projéteis e asteroides.
    Atualiza a pontuação.
    Retorna a pontuação atualizada.
    """
    # O primeiro True remove os projéteis, False significa que os asteroides são tratados manualmente (ex: para divisão)
    hit_dict = pygame.sprite.groupcollide(bullets_group, asteroids_group, True, False)
    
    current_score = score_ref # Usa uma variável local para acumular alterações de pontuação neste quadro
    for bullet_hit, asteroids_hit_list in hit_dict.items():
        for asteroid_hit in asteroids_hit_list:
            if asteroid_hit.alive(): # Verifica se o asteroide ainda está vivo (não foi destruído por outro projétil no mesmo quadro)
                # Assumindo que asteroid_hit.properties['score'] existe em game_entities.Asteroid
                # Caso contrário, podemos precisar passar ASTEROID_SIZES ou obter a pontuação de forma diferente
                current_score += asteroid_hit.properties.get('score', 10) # Pontuação padrão se não encontrada
                asteroid_hit.kill_asteroid(spawn_children=True)
    return current_score

def handle_player_asteroid_collisions(player, asteroids_group):
    """
    Lida com colisões entre o jogador e asteroides.
    Retorna True se o jogo deve terminar, False caso contrário.
    """
    if player.alive(): # Só verifica a colisão se o jogador estiver vivo
        if pygame.sprite.spritecollide(player, asteroids_group, False, pygame.sprite.collide_circle):
            print("\033[91mGAME OVER! JOGADOR ATINGIU UM ASTEROIDE!\033[0m")
            return True # O jogo deve terminar
    return False # O jogo continua
