from keyframe import KeyFrameAnimation

class DancerCircle:
    def __init__(self, character, xsize_box, ysize_box, position_scale = 1, radius = 10):
        self.target = character
        self.radius = radius
        self.position_scale = position_scale
        self.__clicked = False
        self.pose_keyframe = KeyFrameAnimation()
        self.sync_keyframe = KeyFrameAnimation()
        
        position = character.get_position()
        self.x = xsize_box/2 + position_scale * position[0]
        self.y = ysize_box/2 + position_scale * position[2]

    @property
    def get_is_clicked(self):
        return self.__clicked
    
    @get_is_clicked.setter
    def set_is_clicked(self, clicked):
        self.__clicked = clicked
        
    def get_character_pos(self):
        return self.target.get_position()

    def add_keyframe(self, keyframe) -> None:
        self.pose_keyframe.add_keyframe(keyframe)
        
    def add_sync_keyframe(self, keyframe) -> None:
        self.sync_keyframe.add_keyframe(keyframe)
        
    def animate(self, frame):
        if len(self.pose_keyframe.keyframes) == 0:
            return
        
        position = self.pose_keyframe.interpolate_position(frame)
        self.translate(position[0] - self.x, position[1] - self.y)
        
    def translate(self, dx, dy):
        self.x +=dx
        self.y +=dy
        
        pos_before = self.target.get_position()
        pos_after = [pos_before[0] + dx / self.position_scale, pos_before[1], pos_before[2] + dy / self.position_scale]
        self.target.set_position(pos_after)

