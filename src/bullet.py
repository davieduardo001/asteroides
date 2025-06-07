import pygame
import math

# Cores
WHITE = (255, 255, 255)

class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, angle, screen_width, screen_height):
        super().__init__()
        self.image = pygame.Surface([4, 10]) # Retângulo pequeno para o projétil
        self.image.fill(WHITE)
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.speed = 10
        
        # Salva as dimensões da tela para verificação de limites
        self.SCREEN_WIDTH = screen_width
        self.SCREEN_HEIGHT = screen_height

        # Comentários originais sobre rotação podem ser mantidos ou adaptados
        # A rotação do projétil pode ser implementada se desejado,
        # de forma similar à rotação do jogador, aplicada uma vez na criação.

        angle_rad = math.radians(angle)
        self.vx = self.speed * math.sin(-angle_rad) # sen(-ângulo) para dx
        self.vy = self.speed * -math.cos(-angle_rad) # -cos(-ângulo) para dy (Pygame Y aumenta para baixo)

    def update(self):
        self.rect.x += self.vx
        self.rect.y += self.vy

        # Remove o projétil se sair completamente da tela
        if (self.rect.right < 0 or self.rect.left > self.SCREEN_WIDTH or
            self.rect.bottom < 0 or self.rect.top > self.SCREEN_HEIGHT):
            self.kill()
