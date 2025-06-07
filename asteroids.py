import pygame
import sys
import random
import math
import threading
from src.input_handler import input_queue, shared_input_state, input_lock, stop_input_thread_event, input_processing_thread_func
from src.game_entities import Asteroid as GameEntityAsteroid # Alias para evitar confusão se alguma variável local 'Asteroid' existir
from src.asteroid_manager import setup_initial_asteroids, spawn_periodic_asteroids, ASTEROID_SPAWN_RATE
from src.collision_handler import handle_bullet_asteroid_collisions, handle_player_asteroid_collisions
from src.bullet import Bullet
from src.spaceship import Player


# Inicializa o Pygame
pygame.init()

# Dimensões da tela (será configurado para tela cheia)
SCREEN_WIDTH = 0
SCREEN_HEIGHT = 0


# Cores
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
DARK_BLUE = (20, 20, 60) # Para o fundo espacial
RED = (255, 0, 0)
GREY = (128, 128, 128)

# Configura a tela para modo tela cheia
infoObject = pygame.display.Info() # Obtém informações da tela
SCREEN_WIDTH = infoObject.current_w
SCREEN_HEIGHT = infoObject.current_h
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.FULLSCREEN)
pygame.display.set_caption("Asteroides")

# Carrega a imagem de fundo
try:
    background_image = pygame.image.load('static/images/wllp.jpg').convert()
    background_image = pygame.transform.scale(background_image, (SCREEN_WIDTH, SCREEN_HEIGHT))
except pygame.error as e:
    print(f"Erro ao carregar imagem de fundo: {e}")
    background_image = None # Alternativa caso o carregamento da imagem falhe

# Semáforo de controle de asteroides
asteroid_semaphore = threading.Semaphore(15) # Acomoda os 8 asteroides iniciais e suas divisões

# Relógio do jogo
clock = pygame.time.Clock()
FPS = 60



# --- Variáveis do Jogo (a serem expandidas) ---
score = 0
game_paused = False
# asteroid_spawn_timer e ASTEROID_SPAWN_RATE estão agora em asteroid_manager.py

# --- Fonte para Pontuação ---
try:
    score_font = pygame.font.Font(None, 50) # Fonte padrão, tamanho 50
except Exception as e:
    print(f"Não foi possível carregar fonte padrão: {e}")
    score_font = pygame.font.SysFont('arial', 50) # Fonte do sistema alternativa

# --- Loop Principal do Jogo ---
def game_loop():
    running = True
    global score # Permite a modificação da pontuação global

    # Inicializa os grupos de sprites primeiro
    all_sprites = pygame.sprite.Group()
    asteroids_group = pygame.sprite.Group() # Asteroides atualmente desabilitados
    bullets_group = pygame.sprite.Group()

    # Cria instância do jogador, passando referências dos grupos de sprites e dimensões da tela
    player = Player(all_sprites, bullets_group, SCREEN_WIDTH, SCREEN_HEIGHT)
    all_sprites.add(player)

    # Inicia a thread de processamento de entrada
    input_thread = threading.Thread(target=input_processing_thread_func, daemon=True)
    input_thread.start()

    # Configura asteroides iniciais usando o gerenciador de asteroides
    setup_initial_asteroids(all_sprites, asteroids_group, asteroid_semaphore, SCREEN_WIDTH, SCREEN_HEIGHT)

    # Loop principal do jogo
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False # Sair do jogo com ESC
                elif event.key == pygame.K_p: # Placeholder para pausa
                    global game_paused
                    game_paused = not game_paused
                    print(f"Jogo pausado: {game_paused}")
                # Comandos de entrada do jogador para a fila
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
                # Sem KEYUP para shoot_request, pois é um evento único

        if not game_paused:
            # --- Lógica do Jogo (a ser adicionada) ---
            # Lógica de movimento das estrelas removida, pois agora usamos uma imagem de fundo estática
            
            # Atualiza todos os sprites (jogador, projéteis, asteroides)
            all_sprites.update() 
            # asteroids_group.update() é chamado implicitamente por all_sprites.update() se os asteroides estiverem em all_sprites

            # --- Detecção de Colisão (tratada por collision_handler.py) ---
            score = handle_bullet_asteroid_collisions(bullets_group, asteroids_group, score)
            if handle_player_asteroid_collisions(player, asteroids_group):
                running = False # Fim de jogo

            # --- Geração de Asteroides (tratada por asteroid_manager.py) ---
            spawn_periodic_asteroids(all_sprites, asteroids_group, asteroid_semaphore, SCREEN_WIDTH, SCREEN_HEIGHT)

        # --- Desenho ---
        screen.fill(BLACK) # Define o fundo como preto

        # Lógica de desenho das estrelas removida

        # Desenha todos os sprites (jogador e projéteis já estão em all_sprites)
        all_sprites.draw(screen) # Jogador e projéteis estão em all_sprites
        asteroids_group.draw(screen) # Desenha os asteroides explicitamente

        # Desenha a Pontuação
        score_text_surface = score_font.render(str(score), True, WHITE)
        score_text_rect = score_text_surface.get_rect(center=(SCREEN_WIDTH // 2, 50))
        screen.blit(score_text_surface, score_text_rect)

        # Desenha Botão de Pausa (placeholder)
        pause_button_margin = 20
        pause_button_size = 40
        pause_icon_line_length = 20
        pause_icon_line_width = 4
        pause_icon_spacing = 10

        pause_button_rect = pygame.Rect(SCREEN_WIDTH - pause_button_size - pause_button_margin, pause_button_margin, pause_button_size, pause_button_size)
        pygame.draw.rect(screen, GREY, pause_button_rect)
        # Ícone de pausa (duas linhas verticais)
        line1_x = SCREEN_WIDTH - pause_button_margin - (pause_button_size // 2) - (pause_icon_spacing // 2)
        line2_x = SCREEN_WIDTH - pause_button_margin - (pause_button_size // 2) + (pause_icon_spacing // 2)
        icon_y_start = pause_button_margin + (pause_button_size - pause_icon_line_length) // 2
        icon_y_end = icon_y_start + pause_icon_line_length

        pygame.draw.line(screen, WHITE, (line1_x, icon_y_start), (line1_x, icon_y_end), pause_icon_line_width)
        pygame.draw.line(screen, WHITE, (line2_x, icon_y_start), (line2_x, icon_y_end), pause_icon_line_width)

        if game_paused:
            # Exibe mensagem de Pausado
            pause_text_surface = score_font.render("PAUSADO", True, WHITE)
            pause_text_rect = pause_text_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
            screen.blit(pause_text_surface, pause_text_rect)

        pygame.display.flip() # Atualiza a tela

        clock.tick(FPS) # Limita a taxa de quadros

    # Sinaliza a thread de entrada para parar e espera até que ela termine
    print("Loop principal terminando. Sinalizando thread de entrada para parar.")
    stop_input_thread_event.set()
    input_queue.join() # Aguarda até que todos os itens na fila sejam processados
    input_thread.join()
    print("Thread de entrada unida. Saindo do jogo.")

    pygame.quit()
    sys.exit()

if __name__ == '__main__':
    game_loop()
