from fonts import Fonts
from keyframe import KeyFrameAnimation, KeyFrame
import imgui

class DancerCircle:
    def __init__(self, character, xsize_box, ysize_box, position_scale = 1, radius = 10):
        self.target = character
        self.radius = radius
        self.position_scale = position_scale
        self.__clicked = False
        self.pose_keyframe = KeyFrameAnimation()
        self.sync_keyframe = KeyFrameAnimation()
        
        self.thick = 5
        self.x = 0 
        self.y = 0
        self.update_circle_pos()
                
        self.__name = character.get_name()
        self.__group_idx = 1
        
              
        self.group_idx_font = Fonts["group_idx_font"]["font"]
        self.dancer_label= Fonts["dancer_label"]["font"]

    @property
    def get_name(self):
        return self.__name
    
    @get_name.setter
    def set_name(self, name):
        self.__name = name
    
    @property
    def get_group_index(self):
        return self.__group_idx
    
    @get_group_index.setter
    def set_group_index(self, idx):
        self.__group_idx = idx
        
    @property
    def get_is_clicked(self):
        return self.__clicked
    
    @get_is_clicked.setter
    def set_is_clicked(self, clicked):
        self.__clicked = clicked
        
    def get_character_pos(self):
        return self.target.get_root_position()
    
    def update_circle_pos(self):
        position = self.get_character_pos()
        self.x = self.position_scale * position[0]
        self.y = self.position_scale * position[2]

    def add_keyframe(self, frame) -> None:
        keyframe = KeyFrame(frame, self.get_character_pos())
        self.pose_keyframe.add_keyframe(keyframe)
        
    def add_sync_keyframe(self, frame) -> None:
        keyframe = KeyFrame(frame, self.get_character_pos())
        self.sync_keyframe.add_keyframe(keyframe)
        
    def animate(self, frame):
        if len(self.pose_keyframe.keyframes) > 0 and self.target is not None:
            position = self.pose_keyframe.interpolate_position(frame)
            self.target.set_position(position)
        
        self.update_circle_pos()
        
    def render(self,draw_list, x, y, frame):
        color =  imgui.get_color_u32_rgba(1,1,1,1)
        if len(self.sync_keyframe.keyframes) > 1:
            left, right = self.sync_keyframe.get_nearest_keyframe(frame)
            if left %2 ==0 and right %2 ==1:
                color = imgui.get_color_u32_rgba(1,0.7,0,1)                     
        if self.target.is_selected():
            color = imgui.get_color_u32_rgba(1,1,0,1)
            
        draw_list.add_circle(x+self.x, y+self.y, radius = self.radius,col = color, thickness = self.thick)
        
        # Dancer group index
        with imgui.font(self.group_idx_font):
            text_size = imgui.calc_text_size(str(self.__group_idx))
            draw_list.add_text(x+self.x-text_size.x/2, y+self.y-text_size.y/2, col = color, text = str(self.__group_idx))
        
        # Dancer name
        with imgui.font(self.dancer_label):
            text_size = imgui.calc_text_size(self.__name)
            draw_list.add_text(x+self.x-text_size.x/2, y+self.y+self.radius+text_size.y/2, col = color, text = self.__name)
        
    def translate(self, dx, dy):
        self.x +=dx
        self.y +=dy
        
        pos_diff = [dx/self.position_scale, 0, dy/self.position_scale]
        self.target.translate(pos_diff)

