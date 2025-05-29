import pygame
import random
from explosion import Explosion
import math
from item import Item


class EnemyBullet:
    def __init__(self, x, y, speed=4):
        self.image = pygame.Surface((5, 15))
        self.image.fill((255, 0, 0))  # 红色子弹
        self.rect = self.image.get_rect(center=(x, y))
        self.speed = speed
        self.speed_x = 0
        self.speed_y = speed

    def update(self):
        self.rect.x += self.speed_x
        self.rect.y += self.speed_y

    def draw(self, screen):
        screen.blit(self.image, self.rect)

    def is_off_screen(self):
        return (self.rect.top > 600 or self.rect.bottom < 0 or 
                self.rect.left > 800 or self.rect.right < 0)


class Enemy:
    def __init__(self, config, x, y, enemy_type="enemy_normal"):
        # Initialize pygame mixer if not already initialized
        if not pygame.mixer.get_init():
            pygame.mixer.init()
            
        # Load sound effects
        try:
            self.sounds = {
                'shoot': pygame.mixer.Sound('../assets/sounds/enemy_shoot.wav'),
                'explosion': pygame.mixer.Sound('../assets/sounds/explosion.wav')
            }
            # Set volume for all sounds (0.0 to 1.0)
            for sound in self.sounds.values():
                sound.set_volume(0.5)
        except (pygame.error, FileNotFoundError) as e:
            print(f"Error loading enemy sound effects: {e}")
            self.sounds = {}

        self.config = config["enemies"]
        try:
            self.original_image = pygame.image.load("../assets/images/"+enemy_type+".png")
            # 根据敌人类型设置不同的大小
            if enemy_type == "enemy_boss":
                size = (128, 128)  # Boss更大
            elif enemy_type == "enemy_special":
                size = (80, 80)    # 精英怪稍大
            else:
                size = (64, 64)    # 普通敌人默认大小
            self.image = pygame.transform.scale(self.original_image, size)
            self.image_loaded = True
        except (pygame.error, FileNotFoundError) as e:
            print(f"Error loading enemy image ({enemy_type}): {e}")
            self.image_loaded = False
            # 根据敌人类型创建不同大小的彩色矩形
            if enemy_type == "enemy_boss":
                size = (128, 128)
                color = (255, 0, 0)  # 红色
            elif enemy_type == "enemy_special":
                size = (80, 80)
                color = (255, 165, 0)  # 橙色
            else:
                size = (64, 64)
                color = (255, 255, 0)  # 黄色
            self.image = pygame.Surface(size)
            self.image.fill(color)
            
        self.rect = self.image.get_rect(topleft=(x, y))
        self.speed = self.config[enemy_type]["speed"]
        self.type = enemy_type
        self.score = self.config[enemy_type]["score"]
        self.health = self.config[enemy_type].get("health", 1)
        self.max_health = self.health  # 保存最大生命值用于血条显示
        
        # 射击相关属性
        self.bullets = []
        self.shoot_cooldown = 2000 if enemy_type == "enemy_special" else 1000  # 精英敌人2秒一发，Boss 1秒一发
        self.last_shot_time = 0
        
        # Boss的特殊属性
        if enemy_type == "enemy_boss":
            self.phase = 1
            self.attack_timer = 0
            self.attack_interval = 3000  # 3秒切换一次攻击模式
            self.attack_pattern = "normal"
            # 移动相关属性
            self.max_speed = 2
            self.current_speed_x = 0
            self.current_speed_y = 0
            self.acceleration = 0.1
            self.deceleration = 0.05
            self.target_speed_x = 0
            self.target_speed_y = 0
            # 圆形移动相关
            self.angle = 0
            self.radius = 100
            # Z字形移动相关
            self.zigzag_angle = 0
            self.horizontal_range = 150
            self.vertical_range = 30
            self.zigzag_speed = 0.02
        # 道具掉落概率
        self.drop_rates = {
            "enemy_normal": 1,    # 普通敌人10%概率掉落
            "enemy_special": 0.3,   # 精英敌人30%概率掉落
            "enemy_boss": 1.0       # Boss必定掉落
        }
        # 道具类型权重
        self.item_weights = {
            "health": 0.4,  # 40%概率掉落生命道具
            "weapon": 0.3,  # 30%概率掉落武器道具
            "shield": 1,  # 20%概率掉落护盾道具
            # "bomb": 0.1     # 10%概率掉落炸弹道具
        }

    def shoot(self):
        now = pygame.time.get_ticks()
        if now - self.last_shot_time >= self.shoot_cooldown:
            if self.type == "enemy_special":
                # 精英敌人发射单发子弹
                bullet = EnemyBullet(self.rect.centerx, self.rect.bottom)
                self.bullets.append(bullet)
            elif self.type == "enemy_boss":
                # Boss根据攻击模式和阶段发射子弹
                if self.phase == 1:
                    if self.attack_pattern == "normal":
                        # 普通模式：发射三发直线子弹
                        for offset in [-20, 0, 20]:
                            bullet = EnemyBullet(self.rect.centerx + offset, self.rect.bottom)
                            self.bullets.append(bullet)
                    elif self.attack_pattern == "circle":
                        # 圆形模式：发射四发子弹，形成十字形
                        for angle in [0, 90, 180, 270]:
                            rad = math.radians(angle)
                            bullet = EnemyBullet(self.rect.centerx, self.rect.bottom)
                            bullet.speed_x = math.sin(rad) * 2
                            bullet.speed_y = math.cos(rad) * 2
                            self.bullets.append(bullet)
                    elif self.attack_pattern == "zigzag":
                        # Z字形模式：发射两发子弹，呈V字形
                        for angle in [-30, 30]:
                            rad = math.radians(angle)
                            bullet = EnemyBullet(self.rect.centerx, self.rect.bottom)
                            bullet.speed_x = math.sin(rad) * 2
                            bullet.speed_y = math.cos(rad) * 2
                            self.bullets.append(bullet)
                else:
                    # 第二阶段：更复杂的攻击模式
                    if self.attack_pattern == "normal":
                        # 普通模式：发射五发子弹，呈扇形分布
                        for angle in [-45, -22.5, 0, 22.5, 45]:
                            rad = math.radians(angle)
                            bullet = EnemyBullet(self.rect.centerx, self.rect.bottom)
                            bullet.speed_x = math.sin(rad) * 3
                            bullet.speed_y = math.cos(rad) * 3
                            self.bullets.append(bullet)
                    elif self.attack_pattern == "circle":
                        # 圆形模式：发射八发子弹，形成星形
                        for angle in range(0, 360, 45):
                            rad = math.radians(angle)
                            bullet = EnemyBullet(self.rect.centerx, self.rect.bottom)
                            bullet.speed_x = math.sin(rad) * 3
                            bullet.speed_y = math.cos(rad) * 3
                            self.bullets.append(bullet)
                    elif self.attack_pattern == "zigzag":
                        # Z字形模式：发射三发子弹，呈W字形
                        for angle in [-45, 0, 45]:
                            rad = math.radians(angle)
                            bullet = EnemyBullet(self.rect.centerx, self.rect.bottom)
                            bullet.speed_x = math.sin(rad) * 3
                            bullet.speed_y = math.cos(rad) * 3
                            self.bullets.append(bullet)
            self.last_shot_time = now
            # Play shoot sound
            if 'shoot' in self.sounds:
                self.sounds['shoot'].play()

    def update(self):
        # 更新子弹
        for bullet in self.bullets[:]:
            bullet.update()
            if bullet.is_off_screen():
                self.bullets.remove(bullet)

        if self.type == "enemy_boss":
            now = pygame.time.get_ticks()
            if now - self.attack_timer > self.attack_interval:
                # 切换攻击模式时，保持当前位置和速度
                current_x = self.rect.centerx
                current_y = self.rect.centery
                self.attack_pattern = random.choice(["normal", "circle", "zigzag"])
                self.attack_timer = now
                # 重置移动参数
                if self.attack_pattern == "normal":
                    self.target_speed_x = self.max_speed if current_x < 400 else -self.max_speed
                    self.target_speed_y = 0
                elif self.attack_pattern == "circle":
                    self.angle = math.atan2(current_y - 100, current_x - 400)
                    self.target_speed_x = 0
                    self.target_speed_y = 0
                elif self.attack_pattern == "zigzag":
                    self.zigzag_angle = 0  # 重置Z字形角度
                    self.target_speed_x = 0
                    self.target_speed_y = 0

            # 根据攻击模式更新目标速度
            if self.attack_pattern == "normal":
                # 水平移动
                if self.rect.right >= 800:
                    self.target_speed_x = -self.max_speed
                elif self.rect.left <= 0:
                    self.target_speed_x = self.max_speed
                # 垂直移动（小幅度上下浮动）
                if self.rect.y > 120:
                    self.target_speed_y = -self.max_speed * 0.3
                elif self.rect.y < 80:
                    self.target_speed_y = self.max_speed * 0.3

            elif self.attack_pattern == "circle":
                # 圆形移动
                self.angle += 0.01
                target_x = 400 + math.cos(self.angle) * self.radius
                target_y = 100 + math.sin(self.angle) * (self.radius * 0.3)
                # 计算到目标位置的方向
                dx = target_x - self.rect.centerx
                dy = target_y - self.rect.centery
                distance = (dx * dx + dy * dy) ** 0.5
                if distance > 0:
                    self.target_speed_x = (dx / distance) * self.max_speed
                    self.target_speed_y = (dy / distance) * self.max_speed * 0.3

            elif self.attack_pattern == "zigzag":
                # Z字形移动
                self.zigzag_angle += self.zigzag_speed
                target_x = 400 + math.sin(self.zigzag_angle) * self.horizontal_range
                target_y = 100 + math.sin(self.zigzag_angle * 2) * self.vertical_range
                # 计算到目标位置的方向
                dx = target_x - self.rect.centerx
                dy = target_y - self.rect.centery
                distance = (dx * dx + dy * dy) ** 0.5
                if distance > 0:
                    self.target_speed_x = (dx / distance) * self.max_speed
                    self.target_speed_y = (dy / distance) * self.max_speed * 0.3

            # 平滑地调整当前速度
            if self.current_speed_x < self.target_speed_x:
                self.current_speed_x = min(self.current_speed_x + self.acceleration, self.target_speed_x)
            elif self.current_speed_x > self.target_speed_x:
                self.current_speed_x = max(self.current_speed_x - self.acceleration, self.target_speed_x)
            else:
                self.current_speed_x *= (1 - self.deceleration)

            if self.current_speed_y < self.target_speed_y:
                self.current_speed_y = min(self.current_speed_y + self.acceleration, self.target_speed_y)
            elif self.current_speed_y > self.target_speed_y:
                self.current_speed_y = max(self.current_speed_y - self.acceleration, self.target_speed_y)
            else:
                self.current_speed_y *= (1 - self.deceleration)

            # 更新位置
            self.rect.x += self.current_speed_x
            self.rect.y += self.current_speed_y

            # 确保不会超出屏幕边界
            self.rect.x = max(0, min(self.rect.x, 800 - self.rect.width))
            self.rect.y = max(50, min(self.rect.y, 200))

            # 当生命值低于50%时进入第二阶段
            if self.health < self.config["enemy_boss"]["health"] * 0.5 and self.phase == 1:
                self.phase = 2
                self.max_speed *= 1.5  # 加快最大速度
                self.acceleration *= 1.5  # 加快加速度
                self.zigzag_speed *= 1.5  # 加快Z字形移动速度
                self.attack_interval = 2000  # 加快攻击频率
                self.shoot_cooldown = 800  # 加快射击频率
        else:
            self.rect.y += self.speed

        # 尝试射击
        if self.type in ["enemy_special", "enemy_boss"]:
            self.shoot()

    def draw(self, screen):
        if not self.image_loaded:
            # 如果图片加载失败，绘制一个带边框的矩形
            pygame.draw.rect(screen, self.image.get_at((0, 0)), self.rect)  # 使用矩形的颜色
            pygame.draw.rect(screen, (255, 255, 255), self.rect, 2)  # 白色边框
        else:
            screen.blit(self.image, self.rect)
            
        # 绘制子弹
        for bullet in self.bullets:
            bullet.draw(screen)
        
        # 如果是Boss，绘制血条
        if self.type == "enemy_boss":
            # 血条背景
            bar_width = 200
            bar_height = 20
            bar_x = (800 - bar_width) // 2  # 居中显示
            bar_y = 10
            pygame.draw.rect(screen, (100, 100, 100), (bar_x, bar_y, bar_width, bar_height))
            
            # 当前血量
            health_width = int((self.health / self.max_health) * bar_width)
            health_color = (255, 0, 0) if self.phase == 1 else (255, 100, 0)  # 第二阶段血条颜色变化
            pygame.draw.rect(screen, health_color, (bar_x, bar_y, health_width, bar_height))
            
            # 血条边框
            pygame.draw.rect(screen, (255, 255, 255), (bar_x, bar_y, bar_width, bar_height), 2)

    def take_damage(self):
        self.health -= 1
        if self.health <= 0 and 'explosion' in self.sounds:
            self.sounds['explosion'].play()
        return self.health <= 0

    def drop_item(self):
        if random.random() < self.drop_rates[self.type]:
            # 根据权重选择道具类型
            item_type = random.choices(
                list(self.item_weights.keys()),
                weights=list(self.item_weights.values())
            )[0]
            return Item(self.rect.centerx, self.rect.centery, item_type)
        return None


class EnemyManager:
    def __init__(self, config):
        self.config = config
        self.enemies = []
        self.spawn_timer = 0
        self.spawn_interval = config["enemy_spawn_rate"] * 1000
        self.elite_spawn_timer = 0
        self.elite_spawn_interval = 6000  # 精英敌人每6秒生成一次
        self.explosions = []
        self.game_stage = 1
        self.stage_score = 0
        self.stage_threshold = 100  # 达到这个分数进入下一阶段
        self.boss_spawned = False
        self.boss_defeated = False
        self.boss = None  # 保存Boss引用
        self.items = []  # 存储掉落的道具

    def update(self, player):
        now = pygame.time.get_ticks()
        
        # 更新游戏阶段
        if not self.boss_spawned and player.score >= self.stage_score + self.stage_threshold:
            self.game_stage += 1
            self.stage_score = player.score
            if self.game_stage % 3 == 0:  # 每3个阶段出现一次Boss
                self.spawn_boss()
            else:
                self.spawn_elite()

        # 生成普通敌人
        if not self.boss_spawned and now - self.spawn_timer > self.spawn_interval:
            self.enemies.append(Enemy(self.config, random.randint(0, 700), -50, "enemy_normal"))
            self.spawn_timer = now

        # 生成精英敌人
        if not self.boss_spawned and now - self.elite_spawn_timer > self.elite_spawn_interval:
            self.enemies.append(Enemy(self.config, random.randint(0, 700), -50, "enemy_special"))
            self.elite_spawn_timer = now

        for enemy in self.enemies[:]:
            enemy.update()
            # 检查子弹碰撞
            if player.bullets:
                for bullet in player.bullets[:]:
                    if enemy.rect.colliderect(bullet.rect):
                        if enemy.take_damage():
                            self.explosions.append(Explosion(enemy.rect.centerx, enemy.rect.centery))
                            # 检查是否掉落道具
                            item = enemy.drop_item()
                            if item:
                                self.items.append(item)
                            self.enemies.remove(enemy)
                            player.score += enemy.score
                            if enemy.type == "enemy_boss":
                                self.boss_defeated = True
                                self.boss_spawned = False
                                return "victory"
                        player.bullets.remove(bullet)
                        break

            # 检查敌人子弹碰撞
            for bullet in enemy.bullets[:]:
                if bullet.rect.colliderect(player.hitbox):  # 使用hitbox进行碰撞检测
                    player.take_damage()
                    enemy.bullets.remove(bullet)
                    break

            # 检查与玩家的碰撞
            if enemy.rect.colliderect(player.hitbox):  # 使用hitbox进行碰撞检测
                player.take_damage()
                if enemy.type != "enemy_boss":  # Boss不会因为碰撞而消失或产生爆炸
                    self.explosions.append(Explosion(enemy.rect.centerx, enemy.rect.centery))
                    # 检查是否掉落道具
                    item = enemy.drop_item()
                    if item:
                        self.items.append(item)
                    self.enemies.remove(enemy)
                    player.score += enemy.score  # 添加分数

        for explosion in self.explosions[:]:
            explosion.update()
            if explosion.is_finished():
                self.explosions.remove(explosion)

        # 更新道具
        for item in self.items[:]:
            item.update()
            # 检查道具是否被玩家拾取
            if item.rect.colliderect(player.hitbox):
                item.apply_effect(player)
                self.items.remove(item)
            # 移除超出屏幕的道具
            elif item.is_off_screen():
                self.items.remove(item)

    def spawn_elite(self):
        # 这个方法现在只用于阶段切换时生成精英敌人
        self.enemies.append(Enemy(self.config, random.randint(0, 700), -50, "enemy_special"))
        # 重置精英敌人生成计时器，确保不会立即生成下一个
        self.elite_spawn_timer = pygame.time.get_ticks()

    def spawn_boss(self):
        self.boss_spawned = True
        # 将Boss生成在屏幕上方中央位置
        self.boss = Enemy(self.config, 400 - 64, 50, "enemy_boss")  # 64是Boss宽度的一半
        self.enemies.append(self.boss)

    def draw(self, screen):
        for enemy in self.enemies:
            enemy.draw(screen)        
            for explosion in self.explosions:
                explosion.draw(screen)
        # 绘制道具
        for item in self.items:
            item.draw(screen)
