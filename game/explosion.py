# explosion.py
import pygame

class Explosion:
    def __init__(self, x, y):
        self.original_image = pygame.image.load("../assets/images/explosion.png")
        self.image = pygame.transform.scale(self.original_image, (64, 64))
        self.rect = self.image.get_rect(center=(x, y))
        self.timer = 15  # 爆炸持续帧数

    def update(self):
        self.timer -= 1

    def draw(self, screen):
        screen.blit(self.image, self.rect)

    def is_finished(self):
        return self.timer <= 0
