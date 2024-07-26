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
        
        self.xsize_box = xsize_box
        self.ysize_box = ysize_box
        
        self.x = 0 
        self.y = 0
        self.update_circle_pos()

    @property
    def get_is_clicked(self):
        return self.__clicked
    
    @get_is_clicked.setter
    def set_is_clicked(self, clicked):
        self.__clicked = clicked
        
    def get_character_pos(self):
        return self.target.get_position()
    
    def update_circle_pos(self):
        position = self.get_character_pos()
        self.x = self.xsize_box/2 + self.position_scale * position[0]
        self.y = self.ysize_box/2 + self.position_scale * position[2]

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
            
        draw_list.add_circle_filled(x+self.x, y+self.y, self.radius,color)
        
    def translate(self, dx, dy):
        self.x +=dx
        self.y +=dy
        
        pos_diff = [dx/self.position_scale, 0, dy/self.position_scale]
        self.target.translate(pos_diff)

