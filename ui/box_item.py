import imgui
import imgui.core

from enum_list import Boundary
class BoxItem:
    def __init__(self):
        self.x_origin = 0
        self.y_origin = 0
        self.xsize_box = 0
        self.ysize_box = 0
        
    def update_position(self,x,y,xsize_box,ysize_box):
        self.x_origin = x
        self.y_origin = y
        self.xsize_box = xsize_box
        self.ysize_box = ysize_box
        return
        
    def draw_box(self, draw_list, color, rounding, thickness):
        draw_list.add_rect(upper_left_x = self.x_origin,
                           upper_left_y = self.y_origin,
                           lower_right_x = self.x_origin+self.xsize_box,
                           lower_right_y = self.y_origin+self.ysize_box,
                           col=color,
                           rounding = rounding,
                           thickness = thickness)
        return
    
    def draw_box_filled(self, draw_list, color, rounding):
        draw_list.add_rect_filled(upper_left_x = self.x_origin,
                                  upper_left_y = self.y_origin,
                                  lower_right_x = self.x_origin+self.xsize_box,
                                  lower_right_y = self.y_origin+self.ysize_box,
                                  col=color,
                                  rounding = rounding)
        return
    
    def is_picked(self,x,y)->bool:
        if self.x_origin<=x<=self.x_origin+self.xsize_box and self.y_origin<=y<=self.y_origin+self.ysize_box:
            return True
        return False
    
    def is_boundary_picked(self,x)->bool:
        if self.x_origin-5<=x<=self.x_origin+5:
            return Boundary.Left
        
        elif self.x_origin+self.xsize_box-5<=x<=self.x_origin+self.xsize_box+5:
            return Boundary.Right
        
        else: return None
