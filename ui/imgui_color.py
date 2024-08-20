import imgui
import imgui.core

COLORS = ['white','red','green','blue','yellow','purple','orange','cyan','black']
IMGUI_COLOR_RGB = {
    'white': (1,1,1,1),
    'red': (1,0,0,1),
    'green': (0,1,0,1),
    'blue': (0,0,1,1),
    'yellow': (1,1,0,1),
    'purple': (1,0,1,1),
    'orange': (1,0.5,0,1),
    'cyan': (0,1,1,1),
    'black': (0,0,0,1)
}

class ImguiColor:
    def __init__(self, r, g, b, a):
        self.r = r
        self.g = g
        self.b = b
        self.a = a
        
    @classmethod
    def from_name(cls, name):
        r, g, b, a = IMGUI_COLOR_RGB[name]
        return cls(r, g, b, a)

    def __call__(self):
        return imgui.get_color_u32_rgba(self.r, self.g, self.b, self.a)
    
    def get_color(self):
        return imgui.get_color_u32_rgba(self.r, self.g, self.b, self.a)