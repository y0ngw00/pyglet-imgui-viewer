import copy

import pyglet

import imgui
import imgui.core
from imgui.integrations.pyglet import create_renderer


class KeyframeViewer:
    def __init__(self, parent_window):
        self.xsize_box = 500
        self.ysize_box = 500
                
                
        self.parent_window = parent_window
        self.max_frame = 500
        
        self.keyframe_animate = True
        pass

    def render(self):
        if imgui.begin("Keyframe editor", True, flags=imgui.WINDOW_NO_MOVE):
            draw_list = imgui.get_window_draw_list()
            canvas_pos = imgui.get_cursor_screen_pos()  # Get the position of the canvas window

            changed, frame = imgui.slider_float("Frame", self.parent_window.get_frame(), 0.0, self.max_frame)
                
            imgui.same_line()
            check_clicked, bAnimate = imgui.checkbox("Animate", self.keyframe_animate)
            if check_clicked is True:
                self.keyframe_animate = bAnimate
            slider_pos = (canvas_pos.x + 10, canvas_pos.y + 40)

            for idx, circle in enumerate(self.parent_window.get_circles()):
                imgui.text("Dancer '{}'".format(idx))
                canvas_x, canvas_y= copy.deepcopy(imgui.get_cursor_screen_pos())
                canvas_x += 80
                
                draw_list.add_rect(canvas_x, canvas_y, canvas_x+300, canvas_y+20, imgui.get_color_u32_rgba(1,1,1,1), rounding=5, thickness=3)
                for idx, keyframe in enumerate(circle.pose_keyframe.keyframes):
                    x = canvas_x +  self.xsize_box * keyframe.frame / self.max_frame
                    
                    if idx > 0 and keyframe.position != circle.pose_keyframe.keyframes[idx-1].position:
                        prev_x = canvas_x +  self.xsize_box * circle.pose_keyframe.keyframes[idx-1].frame / self.max_frame
                        draw_list.add_rect_filled(prev_x, canvas_y, x, canvas_y+20, imgui.get_color_u32_rgba(0.7, 0, 0, 1))
                    else:
                        draw_list.add_line(x, canvas_y, x, canvas_y+20, imgui.get_color_u32_rgba(0.7, 0, 0, 1))
                        
                imgui.text("trajectory")

                canvas_y += 30
                draw_list.add_rect(canvas_x, canvas_y, canvas_x+300, canvas_y+20, imgui.get_color_u32_rgba(1,1,1,1), rounding=5, thickness=3)
                for idx, keyframe in enumerate(circle.sync_keyframe.keyframes):
                    x = canvas_x +  self.xsize_box * keyframe.frame / self.max_frame
                    
                    if idx > 0 and idx %2 ==1:
                        prev_x = canvas_x +  self.xsize_box * circle.sync_keyframe.keyframes[idx-1].frame / self.max_frame
                        draw_list.add_rect_filled(prev_x, canvas_y, x, canvas_y+20, imgui.get_color_u32_rgba(1, 0.6, 0, 1))
                    else:
                        draw_list.add_line(x, canvas_y, x, canvas_y+20, imgui.get_color_u32_rgba(1, 0.6, 0, 1))
                imgui.spacing() 
                imgui.spacing()
                imgui.spacing()
                imgui.text("synchronize")
                
                canvas_pos = imgui.get_cursor_pos()
                imgui.set_cursor_pos((10, canvas_pos.y+40))
            
            imgui.end()
          
    @property  
    def is_keyframe_animate(self):
        return self.keyframe_animate
            
        return changed