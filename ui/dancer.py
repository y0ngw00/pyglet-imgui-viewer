from fonts import Fonts
from keyframe import KeyFrameAnimation, KeyFrame, InterpolationType
from animation_layer import AnimationLayer
import imgui

from imgui_color import COLORS, ImguiColor

class Dancer:
    def __init__(self, character, position_scale = [1.0,1.0], radius = 10):
        self.target = character
        self.radius = radius
        self.position_scale = position_scale
        self.__clicked = False
        
        self.thick = 8
        self.x = 0 
        self.y = 0
        self.update_circle_pos()
                
        self.__group_idx = 0      
        self.group_idx_font = Fonts["group_idx_font"]["font"]
        self.dancer_label= Fonts["dancer_label"]["font"]
        
        self.root_keyframe = KeyFrameAnimation(InterpolationType.LINEAR)
        self.group_keyframe = KeyFrameAnimation(InterpolationType.STEP)
        self.add_group_keyframe(0)
        
    @property
    def get_name(self):
        return self.target.get_name
    
    @get_name.setter
    def set_name(self, name):
        self.target.set_name = name
    
    @property
    def get_group_index(self):
        return self.__group_idx
    
    @get_group_index.setter
    def set_group_index(self, idx):
        self.__group_idx = idx
    
    def is_picked(self,x,y)->bool:
        if (x-self.x)**2 + (y - self.y)**2 < self.radius**2:
            return True
        return False
    
    def is_selected(self):
        return self.target.is_selected()
    
    @property
    def get_is_clicked(self):
        return self.__clicked
    
    @get_is_clicked.setter
    def set_is_clicked(self, clicked):
        self.__clicked = clicked
        self.target.select(clicked)
        
    def get_character_pos(self):
        return self.target.get_position()
    
    def get_character_root_pos(self):
        return self.target.get_root_position()
    
    def get_motion_condition(self, nframe):        
        return self.target.get_motion_condition(nframe)
        
    def update_circle_pos(self):
        position = self.get_character_pos()
        self.x = self.position_scale[0] * position[0]
        self.y = self.position_scale[1] * position[2]

    def add_root_keyframe(self, start, last) -> tuple([KeyFrame, KeyFrame]):
        prev_pos = self.get_character_pos()
        if len(self.root_keyframe.keyframes) > 0:
            prev_pos = self.root_keyframe.interpolate_position(start)
        start_keyframe = KeyFrame(start, prev_pos)
        self.root_keyframe.add_keyframe(start_keyframe)
        
        curr_pos = self.get_character_pos()
        last_keyframe = KeyFrame(last, curr_pos)
        self.root_keyframe.add_keyframe(last_keyframe)
        
        return start_keyframe, last_keyframe
        
    def add_group_keyframe(self, frame) -> None:
        keyframe = KeyFrame(frame, self.get_group_index)
        self.group_keyframe.add_keyframe(keyframe)
        
    def clear_root_keyframe(self) -> None:
        self.root_keyframe.clear_keyframe()
        
    def clear_group_keyframe(self) -> None:
        self.group_keyframe.clear_keyframe()
        
    def animate(self, frame):
        if len(self.root_keyframe.keyframes) > 0 and self.target is not None:
            position = self.root_keyframe.interpolate_position(frame)
            self.target.set_position(position)
            
        if len(self.group_keyframe.keyframes) > 0 and self.target is not None:
            group_idx = self.group_keyframe.interpolate_position(frame)
            self.set_group_index = group_idx
                    
    def render(self,draw_list, x, y, frame):
        color = imgui.get_color_u32_rgba(1,1,0,1) if self.target.is_selected() else imgui.get_color_u32_rgba(1,1,1,1)                 
        draw_list.add_circle_filled(x+self.x, y+self.y, radius = self.radius ,col = color)

        # Dancer group index
        boundary_color = ImguiColor.from_name(COLORS[self.__group_idx])
        draw_list.add_circle(x+self.x, y+self.y, radius = self.radius,col = boundary_color.get_color(), thickness = self.thick)
        
        with imgui.font(self.group_idx_font):
            text_color = imgui.get_color_u32_rgba(0,0,0,1)
            text_size = imgui.calc_text_size(str(self.__group_idx))
            draw_list.add_text(x+self.x-text_size.x/2, y+self.y-text_size.y/2, col = text_color, text = str(self.__group_idx))
        
        # Dancer name
        with imgui.font(self.dancer_label):
            text_size = imgui.calc_text_size(self.get_name)
            draw_list.add_text(x+self.x-text_size.x/2, y+self.y+self.radius+text_size.y/2, col = color, text = self.get_name)
        
    def translate(self, dx, dy):
        self.x +=dx
        self.y +=dy
        
        pos_diff = [dx/self.position_scale[0], 0, dy/self.position_scale[1]]
        self.target.translate(pos_diff)

