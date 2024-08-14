import imgui
import imgui.core

from enum_list import Boundary
class BoxItem:
    def __init__(self):
        self.__x_origin = 0
        self.__y_origin = 0
        self.__xsize_box = 0
        self.__ysize_box = 0
        
    def update_position(self,x,y,xsize_box,ysize_box):
        self.__x_origin = x
        self.__y_origin = y
        self.__xsize_box = xsize_box
        self.__ysize_box = ysize_box
        return
        
    def draw_box(self, draw_list, color, rounding, thickness):
        draw_list.add_rect(upper_left_x = self.__x_origin,
                           upper_left_y = self.__y_origin,
                           lower_right_x = self.__x_origin+self.__xsize_box,
                           lower_right_y = self.__y_origin+self.__ysize_box,
                           col=color,
                           rounding = rounding,
                           thickness = thickness)
        return
    
    def draw_box_filled(self, draw_list, color, rounding):
        draw_list.add_rect_filled(upper_left_x = self.__x_origin,
                                  upper_left_y = self.__y_origin,
                                  lower_right_x = self.__x_origin+self.__xsize_box,
                                  lower_right_y = self.__y_origin+self.__ysize_box,
                                  col=color,
                                  rounding = rounding)
        return
    
    def is_picked(self,x,y)->bool:
        if self.__x_origin<=x<=self.__x_origin+self.__xsize_box and self.__y_origin<=y<=self.__y_origin+self.__ysize_box:
            return True
        return False
    
    def is_boundary_picked(self,x)->bool:
        if self.__x_origin-5<=x<=self.__x_origin+5:
            return Boundary.Left
        
        elif self.__x_origin+self.__xsize_box-5<=x<=self.__x_origin+self.__xsize_box+5:
            return Boundary.Right
        
        else: return None
        
    @property
    def x_origin(self):
        return self.__x_origin
    
    @property
    def y_origin(self):
        return self.__y_origin
    
    @property
    def xsize_box(self):
        return self.__xsize_box
    
    @property
    def ysize_box(self):
        return self.__ysize_box
