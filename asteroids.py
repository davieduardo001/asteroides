import pygame
import sys
import random
import math
import threading
from src.input_handler import input_queue, shared_input_state, input_lock, stop_input_thread_event, input_processing_thread_func
from src.game_entities import Asteroid as GameEntityAsteroid # Alias para evitar confusão se alguma variável local 'Asteroid' existir


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

# --- Classe do Jogador ---
class Player(pygame.sprite.Sprite):
    def __init__(self, all_sprites_ref, bullets_group_ref):
        super().__init__()
        try:
            loaded_image = pygame.image.load('static/images/spaceship.png').convert_alpha()
            desired_width = 65 # Tamanho aumentado
            desired_height = 78 # Tamanho aumentado
            self.original_image = pygame.transform.scale(loaded_image, (desired_width, desired_height))
        except pygame.error as e:
            print(f"Erro ao carregar imagem do jogador: {e}. Usando forma alternativa.")
            self.original_image = pygame.Surface([52, 65], pygame.SRCALPHA) # Tamanho alternativo ajustado
            pygame.draw.polygon(self.original_image, WHITE, [(26, 0), (0, 65), (52, 65)]) # Forma alternativa ajustada
        
        self.image = self.original_image.copy()
        self.rect = self.image.get_rect()
        self.rect.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
        
        self.angle = 0  # 0 graus aponta para CIMA, rotação positiva é anti-horária
        self.rotation_speed = 4.5
        self.thrust_power = 0.25
        self.vx = 0.0
        self.vy = 0.0
        self.max_speed = 6.0
        self.drag = 0.99 # Valor maior = menos arrasto
        self.last_shot_time = 0 # Para controle potencial da cadência de tiro
        self.shoot_delay = 250 # Milissegundos entre disparos (opcional, pode ser ajustado)

        self.all_sprites_ref = all_sprites_ref
        self.bullets_group_ref = bullets_group_ref

    def update(self):
        # Lê o estado de entrada compartilhado
        with input_lock:
            is_rotating_left = shared_input_state['rotate_left']
            is_rotating_right = shared_input_state['rotate_right']
            is_thrusting = shared_input_state['thrust_on']
            wants_to_shoot = shared_input_state['shoot_request']
            if wants_to_shoot:
                shared_input_state['shoot_request'] = False # Reseta a solicitação
        
        # Rotação
        if is_rotating_left:
            self.angle += self.rotation_speed
        if is_rotating_right:
            self.angle -= self.rotation_speed
        self.angle %= 360 # Mantém o ângulo entre 0 e 360

        # Rotaciona a imagem
        self.image = pygame.transform.rotate(self.original_image, self.angle)
        self.rect = self.image.get_rect(center=self.rect.center) # Atualiza o centro do rect após a rotação

        # Propulsão
        if is_thrusting:
            # Ângulo 0 é CIMA. Ângulo positivo rotaciona anti-horário.
            # Componentes do vetor de propulsão:
            # dx = sin(-angulo_rad), dy = -cos(-angulo_rad)
            angle_rad = math.radians(self.angle)
            self.vx += self.thrust_power * math.sin(-angle_rad) 
            self.vy += self.thrust_power * -math.cos(-angle_rad)

        # Lida com o disparo
        if wants_to_shoot:
            bullet = self.shoot() # método shoot já existe
            if bullet:
                self.all_sprites_ref.add(bullet)
                self.bullets_group_ref.add(bullet)
            
        # Aplica arrasto
        self.vx *= self.drag
        self.vy *= self.drag

        # Limita a velocidade
        current_speed_sq = self.vx**2 + self.vy**2
        if current_speed_sq > self.max_speed**2:
            scale = self.max_speed / math.sqrt(current_speed_sq) if current_speed_sq > 0 else 0
            self.vx *= scale
            self.vy *= scale

        # Atualiza a posição
        self.rect.x += self.vx
        self.rect.y += self.vy

        # Jogador atravessa a tela (screen wrapping)
        if self.rect.left > SCREEN_WIDTH:
            self.rect.right = 0
        if self.rect.right < 0:
            self.rect.left = SCREEN_WIDTH
        if self.rect.top > SCREEN_HEIGHT:
            self.rect.bottom = 0
        if self.rect.bottom < 0:
            self.rect.top = SCREEN_HEIGHT

    def shoot(self):
        # Opcional: Implementar um limite de cadência de tiro
        # current_time = pygame.time.get_ticks()
        # if current_time - self.last_shot_time > self.shoot_delay:
        #     self.last_shot_time = current_time
        angle_rad = math.radians(self.angle)
        # Calcula a posição inicial do projétil (ponta da nave)
        # Deslocamento do centro para a ponta da nave (aprox. metade da altura da nave)
        # Assumindo que a altura da original_image é uma boa aproximação para o comprimento da nave
        ship_length = self.original_image.get_height() / 2
        start_x = self.rect.centerx + ship_length * math.sin(-angle_rad)
        start_y = self.rect.centery + ship_length * -math.cos(-angle_rad)
        
        bullet = Bullet(start_x, start_y, self.angle)
        return bullet
        # return None # Se o limite de cadência de tiro estiver ativo e não for atendido

# --- Classe do Projétil ---
class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, angle):
        super().__init__()
        self.image = pygame.Surface([4, 10]) # Retângulo pequeno para o projétil
        self.image.fill(WHITE)
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.speed = 10
        
        # Rotaciona a imagem do projétil para corresponder ao ângulo de disparo (opcional, um retângulo simples pode ser suficiente)
        # Por simplicidade, manteremos o projétil como um retângulo não rotacionado por enquanto.
        # Se a rotação for desejada, é semelhante à rotação do jogador, mas feita uma vez na criação.

        angle_rad = math.radians(angle)
        self.vx = self.speed * math.sin(-angle_rad)
        self.vy = self.speed * -math.cos(-angle_rad)

    def update(self):
        self.rect.x += self.vx
        self.rect.y += self.vy

        # Remove o projétil se sair da tela
        if not screen.get_rect().colliderect(self.rect):
            self.kill()

# --- Variáveis do Jogo (a serem expandidas) ---
score = 0
game_paused = False
asteroid_spawn_timer = 0
ASTEROID_SPAWN_RATE = 60 # Gera um novo asteroide (se houver espaço) a cada segundo a 60 FPS



# --- Fonte para Pontuação ---
try:
    score_font = pygame.font.Font(None, 50) # Fonte padrão, tamanho 50
except Exception as e:
    print(f"Não foi possível carregar fonte padrão: {e}")
    score_font = pygame.font.SysFont('arial', 50) # Fonte do sistema alternativa

# --- Loop Principal do Jogo ---
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

    # Geração inicial de asteroides - Fase 1: 2 LG, 3 MD, 3 SM
    initial_asteroids_config = [
        {'type': 'LG', 'count': 2},
        {'type': 'MD', 'count': 3},
        {'type': 'SM', 'count': 3}
    ]

    for config in initial_asteroids_config:
        for _ in range(config['count']):
            if asteroid_semaphore.acquire(blocking=False):
                start_x = random.randrange(0, SCREEN_WIDTH)
                # Garante que os asteroides surjam fora da tela ou nas bordas, variando y para diversidade
                if random.choice([True, False]): # Surge de cima/baixo ou esquerda/direita
                    # Surgimento de cima/baixo
                    start_y = random.choice([-100, SCREEN_HEIGHT + 100])
                    start_x = random.randrange(0, SCREEN_WIDTH)
                else:
                    # Surgimento da esquerda/direita
                    start_x = random.choice([-100, SCREEN_WIDTH + 100])
                    start_y = random.randrange(0, SCREEN_HEIGHT)
                
                new_asteroid = GameEntityAsteroid(position=(start_x, start_y), size_type=config['type'], 
                                                  all_sprites_ref=all_sprites, asteroids_group_ref=asteroids_group, 
                                                  asteroid_semaphore_ref=asteroid_semaphore, 
                                                  screen_width=SCREEN_WIDTH, screen_height=SCREEN_HEIGHT)
                all_sprites.add(new_asteroid)
                asteroids_group.add(new_asteroid)
                # print(f"Asteroide {config['type']} inicial criado. Contagem do semáforo: {asteroid_semaphore._value if hasattr(asteroid_semaphore, '_value') else 'N/A'}")
            else:
                print(f"Não foi possível adquirir semáforo para asteroide {config['type']} inicial. Parando geração inicial.")
                break # Para este tipo se o semáforo esgotar
        else: # Continua para o próximo tipo apenas se o loop interno completar sem interrupção
            continue
        break # Interrompe o loop externo se o loop interno foi interrompidoly unavailable



    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False # Sair do jogo com ESC
                elif event.key == pygame.K_p: # Placeholder for pause
                    global game_paused
                    game_paused = not game_paused
                    print(f"Jogo pausado: {game_paused}")
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
            # --- Lógica do Jogo (to be added) ---
            # Lógica de movimento das estrelas removida, pois agora usamos uma imagem de fundo estática
            
            # Atualiza todos os sprites (jogador, projéteis, asteroides)
            all_sprites.update() 
            # asteroids_group.update() é chamado implicitamente por all_sprites.update() se os asteroides estiverem em all_sprites

            # --- Detecção de Colisão ---
            # Colisões Projétil-Asteroide
            # O primeiro True remove projéteis, o False significa que asteroides são tratados manualmente
            # hit_dict terá: {projetil_que_acertou: [lista_de_asteroides_que_acertou]}
            hit_dict = pygame.sprite.groupcollide(bullets_group, asteroids_group, True, False) 
            
            for bullet_that_hit, asteroids_collided_with_this_bullet in hit_dict.items():
                for asteroid_hit in asteroids_collided_with_this_bullet:
                    if asteroid_hit.alive(): # Verifica se o asteroide não foi destruído por outro projétil no mesmo frame
                        score += asteroid_hit.properties['score'] 
                        asteroid_hit.kill_asteroid(spawn_children=True) 
                        # print(f"Pontuação: {score}") # Debug da pontuação

            # Colisões Jogador-Asteroide (Espaço reservado para depois)
            # if pygame.sprite.spritecollide(player, asteroids_group, False, pygame.sprite.collide_circle):
            #     print("Jogador atingiu um asteroide!")
            #     # running = False # Exemplo: fim de jogo

            # Gera novos asteroides periodicamente
            global asteroid_spawn_timer
            asteroid_spawn_timer += 1
            if asteroid_spawn_timer >= ASTEROID_SPAWN_RATE:
                asteroid_spawn_timer = 0
                if asteroid_semaphore.acquire(blocking=False):
                    start_x = random.choice([random.randrange(-100, -50), random.randrange(SCREEN_WIDTH + 50, SCREEN_WIDTH + 100)])
                    start_y = random.randrange(0, SCREEN_HEIGHT)
                    # Escolhe aleatoriamente um lado para surgir (cima, baixo, esquerda, direita)
                    # start_x = random.randrange(0, SCREEN_WIDTH)
                    # start_y = random.choice([random.randrange(-100, -50), random.randrange(SCREEN_HEIGHT + 50, SCREEN_HEIGHT + 100)])
                    
                    new_asteroid = GameEntityAsteroid(position=(start_x, start_y), size_type='LG', 
                                                      all_sprites_ref=all_sprites, asteroids_group_ref=asteroids_group, 
                                                      asteroid_semaphore_ref=asteroid_semaphore, 
                                                      screen_width=SCREEN_WIDTH, screen_height=SCREEN_HEIGHT)
                    all_sprites.add(new_asteroid)
                    asteroids_group.add(new_asteroid)
                    # print(f"Asteroide periódico criado. Contagem do semáforo: {asteroid_semaphore._value}") # Debug
                # else:
                    # print(f"Máximo de asteroides (LG) alcançado, não gerando. Contagem do semáforo: {asteroid_semaphore._value}") # Debug


        # --- Desenho ---
        screen.fill(BLACK) # Set background to black
        # if background_image:
        #     screen.blit(background_image, (0,0))
        # else:
        #     screen.fill(DARK_BLUE) # Fallback background color

        # Lógica de desenho das estrelas removida

        # Desenha todos os sprites (jogador)
        all_sprites.draw(screen) # Jogador está em all_sprites
        # asteroids_group.draw(screen) # Desenho dos asteroides desativado



        # Desenha a Pontuação
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
