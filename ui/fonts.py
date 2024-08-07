import imgui
import imgui.core

Fonts = {
    "group_idx_font": {
        "font": None,
        "path": "pyglet_render/data/PublicSans-SemiBold.ttf",
        "size": 30
    },
    "dancer_label":{
        "font": None,
        "path": "pyglet_render/data/PublicSans-SemiBold.ttf",
        "size": 15
    },
    "button_font_bold":{
        "font": None,
        "path": "pyglet_render/data/PublicSans-SemiBold.ttf",
        "size": 20
    },
    "sequence_name":{
        "font": None,
        "path": "pyglet_render/data/PublicSans-SemiBold.ttf",
        "size": 20
    },
}

def initialize_imgui_fonts():    
    for font in Fonts:
        Fonts[font]["font"] = imgui.get_io().fonts.add_font_from_file_ttf(Fonts[font]["path"], Fonts[font]["size"])
