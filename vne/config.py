import os 

CONFIG = {
    "screen_width": 800,
    "screen_height": 600,
    "fullscreen": False,
    "font_name": "Arial",
    "font_size": 24,
    "name_font": "Arial",
    "name_font_size": 20,
    "bg_color": (0, 0, 0),   
    "dialogue_rect": { 
         "x": 0,
         "y": 480,
         "width": 800,
         "height": 120,
         "bg_color": (50, 50, 50),
         "border_color": (255, 255, 255)
    },
    "namebox_rect": { 
         "x": 0,    
         "y": 440,  
         "width": 200,
         "height": 40,
         "bg_color": (50, 50, 50),
         "border_color": (255, 255, 255)
    },
    "sprite_scale": 0.5,
    "bgm_channel": 0,
    "sfx_channel": 1,
    "bgm_volume": 0.6,
    "sfx_volume": 1.0 
}


key = bytes.fromhex(os.environ.get("VNE_KEY", ""))