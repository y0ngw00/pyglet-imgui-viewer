import imgui
import imgui.core

class FrameBar:
    def __init__(self, parent,length, x_offset=0, y_offset=0, color = None):
        self.parent_window = parent
        self.length = length
        self.color = color
        self.__selected = False
        
        self.x_offset = x_offset
        self.y_offset = y_offset
        self.__bar_pos = 0
        self.__x_origin = 0
        self.__y_origin = 0
        
        if color is None:
            self.color = imgui.get_color_u32_rgba(1,0,0,1)
    
    def render(self, draw_list, pos):
        self.__bar_pos = pos
        draw_list.add_line(self.__x_origin+self.__bar_pos, 
                           self.__y_origin, 
                           self.__x_origin+self.__bar_pos, 
                           self.__y_origin+self.length, 
                           self.color, 
                           2)
        draw_list.add_triangle_filled(self.__x_origin+self.__bar_pos,
                                      self.__y_origin,
                                    self.__x_origin+self.__bar_pos-10, 
                                    self.__y_origin-10,
                                    self.__x_origin+self.__bar_pos+10,
                                    self.__y_origin-10,
                                    self.color)
        
    def update_position(self,x,y):
        self.__x_origin = x
        self.__y_origin = y
        return
        
    def is_picked(self,x,y)->bool:
        if x>= self.__x_origin+self.__bar_pos-10 and x <=self.__x_origin+self.__bar_pos+10:
            if y>=self.__y_origin-10 and y<=self.__y_origin:
                return True
        return False
    
    @property
    def selected(self):
        return self.__selected
    
    def select(self, selected, modifier = None):
        self.__selected = selected
        