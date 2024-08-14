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
        self.x_origin = 0
        self.y_origin = 0
        
        if color is None:
            self.color = imgui.get_color_u32_rgba(1,0,0,1)
    
    def render(self, draw_list, frame):
        self.x_origin = self.parent_window.x_origin + self.x_offset
        self.y_origin = self.parent_window.y_origin
        draw_list.add_line(self.x_origin+frame, 
                           self.y_origin, 
                           self.x_origin+frame, 
                           self.y_origin+self.length, 
                           self.color, 
                           2)
        draw_list.add_triangle_filled(self.x_origin+frame,
                                      self.y_origin,
                                    self.x_origin+frame-10, 
                                    self.y_origin-10,
                                    self.x_origin+frame+10,
                                    self.y_origin-10,
                                    self.color)
        
    def is_picked(self,x,y,frame)->bool:
        if self.x_origin+frame-10<=x<=self.x_origin+frame+10:
            if self.y_origin-10<=y<=self.y_origin:
                return True
        return False
    
    @property
    def selected(self):
        return self.__selected
    
    def select(self, selected, modifier = None):
        self.__selected = selected
        