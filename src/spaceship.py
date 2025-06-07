import pygame
import math
from src.input_handler import input_lock, shared_input_state
from src.bullet import Bullet

# Cores (definidas localmente ou importadas se forem globais)
WHITE = (255, 255, 255)

class Player(pygame.sprite.Sprite):
    def __init__(self, all_sprites_ref, bullets_group_ref, screen_width, screen_height):
        super().__init__()
        self.SCREEN_WIDTH = screen_width
        self.SCREEN_HEIGHT = screen_height
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
        self.rect.center = (self.SCREEN_WIDTH // 2, self.SCREEN_HEIGHT // 2)
        
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
            angle_rad = math.radians(self.angle)
            self.vx += self.thrust_power * math.sin(-angle_rad) 
            self.vy += self.thrust_power * -math.cos(-angle_rad)

        # Lida com o disparo
        if wants_to_shoot:
            bullet = self.shoot()
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
        if self.rect.left > self.SCREEN_WIDTH:
            self.rect.right = 0
        if self.rect.right < 0:
            self.rect.left = self.SCREEN_WIDTH
        if self.rect.top > self.SCREEN_HEIGHT:
            self.rect.bottom = 0
        if self.rect.bottom < 0:
            self.rect.top = self.SCREEN_HEIGHT

    def shoot(self):
        angle_rad = math.radians(self.angle)
        ship_length = self.original_image.get_height() / 2
        start_x = self.rect.centerx + ship_length * math.sin(-angle_rad)
        start_y = self.rect.centery + ship_length * -math.cos(-angle_rad)
        
        # Passa as dimensões da tela para o construtor do Projétil
        bullet = Bullet(start_x, start_y, self.angle, self.SCREEN_WIDTH, self.SCREEN_HEIGHT)
        return bullet
