import pygame
from config import load_config, update_volume
from ui import show_main_menu, show_game_mode_menu, show_pause_settings, show_settings_menu, show_key_binding_prompt
from player import Player
from enemy import EnemyManager
from background import Background

def apply_config_changes(config, player1, player2, enemies):
    """应用配置更改"""
    if config:
        # 更新音量
        volume = config.get("volume", 0.5)
        for sound_name, sound in player1.sounds.items():
            sound.set_volume(volume)
        if player2:
            for sound_name, sound in player2.sounds.items():
                sound.set_volume(volume)
        
        # 更新玩家配置
        player1.max_speed = config["player"]["max_speed"]
        player1.acceleration = config["player"]["acceleration"]
        if player2:
            player2.max_speed = config["player"]["max_speed"]
            player2.acceleration = config["player"]["acceleration"]
        
        # 更新敌人配置
        enemies.config = config

def main():
    pygame.init()
    config = load_config()
    screen = pygame.display.set_mode((config["screen_width"], config["screen_height"]))
    pygame.display.set_caption("打飞机大战")
    clock = pygame.time.Clock()

    font = pygame.font.SysFont(config["font"], 36)

    game_state = "menu"
    previous_state = None
    waiting_for_key = False
    current_key_binding = None
    is_two_player = False  # 是否双人模式

    player1 = Player(config, x=300, y=500, player_id=1)
    player2 = None  # 第二个玩家初始为None
    enemies = EnemyManager(config)

    # 初始化背景
    background = Background(config["screen_width"], config["screen_height"])

    running = True
    while running:
        # 检查配置更新
        new_config = load_config()
        if new_config:
            apply_config_changes(new_config, player1, player2, enemies)
            config = new_config

        screen.fill((0, 0, 0))
        mouse_pos = pygame.mouse.get_pos()
        mouse_click = False
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mouse_click = True
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if game_state == "playing":
                        previous_state = game_state
                        game_state = "pause"
                    elif game_state == "pause":
                        game_state = "playing"
                    elif game_state == "settings":
                        if previous_state == "pause":
                            game_state = "pause"
                        else:
                            game_state = previous_state
                    elif game_state == "key_binding":
                        game_state = "settings"

            if game_state == "menu":
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        game_state = "playing"

            if game_state in ["game_over", "victory"]:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_r:
                       # 重新开始游戏
                       player1 = Player(config, x=300, y=500, player_id=1)
                       player2 = None
                       enemies = EnemyManager(config)
                       game_state = "playing"
                    elif event.key == pygame.K_ESCAPE:
                       running = False

        screen.fill((0, 0, 0))

        # 更新和绘制背景
        if game_state == "playing":
            background.update()
        # 在所有状态下都绘制背景
        background.draw(screen)

        if game_state == "menu":
            buttons = show_main_menu(screen, font)
            for text, rect in buttons:
                if mouse_click and rect.collidepoint(mouse_pos):
                    if text == "开始游戏":
                        game_state = "mode_select"
                    elif text == "设置":
                        previous_state = game_state
                        game_state = "settings"
                    elif text == "退出游戏":
                        running = False
        elif game_state == "pause":
            buttons = show_pause_settings(screen, font)
            for text, rect in buttons:
                if mouse_click and rect.collidepoint(mouse_pos):
                    if text == "继续游戏":
                        game_state = "playing"
                    elif text == "设置":
                        previous_state = game_state
                        game_state = "settings"
                    elif text == "退出到主菜单":
                        game_state = "menu"
                        # 重置游戏状态
                        player1 = Player(config, x=300, y=500, player_id=1)
                        player2 = None
                        enemies = EnemyManager(config)
                        is_two_player = False
                    elif text == "退出游戏":
                        running = False
        elif game_state == "playing":
            # 更新玩家
            player1.update()
            if player2:
                player2.update()
            result = enemies.update(player1)
            if player2:
                enemies.update(player2)
            if result == "victory":
                game_state = "victory"
                player1.play_victory_sound()
            player1.draw(screen)
            if player2:
                player2.draw(screen)
            enemies.draw(screen)
            
            # 显示分数和生命值
            if is_two_player:
                # 双人模式：左侧显示P1，右侧显示P2
                # P1信息
                score_text1 = font.render(f"P1得分: {player1.score}", True, (255, 255, 255))
                life_text1 = font.render(f"P1生命: {player1.lives}", True, (255, 255, 255))
                screen.blit(score_text1, (10, 10))
                screen.blit(life_text1, (10, 50))
                
                # P2信息
                score_text2 = font.render(f"P2得分: {player2.score}", True, (255, 255, 255))
                life_text2 = font.render(f"P2生命: {player2.lives}", True, (255, 255, 255))
                screen.blit(score_text2, (screen.get_width() - 200, 10))
                screen.blit(life_text2, (screen.get_width() - 200, 50))
            else:
                # 单人模式：只显示P1信息
                score_text = font.render(f"得分: {player1.score}", True, (255, 255, 255))
                life_text = font.render(f"生命: {player1.lives}", True, (255, 255, 255))
                screen.blit(score_text, (10, 10))
                screen.blit(life_text, (10, 50))

            # 判断生命是否结束
            if not player1.is_alive() and (not player2 or not player2.is_alive()):
                game_state = "game_over"
        elif game_state == "mode_select":
            buttons = show_game_mode_menu(screen, font)
            for text, rect in buttons:
                if mouse_click and rect.collidepoint(mouse_pos):
                    if text == "单人游戏":
                        is_two_player = False
                        game_state = "playing"
                    elif text == "双人游戏":
                        is_two_player = True
                        player2 = Player(config, x=500, y=500, player_id=2)
                        game_state = "playing"
                    elif text == "设置":
                        previous_state = game_state
                        game_state = "settings"
                    elif text == "退出游戏":
                        running = False
        elif game_state == "settings":
            buttons = show_settings_menu(screen, font)
            for button_id, rect in buttons:
                if mouse_click and rect.collidepoint(mouse_pos):
                    if button_id == "volume_down":
                        config = load_config()
                        new_volume = max(0.0, config["volume"] - 0.1)
                        update_volume(new_volume)
                    elif button_id == "volume_up":
                        config = load_config()
                        new_volume = min(1.0, config["volume"] + 0.1)
                        update_volume(new_volume)
                    elif button_id == "back":
                        if previous_state == "pause":
                            game_state = "pause"
                        else:
                            game_state = previous_state
                    elif button_id.startswith("bind_"):
                        _, player, action = button_id.split("_")
                        game_state = "key_binding"
                        current_key_binding = (player, action)
        elif game_state == "key_binding":
            if current_key_binding:
                player, action = current_key_binding
                if show_key_binding_prompt(screen, font, player, action):
                    game_state = "settings"
                else:
                    running = False
        elif game_state == "game_over":
            game_over_text = font.render("游戏结束！按 R 重新开始，ESC 退出", True, (255, 0, 0))
            screen.blit(game_over_text, (100, 250))
        elif game_state == "victory":
            victory_text = font.render("恭喜通关！按 R 重新开始，ESC 退出", True, (255, 215, 0))
            screen.blit(victory_text, (100, 250))

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()


if __name__ == "__main__":
    main()
