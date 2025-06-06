import pygame
from bullet import Bullet
from config import load_config  # 导入 load_config 函数

def get_key_constant(key_name):
    """将按键名称转换为 pygame 按键常量"""
    # 特殊按键映射
    special_keys = {
        "LEFT": pygame.K_LEFT,
        "RIGHT": pygame.K_RIGHT,
        "UP": pygame.K_UP,
        "DOWN": pygame.K_DOWN,
        "SPACE": pygame.K_SPACE,
        "ESCAPE": pygame.K_ESCAPE,
        "RETURN": pygame.K_RETURN,
        "TAB": pygame.K_TAB,
        "BACKSPACE": pygame.K_BACKSPACE,
        "DELETE": pygame.K_DELETE,
        "INSERT": pygame.K_INSERT,
        "HOME": pygame.K_HOME,
        "END": pygame.K_END,
        "PAGEUP": pygame.K_PAGEUP,
        "PAGEDOWN": pygame.K_PAGEDOWN,
        "F1": pygame.K_F1,
        "F2": pygame.K_F2,
        "F3": pygame.K_F3,
        "F4": pygame.K_F4,
        "F5": pygame.K_F5,
        "F6": pygame.K_F6,
        "F7": pygame.K_F7,
        "F8": pygame.K_F8,
        "F9": pygame.K_F9,
        "F10": pygame.K_F10,
        "F11": pygame.K_F11,
        "F12": pygame.K_F12,
        "LSHIFT": pygame.K_LSHIFT,
        "RSHIFT": pygame.K_RSHIFT,
        "LCTRL": pygame.K_LCTRL,
        "RCTRL": pygame.K_RCTRL,
        "LALT": pygame.K_LALT,
        "RALT": pygame.K_RALT,
        "LSUPER": pygame.K_LSUPER,
        "RSUPER": pygame.K_RSUPER,
        "MENU": pygame.K_MENU,
        "NUMLOCK": pygame.K_NUMLOCK,
        "CAPSLOCK": pygame.K_CAPSLOCK,
        "SCROLLLOCK": pygame.K_SCROLLLOCK,
        "PRINTSCREEN": pygame.K_PRINTSCREEN,
        "PAUSE": pygame.K_PAUSE,
        "BREAK": pygame.K_BREAK,
        "SLASH": pygame.K_SLASH,
        "BACKSLASH": pygame.K_BACKSLASH,
        "MINUS": pygame.K_MINUS,
        "EQUALS": pygame.K_EQUALS,
        "LEFTBRACKET": pygame.K_LEFTBRACKET,
        "RIGHTBRACKET": pygame.K_RIGHTBRACKET,
        "SEMICOLON": pygame.K_SEMICOLON,
        "QUOTE": pygame.K_QUOTE,
        "COMMA": pygame.K_COMMA,
        "PERIOD": pygame.K_PERIOD,
        "BACKQUOTE": pygame.K_BACKQUOTE
    }
    
    # 如果是特殊按键，直接返回对应的常量
    if key_name in special_keys:
        return special_keys[key_name]
    
    # 如果是单个字符，转换为对应的按键常量
    if len(key_name) == 1:
        # 转换为小写字母的按键常量
        if key_name.isalpha():
            return getattr(pygame, f"K_{key_name.lower()}")
        # 数字键
        elif key_name.isdigit():
            return getattr(pygame, f"K_{key_name}")
        # 其他字符
        else:
            # 对于特殊字符，尝试直接获取对应的按键常量
            try:
                return getattr(pygame, f"K_{key_name}")
            except AttributeError:
                # 如果找不到对应的按键常量，返回 None
                return None
    
    # 如果找不到对应的按键常量，返回 None
    return None

class Player:
    def __init__(self, config, x=400, y=500, player_id=1):
        # Initialize pygame mixer if not already initialized
        if not pygame.mixer.get_init():
            pygame.mixer.init()
            
        # Load sound effects
        try:
            self.sounds = {
                'shoot': pygame.mixer.Sound('../assets/sounds/player_shoot.wav'),
                'explosion': pygame.mixer.Sound('../assets/sounds/explosion.wav'),
                'victory': pygame.mixer.Sound('../assets/sounds/victory.wav'),
                'shield': pygame.mixer.Sound('../assets/sounds/shield.wav')
            }
            # Set volume for all sounds (0.0 to 1.0)
            for sound in self.sounds.values():
                sound.set_volume(0.5)
        except (pygame.error, FileNotFoundError) as e:
            print(f"Error loading player sound effects: {e}")
            self.sounds = {}

        self.config = config
        self.player_id = player_id
        try:
            self.original_image = pygame.image.load(f"../assets/images/player{player_id}.png")
            self.image = pygame.transform.scale(self.original_image, (64, 64))
            self.image_loaded = True
        except (pygame.error, FileNotFoundError) as e:
            print(f"Error loading player image: {e}")
            self.image_loaded = False
            self.image = pygame.Surface((64, 64))
            self.image.fill((0, 255, 0))  # 绿色矩形作为默认图像
            
        self.rect = self.image.get_rect(center=(x, y))
        self.hitbox = pygame.Rect(0, 0, 40, 40)  # 创建一个更小的碰撞箱
        self.hitbox.center = self.rect.center
        
        # 移动相关属性
        self.max_speed = config["player"]["max_speed"]
        self.acceleration = config["player"]["acceleration"]
        self.current_speed_x = 0
        self.current_speed_y = 0
        self.target_speed_x = 0
        self.target_speed_y = 0
        
        # 生命值
        self.max_lives = config["player"]["lives"]  # 从配置中获取最大生命值
        self.lives = self.max_lives  # 当前生命值
        self.score = 0
        
        # 武器相关属性
        self.weapon_level = 1
        self.bullets = []
        self.last_shot_time = 0
        self.shoot_cooldown = 200  # 射击冷却时间（毫秒）

        # 护盾相关属性
        self.has_shield = False
        self.shield_alpha = 255
        self.shield_fade_speed = 5
        self.shield_rect = pygame.Rect(0, 0, 80, 80)  # 护盾比飞机稍大
        self.shield_rect.center = self.rect.center
        self.shield_time = 0
        self.shield_duration = 5000  # 护盾持续时间5秒
        self.shield_warning_time = 1000  # 最后1秒开始闪烁警告
        self.shield_warning_alpha = 255
        self.shield_warning_fade_speed = 25  # 警告闪烁速度

        # 无敌时间
        self.invincible = False
        self.invincible_timer = 0
        self.invincible_duration = 2000  # 无敌时间2秒
        self.invincible_alpha = 255
        self.invincible_fade_speed = 10

    def update(self):
        # 重新加载配置以获取最新的按键设置
        new_config = load_config()
        if new_config:
            self.config = new_config
            # 更新音量
            volume = self.config.get("volume", 0.5)
            for sound in self.sounds.values():
                sound.set_volume(volume)
            # 更新玩家属性
            self.max_speed = self.config["player"]["max_speed"]
            self.acceleration = self.config["player"]["acceleration"]
            self.max_lives = self.config["player"]["lives"]

        # 获取按键状态
        keys = pygame.key.get_pressed()
        
        # 根据玩家ID选择对应的按键配置
        if self.player_id == 1:
            left_key = get_key_constant(self.config["key_bindings"]["player1"]["left"])
            right_key = get_key_constant(self.config["key_bindings"]["player1"]["right"])
            up_key = get_key_constant(self.config["key_bindings"]["player1"]["up"])
            down_key = get_key_constant(self.config["key_bindings"]["player1"]["down"])
            shoot_key = get_key_constant(self.config["key_bindings"]["player1"]["shoot"])
        else:
            left_key = get_key_constant(self.config["key_bindings"]["player2"]["left"])
            right_key = get_key_constant(self.config["key_bindings"]["player2"]["right"])
            up_key = get_key_constant(self.config["key_bindings"]["player2"]["up"])
            down_key = get_key_constant(self.config["key_bindings"]["player2"]["down"])
            shoot_key = get_key_constant(self.config["key_bindings"]["player2"]["shoot"])
        
        # 更新目标速度
        self.target_speed_x = 0
        self.target_speed_y = 0
        
        if left_key and keys[left_key]:
            self.target_speed_x = -self.max_speed
        if right_key and keys[right_key]:
            self.target_speed_x = self.max_speed
        if up_key and keys[up_key]:
            self.target_speed_y = -self.max_speed
        if down_key and keys[down_key]:
            self.target_speed_y = self.max_speed
            
        # 计算速度矢量的长度
        speed_length = (self.target_speed_x ** 2 + self.target_speed_y ** 2) ** 0.5
        
        # 如果速度超过最大速度，进行归一化处理
        if speed_length > self.max_speed:
            scale = self.max_speed / speed_length
            self.target_speed_x *= scale
            self.target_speed_y *= scale
            
        # 平滑地调整当前速度
        if self.current_speed_x < self.target_speed_x:
            self.current_speed_x = min(self.current_speed_x + self.acceleration, self.target_speed_x)
        elif self.current_speed_x > self.target_speed_x:
            self.current_speed_x = max(self.current_speed_x - self.acceleration, self.target_speed_x)
        else:
            self.current_speed_x *= 0.9  # 添加一些阻力

        if self.current_speed_y < self.target_speed_y:
            self.current_speed_y = min(self.current_speed_y + self.acceleration, self.target_speed_y)
        elif self.current_speed_y > self.target_speed_y:
            self.current_speed_y = max(self.current_speed_y - self.acceleration, self.target_speed_y)
        else:
            self.current_speed_y *= 0.9  # 添加一些阻力
            
        # 确保当前速度也不超过最大速度
        current_speed_length = (self.current_speed_x ** 2 + self.current_speed_y ** 2) ** 0.5
        if current_speed_length > self.max_speed:
            scale = self.max_speed / current_speed_length
            self.current_speed_x *= scale
            self.current_speed_y *= scale

        # 更新位置
        self.rect.x += self.current_speed_x
        self.rect.y += self.current_speed_y
        
        # 确保不会超出屏幕边界
        self.rect.x = max(0, min(self.rect.x, 800 - self.rect.width))
        self.rect.y = max(0, min(self.rect.y, 600 - self.rect.height))
        
        # 更新碰撞箱位置
        self.hitbox.center = self.rect.center
        
        # 更新护盾位置
        if self.has_shield:
            self.shield_rect.center = self.rect.center
            
            # 检查护盾是否即将结束
            remaining_time = self.shield_duration - (pygame.time.get_ticks() - self.shield_time)
            
            if remaining_time <= self.shield_warning_time:
                # 护盾即将结束时快速闪烁
                self.shield_warning_alpha = max(50, self.shield_warning_alpha - self.shield_warning_fade_speed)
                if self.shield_warning_alpha <= 50:
                    self.shield_warning_fade_speed = -self.shield_warning_fade_speed
                elif self.shield_warning_alpha >= 255:
                    self.shield_warning_fade_speed = abs(self.shield_warning_fade_speed)
                self.shield_alpha = self.shield_warning_alpha
            else:
                # 正常护盾呼吸效果
                self.shield_alpha = max(100, self.shield_alpha - self.shield_fade_speed)
                if self.shield_alpha <= 100:
                    self.shield_fade_speed = -self.shield_fade_speed
                elif self.shield_alpha >= 255:
                    self.shield_fade_speed = abs(self.shield_fade_speed)
            
            # 检查护盾是否过期
            if pygame.time.get_ticks() - self.shield_time > self.shield_duration:
                self.has_shield = False
                self.shield_alpha = 255
                self.shield_warning_alpha = 255
        
        # 更新无敌时间
        if self.invincible:
            self.invincible_alpha = max(50, self.invincible_alpha - self.invincible_fade_speed)
            if self.invincible_alpha <= 50:
                self.invincible_fade_speed = -self.invincible_fade_speed
            elif self.invincible_alpha >= 255:
                self.invincible_fade_speed = abs(self.invincible_fade_speed)
            
            if pygame.time.get_ticks() - self.invincible_timer > self.invincible_duration:
                self.invincible = False
                self.invincible_alpha = 255
        
        # 射击
        if shoot_key and keys[shoot_key]:
            self.shoot()
            
        # 更新子弹
        for bullet in self.bullets[:]:
            bullet.update()
            if bullet.is_off_screen():
                self.bullets.remove(bullet)

    def draw(self, screen):
        # 绘制护盾
        if self.has_shield:
            shield_surface = pygame.Surface((80, 80), pygame.SRCALPHA)
            # 确保所有颜色值都是有效的整数
            alpha = max(0, min(255, int(self.shield_alpha)))
            shield_color = (0, 255, 255, alpha)
            pygame.draw.circle(shield_surface, shield_color, (40, 40), 40)
            screen.blit(shield_surface, self.shield_rect)
        
        # 绘制飞机
        if self.invincible:
            # 创建半透明的飞机图像
            temp_image = self.image.copy()
            temp_image.set_alpha(self.invincible_alpha)
            screen.blit(temp_image, self.rect)
        else:
            screen.blit(self.image, self.rect)
        
        # 绘制子弹
        for bullet in self.bullets:
            bullet.draw(screen)

    def shoot(self):
        now = pygame.time.get_ticks()
        if now - self.last_shot_time >= self.shoot_cooldown:
            if self.weapon_level == 1:
                # 单发子弹
                bullet = Bullet(self.rect.centerx, self.rect.top)
                self.bullets.append(bullet)
            elif self.weapon_level == 2:
                # 双发子弹
                bullet1 = Bullet(self.rect.left + 10, self.rect.top)
                bullet2 = Bullet(self.rect.right - 10, self.rect.top)
                self.bullets.extend([bullet1, bullet2])
            elif self.weapon_level == 3:
                # 三发子弹
                bullet1 = Bullet(self.rect.left + 10, self.rect.top)
                bullet2 = Bullet(self.rect.centerx, self.rect.top)
                bullet3 = Bullet(self.rect.right - 10, self.rect.top)
                self.bullets.extend([bullet1, bullet2, bullet3])
            
            self.last_shot_time = now
            # Play shoot sound
            if 'shoot' in self.sounds:
                self.sounds['shoot'].play()

    def take_damage(self):
        # 如果处于无敌状态，直接返回False，不进行任何伤害判定
        if self.invincible:
            return False
            
        if self.has_shield:
            self.has_shield = False
            self.invincible = True
            self.invincible_timer = pygame.time.get_ticks()
            return False
        else:
            self.lives -= 1
            self.invincible = True
            self.invincible_timer = pygame.time.get_ticks()
            # Play explosion sound
            if 'explosion' in self.sounds:
                self.sounds['explosion'].play()
            return True

    def is_alive(self):
        return self.lives > 0

    def play_victory_sound(self):
        if 'victory' in self.sounds:
            self.sounds['victory'].play()

    def upgrade_weapon(self):
        if self.weapon_level < 3:
            self.weapon_level += 1
            # Play upgrade sound
            if 'shoot' in self.sounds:
                self.sounds['shoot'].play()

    def activate_shield(self):
        """激活护盾并播放音效"""
        self.has_shield = True
        self.shield_time = pygame.time.get_ticks()
        self.shield_alpha = 255
        self.shield_warning_alpha = 255
        if 'shield' in self.sounds:
            self.sounds['shield'].play()

