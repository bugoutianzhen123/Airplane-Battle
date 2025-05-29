import pygame
import random

class Item:
    def __init__(self, x, y, item_type):
        self.type = item_type
        try:
            self.original_image = pygame.image.load(f"../assets/images/item_{item_type}.png")
            self.image = pygame.transform.scale(self.original_image, (32, 32))
            self.image_loaded = True
        except (pygame.error, FileNotFoundError) as e:
            print(f"Error loading item image ({item_type}): {e}")
            self.image_loaded = False
            # 创建一个彩色矩形作为替代
            self.image = pygame.Surface((32, 32))
            self.image.fill(self.colors[item_type])
            
        self.rect = self.image.get_rect(center=(x, y))
        self.speed = 2  # 道具下落速度
        
        # 道具效果
        self.effects = {
            "health": 1,     # 恢复生命值
            "shield": 1,     # 获得护盾
            "weapon": 1,     # 武器升级
            # "bomb": 1    # 获得炸弹
        }
        
        # 道具颜色
        self.colors = {
            "health": (255, 0, 0),     # 红色
            "shield": (0, 255, 0),     # 绿色
            "weapon": (0, 0, 255),     # 蓝色
            # "bomb": (255, 255, 0)     # 黄色
        }

    def update(self):
        self.rect.y += self.speed

    def draw(self, screen):
        if not self.image_loaded:
            # 如果图片加载失败，绘制一个带边框的矩形
            pygame.draw.rect(screen, self.colors[self.type], self.rect)  # 使用道具对应的颜色
            pygame.draw.rect(screen, (255, 255, 255), self.rect, 2)  # 白色边框
        else:
            screen.blit(self.image, self.rect)

    def is_off_screen(self):
        return self.rect.top > 600

    def apply_effect(self, player):
        if self.type == "health":
            player.lives = min(player.lives + self.effects["health"], player.max_lives)
        elif self.type == "weapon":
            player.upgrade_weapon()  # 使用 upgrade_weapon 方法来升级武器
        elif self.type == "shield":
            player.shield = True
            player.shield_time = pygame.time.get_ticks()
            player.activate_shield()  # 使用 activate_shield 方法来触发音效
        # elif self.type == "bomb":
        #     player.bombs += self.effects["bomb"] 