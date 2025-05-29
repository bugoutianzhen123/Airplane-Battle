import pygame

class Background:
    def __init__(self, screen_width, screen_height):
        try:
            self.original_image = pygame.image.load("../assets/images/cloud.png").convert_alpha()
            # 调整图片大小以适应屏幕
            self.image = pygame.transform.scale(self.original_image, (screen_width, screen_height))
            self.image_loaded = True
        except (pygame.error, FileNotFoundError) as e:
            print(f"Error loading background image: {e}")
            self.image_loaded = False
            self.image = pygame.Surface((screen_width, screen_height))
            self.image.fill((0, 0, 0))  # 黑色背景
            
        self.rect = self.image.get_rect()
        self.screen_width = screen_width
        self.screen_height = screen_height
        
        # 创建两个背景图片的位置，用于无缝滚动
        self.y1 = 0
        self.y2 = -screen_height
        
        # 滚动速度
        self.scroll_speed = 1

    def update(self):
        # 更新两个背景图片的位置
        self.y1 += self.scroll_speed
        self.y2 += self.scroll_speed
        
        # 当第一个背景图片完全滚出屏幕时，将其重置到顶部
        if self.y1 >= self.screen_height:
            self.y1 = -self.screen_height
            
        # 当第二个背景图片完全滚出屏幕时，将其重置到顶部
        if self.y2 >= self.screen_height:
            self.y2 = -self.screen_height

    def draw(self, screen):
        if self.image_loaded:
            # 绘制两个背景图片
            screen.blit(self.image, (0, self.y1))
            screen.blit(self.image, (0, self.y2))
        else:
            # 如果图片加载失败，绘制纯色背景
            screen.fill((0, 0, 0)) 