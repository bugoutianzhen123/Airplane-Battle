import pygame

class Bullet:
    def __init__(self, x, y, speed=8):
        self.image = pygame.Surface((5, 15))  # 简单的矩形子弹
        self.image.fill((255, 255, 0))  # 黄色
        self.rect = self.image.get_rect(center=(x, y))
        self.speed = speed

    def update(self):
        self.rect.y -= self.speed

    def draw(self, screen):
        screen.blit(self.image, self.rect)

    def is_off_screen(self):
        return self.rect.bottom < 0
