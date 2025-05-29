import json
import os
import pygame

# 按键名称到 pygame 常量的映射
KEY_MAPPING = {
    "LEFT": pygame.K_LEFT,
    "RIGHT": pygame.K_RIGHT,
    "UP": pygame.K_UP,
    "DOWN": pygame.K_DOWN,
    "SPACE": pygame.K_SPACE,
    "A": pygame.K_a,
    "D": pygame.K_d,
    "W": pygame.K_w,
    "S": pygame.K_s,
    "F": pygame.K_f
}

# 默认配置（可用于首次生成 settings.json 或作为 fallback）
DEFAULT_CONFIG = {
    "screen_width": 800,
    "screen_height": 600,
    "volume": 0.5,  # 音量设置 (0.0 到 1.0)
    "font": "SimHei",
    "key_bindings": {
        "player1": {
            "left": "LEFT",
            "right": "RIGHT",
            "up": "UP",
            "down": "DOWN",
            "shoot": "SPACE"
        },
        "player2": {
            "left": "A",
            "right": "D",
            "up": "W",
            "down": "S",
            "shoot": "F"
        }
    },
    "player": {
        "lives": 3,
        "max_speed": 5,
        "acceleration": 0.2
    },
    "enemies": {
        "enemy_normal": {
            "speed": 2,
            "score": 100,
            "health": 1
        },
        "enemy_special": {
            "speed": 3,
            "score": 200,
            "health": 2
        },
        "enemy_boss": {
            "speed": 1,
            "score": 1000,
            "health": 10
        }
    },
    "enemy_spawn_rate": 1.0  # 每秒生成一个敌人
}

# 保存上次修改时间
_last_modified_time = 0

CONFIG_PATH = os.path.join("../config", "settings.json")

def get_key_constant(key_name):
    """将按键名称转换为 pygame 按键常量"""
    return KEY_MAPPING.get(key_name, key_name)

def load_config():
    """加载配置文件，如果文件不存在则生成默认配置"""
    global _last_modified_time
    try:
        # 检查文件是否存在
        if not os.path.exists(CONFIG_PATH):
            save_config(DEFAULT_CONFIG)
            print("配置文件未找到，已生成默认配置文件。")
            return DEFAULT_CONFIG

        # 检查文件是否被修改
        current_modified_time = os.path.getmtime(CONFIG_PATH)
        if current_modified_time == _last_modified_time:
            # 文件未修改，返回当前配置
            with open(CONFIG_PATH, "r", encoding="utf-8") as f:
                return json.load(f)

        # 文件已修改，更新修改时间并加载新配置
        _last_modified_time = current_modified_time
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            config = json.load(f)
            # 确保所有必要的配置项都存在
            for key, value in DEFAULT_CONFIG.items():
                if key not in config:
                    config[key] = value
                elif key == "key_bindings":
                    # 确保按键绑定配置完整
                    for player, actions in DEFAULT_CONFIG[key].items():
                        if player not in config[key]:
                            config[key][player] = {}
                        for action, key_name in actions.items():
                            if action not in config[key][player]:
                                config[key][player][action] = key_name
            return config
    except Exception as e:
        print(f"读取配置文件失败，使用默认配置: {e}")
        return DEFAULT_CONFIG

def save_config(config):
    """保存配置到文件"""
    global _last_modified_time
    try:
        os.makedirs(os.path.dirname(CONFIG_PATH), exist_ok=True)
        with open(CONFIG_PATH, "w", encoding="utf-8") as f:
            json.dump(config, f, indent=4, ensure_ascii=False)
        _last_modified_time = os.path.getmtime(CONFIG_PATH)
    except Exception as e:
        print(f"Error saving config: {e}")

def reset_to_default():
    """重置配置为默认"""
    save_config(DEFAULT_CONFIG)
    print("配置已重置为默认值。")

def update_key_binding(player, action, key):
    """更新按键绑定"""
    config = load_config()
    if config:
        config["key_bindings"][player][action] = key
        save_config(config)
        return True
    return False

def update_volume(volume):
    """更新音量设置"""
    config = load_config()
    if config:
        config["volume"] = max(0.0, min(1.0, volume))  # 确保音量在0.0到1.0之间
        save_config(config)
        return config["volume"]
    return None

