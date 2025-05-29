import pygame
from config import load_config, update_volume, update_key_binding

def show_main_menu(screen, font):
    title = font.render("飞机大作战", True, (255, 255, 0))
    screen.blit(title, (screen.get_width() // 2 - title.get_width() // 2, 150))

    # 按钮设置
    texts = ["开始游戏", "设置", "退出游戏"]
    buttons = []
    for i, text in enumerate(texts):
        txt_surf = font.render(text, True, (0, 0, 0))
        rect = pygame.Rect(screen.get_width() // 2 - 100, 300 + i * 70, 200, 50)
        pygame.draw.rect(screen, (150, 150, 250), rect)
        # 计算文字位置使其居中
        text_x = rect.x + (rect.width - txt_surf.get_width()) // 2
        text_y = rect.y + (rect.height - txt_surf.get_height()) // 2
        screen.blit(txt_surf, (text_x, text_y))
        buttons.append((text, rect))
    return buttons


def show_game_mode_menu(screen, font):
    texts = ["单人游戏", "双人游戏", "设置", "退出游戏"]
    buttons = []
    for i, text in enumerate(texts):
        txt_surf = font.render(text, True, (0, 0, 0))
        rect = pygame.Rect(screen.get_width() // 2 - 100, 200 + i * 70, 200, 50)
        pygame.draw.rect(screen, (150, 150, 250), rect)
        # 计算文字位置使其居中
        text_x = rect.x + (rect.width - txt_surf.get_width()) // 2
        text_y = rect.y + (rect.height - txt_surf.get_height()) // 2
        screen.blit(txt_surf, (text_x, text_y))
        buttons.append((text, rect))
    return buttons  # 返回按钮列表

def show_pause_settings(screen, font):
    texts = ["继续游戏", "设置", "退出到主菜单", "退出游戏"]
    buttons = []
    for i, text in enumerate(texts):
        txt_surf = font.render(text, True, (0, 0, 0))
        rect = pygame.Rect(screen.get_width() // 2 - 120, 150 + i * 80, 240, 60)
        pygame.draw.rect(screen, (180, 180, 180), rect)
        # 计算文字位置使其居中
        text_x = rect.x + (rect.width - txt_surf.get_width()) // 2
        text_y = rect.y + (rect.height - txt_surf.get_height()) // 2
        screen.blit(txt_surf, (text_x, text_y))
        buttons.append((text, rect))
    return buttons

def show_settings_menu(screen, font):
    config = load_config()
    buttons = []
    
    # 标题
    title = font.render("设置", True, (255, 255, 0))
    screen.blit(title, (screen.get_width() // 2 - title.get_width() // 2, 25))
    
    # 音量设置
    volume_text = font.render(f"音量: {int(config['volume'] * 100)}%", True, (255, 255, 255))
    screen.blit(volume_text, (screen.get_width() // 2 - 100, 75))
    
    # 音量调节按钮
    volume_down = pygame.Rect(screen.get_width() // 2 - 150, 75, 40, 40)
    volume_up = pygame.Rect(screen.get_width() // 2 + 110, 75, 40, 40)
    pygame.draw.rect(screen, (150, 150, 250), volume_down)
    pygame.draw.rect(screen, (150, 150, 250), volume_up)
    
    # 音量按钮文字居中
    minus_text = font.render("-", True, (0, 0, 0))
    plus_text = font.render("+", True, (0, 0, 0))
    minus_x = volume_down.x + (volume_down.width - minus_text.get_width()) // 2
    minus_y = volume_down.y + (volume_down.height - minus_text.get_height()) // 2
    plus_x = volume_up.x + (volume_up.width - plus_text.get_width()) // 2
    plus_y = volume_up.y + (volume_up.height - plus_text.get_height()) // 2
    screen.blit(minus_text, (minus_x, minus_y))
    screen.blit(plus_text, (plus_x, plus_y))
    
    buttons.append(("volume_down", volume_down))
    buttons.append(("volume_up", volume_up))
    
    # 按键设置
    y_pos = 150
    for player in ["player1", "player2"]:
        player_text = "玩家1" if player == "player1" else "玩家2"
        screen.blit(font.render(player_text, True, (255, 255, 255)), (screen.get_width() // 2 - 200, y_pos))
        
        for action, key in config["key_bindings"][player].items():
            action_text = {
                "left": "左移",
                "right": "右移",
                "up": "上移",
                "down": "下移",
                "shoot": "射击"
            }[action]
            
            key_text = font.render(f"{action_text}: {key}", True, (255, 255, 255))
            screen.blit(key_text, (screen.get_width() // 2 - 100, y_pos))
            
            # 添加按键绑定按钮
            bind_rect = pygame.Rect(screen.get_width() // 2 + 100, y_pos, 100, 30)
            pygame.draw.rect(screen, (150, 150, 250), bind_rect)
            # 更改按钮文字居中
            change_text = font.render("更改", True, (0, 0, 0))
            change_x = bind_rect.x + (bind_rect.width - change_text.get_width()) // 2
            change_y = bind_rect.y + (bind_rect.height - change_text.get_height()) // 2
            screen.blit(change_text, (change_x, change_y))
            buttons.append((f"bind_{player}_{action}", bind_rect))
            
            y_pos += 40
    
    # 返回按钮
    back_rect = pygame.Rect(screen.get_width() // 2 - 100, y_pos + 50, 200, 50)
    pygame.draw.rect(screen, (150, 150, 250), back_rect)
    # 返回按钮文字居中
    back_text = font.render("返回", True, (0, 0, 0))
    back_x = back_rect.x + (back_rect.width - back_text.get_width()) // 2
    back_y = back_rect.y + (back_rect.height - back_text.get_height()) // 2
    screen.blit(back_text, (back_x, back_y))
    buttons.append(("back", back_rect))
    
    return buttons

def show_key_binding_prompt(screen, font, player, action):
    prompt_text = font.render(f"请按下新的按键来设置{player}的{action}", True, (255, 255, 255))
    screen.blit(prompt_text, (screen.get_width() // 2 - prompt_text.get_width() // 2, 
                            screen.get_height() // 2 - prompt_text.get_height() // 2))
    pygame.display.flip()
    
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                # 获取按键名称
                key_name = pygame.key.name(event.key)
                
                # 处理特殊按键
                if event.key == pygame.K_SPACE:
                    key_name = "SPACE"
                elif event.key == pygame.K_LEFT:
                    key_name = "LEFT"
                elif event.key == pygame.K_RIGHT:
                    key_name = "RIGHT"
                elif event.key == pygame.K_UP:
                    key_name = "UP"
                elif event.key == pygame.K_DOWN:
                    key_name = "DOWN"
                elif event.key == pygame.K_ESCAPE:
                    key_name = "ESCAPE"
                elif event.key == pygame.K_RETURN:
                    key_name = "RETURN"
                elif event.key == pygame.K_TAB:
                    key_name = "TAB"
                elif event.key == pygame.K_BACKSPACE:
                    key_name = "BACKSPACE"
                elif event.key == pygame.K_DELETE:
                    key_name = "DELETE"
                elif event.key == pygame.K_INSERT:
                    key_name = "INSERT"
                elif event.key == pygame.K_HOME:
                    key_name = "HOME"
                elif event.key == pygame.K_END:
                    key_name = "END"
                elif event.key == pygame.K_PAGEUP:
                    key_name = "PAGEUP"
                elif event.key == pygame.K_PAGEDOWN:
                    key_name = "PAGEDOWN"
                elif event.key == pygame.K_F1:
                    key_name = "F1"
                elif event.key == pygame.K_F2:
                    key_name = "F2"
                elif event.key == pygame.K_F3:
                    key_name = "F3"
                elif event.key == pygame.K_F4:
                    key_name = "F4"
                elif event.key == pygame.K_F5:
                    key_name = "F5"
                elif event.key == pygame.K_F6:
                    key_name = "F6"
                elif event.key == pygame.K_F7:
                    key_name = "F7"
                elif event.key == pygame.K_F8:
                    key_name = "F8"
                elif event.key == pygame.K_F9:
                    key_name = "F9"
                elif event.key == pygame.K_F10:
                    key_name = "F10"
                elif event.key == pygame.K_F11:
                    key_name = "F11"
                elif event.key == pygame.K_F12:
                    key_name = "F12"
                elif event.key == pygame.K_LSHIFT:
                    key_name = "LSHIFT"
                elif event.key == pygame.K_RSHIFT:
                    key_name = "RSHIFT"
                elif event.key == pygame.K_LCTRL:
                    key_name = "LCTRL"
                elif event.key == pygame.K_RCTRL:
                    key_name = "RCTRL"
                elif event.key == pygame.K_LALT:
                    key_name = "LALT"
                elif event.key == pygame.K_RALT:
                    key_name = "RALT"
                elif event.key == pygame.K_LSUPER:
                    key_name = "LSUPER"
                elif event.key == pygame.K_RSUPER:
                    key_name = "RSUPER"
                elif event.key == pygame.K_MENU:
                    key_name = "MENU"
                elif event.key == pygame.K_NUMLOCK:
                    key_name = "NUMLOCK"
                elif event.key == pygame.K_CAPSLOCK:
                    key_name = "CAPSLOCK"
                elif event.key == pygame.K_SCROLLLOCK:
                    key_name = "SCROLLLOCK"
                elif event.key == pygame.K_PRINTSCREEN:
                    key_name = "PRINTSCREEN"
                elif event.key == pygame.K_PAUSE:
                    key_name = "PAUSE"
                elif event.key == pygame.K_BREAK:
                    key_name = "BREAK"
                elif event.key == pygame.K_SLASH:
                    key_name = "SLASH"
                elif event.key == pygame.K_BACKSLASH:
                    key_name = "BACKSLASH"
                elif event.key == pygame.K_MINUS:
                    key_name = "MINUS"
                elif event.key == pygame.K_EQUALS:
                    key_name = "EQUALS"
                elif event.key == pygame.K_LEFTBRACKET:
                    key_name = "LEFTBRACKET"
                elif event.key == pygame.K_RIGHTBRACKET:
                    key_name = "RIGHTBRACKET"
                elif event.key == pygame.K_SEMICOLON:
                    key_name = "SEMICOLON"
                elif event.key == pygame.K_QUOTE:
                    key_name = "QUOTE"
                elif event.key == pygame.K_COMMA:
                    key_name = "COMMA"
                elif event.key == pygame.K_PERIOD:
                    key_name = "PERIOD"
                elif event.key == pygame.K_BACKQUOTE:
                    key_name = "BACKQUOTE"
                
                # 将按键名称转换为大写
                key_name = key_name.upper()
                
                # 更新按键绑定
                update_key_binding(player, action, key_name)
                waiting = False
            elif event.type == pygame.QUIT:
                return False
    return True