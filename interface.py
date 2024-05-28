import sys
import os
from pathlib import Path
from datetime import datetime

CURR_PATH = os.path.dirname(os.path.abspath(__file__))
PARENT_PATH = os.path.dirname(CURR_PATH)+"/"
sys.path.insert(0, PARENT_PATH)

import pyglet
import imgui
import imgui.core
from imgui.integrations.pyglet import create_renderer

import tkinter as tk
from tkinter import filedialog

import loader

class UI:
    def __init__(self, window):
        imgui.create_context()
        imgui.get_io().display_size = 1920, 1080
        imgui.get_io().fonts.get_tex_data_as_rgba32()
        self.impl = create_renderer(window)
        
        self.new_font = imgui.get_io().fonts.add_font_from_file_ttf("model/PublicSans-SemiBold.ttf", 20)
        self.impl.refresh_font_texture()
        imgui.new_frame()  
        imgui.end_frame()

        self.window = window
        self.scene = window.scene
        self.root = tk.Tk()
        self.root.withdraw()
        # Window variables
        self.test_input = 0
        self.selected_audio_file = ""
        self.selected_network_file = ""
        
        self.pos_idx=0
        self.pos_list = [[0,0,0], [1.5,0,-1.5], [-1.5,0,-1.5], [3.0,0,-3.0],[-3.0,0,-3.0] ]
        
        self.circles = []
        self.last_clicked_item = None
        
        self.x_box = 0
        self.y_box = 0
        
        self.xsize_box = 300
        self.ysize_box = 300

    def render(self):
    
        imgui.render()
        self.impl.render(imgui.get_draw_data())
        imgui.new_frame()

        self.render_main_menu()
        self.render_ui_window()

        imgui.end_frame()
        
    def draw_formation_interface(self, x, y):
        if imgui.begin("Drawing Interface", True, imgui.WINDOW_NO_MOVE):
            draw_list = imgui.get_window_draw_list()
            canvas_pos = imgui.get_cursor_screen_pos()  # Get the position of the canvas window

            layout_padding = [10,10]
            x_origin = canvas_pos.x+layout_padding[0]
            y_origin = canvas_pos.y+layout_padding[1]
            
            self.x_box = x_origin
            self.y_box = y_origin
            
            draw_list.add_rect(x_origin, y_origin, x_origin+self.xsize_box, y_origin+self.ysize_box, imgui.get_color_u32_rgba(1,0,0,1), rounding=5, thickness=3)
            # Draw a line
            # draw_list.add_line((10, 10), (100, 100), imgui.get_color_u32((255, 255, 0, 255)), 1)

            # Draw a dot
            for circle in self.circles:
                # if circle.get_is_clicked:
                #     circle.x = x - canvas_pos.x
                #     circle.y = y - canvas_pos.y
                color =  imgui.get_color_u32_rgba(1,1,1,1)
                if circle.get_is_clicked:
                    color = imgui.get_color_u32_rgba(1,1,0,1)
                
                draw_list.add_circle(x_origin+circle.x, y_origin+circle.y, circle.radius,color, thickness=3)

            imgui.end()
        return
    
    def draw_keyframe_interface(self):
        if imgui.begin("Keyframe editor", True):
            draw_list = imgui.get_window_draw_list()
            canvas_pos = imgui.get_cursor_screen_pos()  # Get the position of the canvas window

            changed, self.window.frame = imgui.slider_float("Frame", self.window.frame, 0.0, self.window.max_frame)
            slider_pos = (canvas_pos.x + 10, canvas_pos.y + 40)

            for idx, circle in enumerate(self.circles):
                imgui.text("Dancer '{}'".format(idx))
                canvas_pos = imgui.get_cursor_pos()
                canvas_screen_pos = imgui.get_cursor_screen_pos()
                draw_list.add_rect(canvas_screen_pos.x, canvas_screen_pos.y, canvas_screen_pos.x+300, canvas_screen_pos.y+20, imgui.get_color_u32_rgba(1,1,1,1), rounding=5, thickness=3)
                for keyframe in circle.keyframe_anim.keyframes:
                    x = canvas_screen_pos.x +  self.xsize_box * keyframe.frame / self.window.max_frame
                    draw_list.add_line(x, canvas_screen_pos.y, x, canvas_screen_pos.y+20, imgui.get_color_u32_rgba(1, 0, 0, 1))
                imgui.set_cursor_pos((10, canvas_pos.y+40))


            imgui.end()
            
            if changed:
                self.update_ui(is_animate = changed)
        return

    def render_main_menu(self):
        file_ext = ""
        file_descriptions = ""
        is_open_file = False
        if imgui.begin_main_menu_bar():
            if imgui.begin_menu("File"):
                imgui.menu_item("(demo menu)", None, False, False)
                
                if imgui.menu_item("New")[0]:
                    pass
                
                if imgui.begin_menu("Open"):
                #     pass
                    if imgui.menu_item("BVH", None)[0]:
                        file_descriptions = "BVH Files"
                        file_ext = "*.bvh"
                        is_open_file = True

                    if imgui.menu_item("GLTF", None)[0]:
                        file_descriptions = "GLTF Files"
                        file_ext = ["*.gltf","*.glb"]
                        is_open_file = True

                    imgui.end_menu()
                imgui.separator()
                
                if imgui.begin_menu("Options"):
                    enabled = imgui.checkbox("Enabled", True)[1]
                    
                    imgui.begin_child("child", 0, 60, True)
                    for i in range(10):
                        imgui.text(f"Scrolling Text {i}")
                    imgui.end_child()
                    
                    f = imgui.slider_float("Value", 0.5, 0.0, 1.0)[1]
                    f = imgui.input_float("Input", f, 0.1)[1]
                    
                    items = ["Yes", "No", "Maybe"]
                    n = imgui.combo("Combo", 0, items)[1]
                    
                    imgui.end_menu()
                
                if imgui.menu_item("Checked", None, True)[0]:
                    pass
                
                if imgui.menu_item("Quit", "Alt+F4")[0]:
                    self.window.quit()
                
                imgui.end_menu()
            
            imgui.end_main_menu_bar()


        if is_open_file is True:
            selected_file = ""
            imgui.open_popup("Open File")

            if imgui.begin_popup_modal("Open File", None, imgui.WINDOW_ALWAYS_AUTO_RESIZE)[0]:
                selected_file = self.render_file_dialog(file_descriptions, file_ext)

            imgui.end_popup()

            if selected_file:
                print(f"Open File: {selected_file}")
                self.open_file(selected_file)

    def render_ui_window(self):   
        x,y = imgui.get_mouse_pos()
        
        self.draw_formation_interface(x,y)
        
        self.draw_keyframe_interface()

        imgui.begin("Test Window")
        imgui.text("This is the test window.")
        changed, self.window.frame = imgui.input_int("Animation frame", self.window.frame)

        # clicked, value = imgui.input_text("Text Input", "")

        with imgui.font(self.new_font):
            imgui.text("Current number of characters: {}".format(len(self.circles)))
            imgui.same_line()
            if imgui.button("Add character(GLTF,GLB)"):
                file_descriptions = "3D model file(.gltf, .glb)"
                file_ext = ["*.gltf","*.glb"]
                selected_character_file = self.render_file_dialog(file_descriptions, file_ext)
                if selected_character_file:
                    print(f"Open File: {selected_character_file}")
                    self.open_file(selected_character_file)

            if imgui.button("Select audio file"):
                file_descriptions = "Audio files (.wav)"
                file_ext = "*.wav"
                selected_audio_file = self.render_file_dialog(file_descriptions, file_ext)
                # if selected_audio_file:
                #     print(f"Open File: {selected_audio_file}")
                #     self.open_file(selected_audio_file)
                self.selected_audio_file = str(selected_audio_file)
            
            imgui.text(self.selected_audio_file)
            imgui.spacing()
            
            if imgui.button("Select model checkpoint"):
                file_descriptions = "checkpoint file (.ckpt)"
                file_ext = "*.ckpt"
                self.selected_network_file = self.render_file_dialog(file_descriptions, file_ext)
            imgui.text(self.selected_network_file)
            imgui.spacing()
            
            if imgui.button("Generate!"):
                self.generate_motion()
        imgui.end()

    def is_ui_active(self):
        return imgui.is_any_item_active()
    
    def generate_motion(self):
        output_path = os.path.dirname(self.selected_audio_file)+"/" + self.selected_audio_file.split("/")[-1].split(".")[0] + ".bvh"
        synthesize(self.selected_audio_file, self.selected_network_file, output_path)
        self.open_file(output_path)

    def render_file_dialog(self, file_descriptions,file_ext):
        file_types = [(file_descriptions, file_ext)]
        selected_file = filedialog.askopenfilename(filetypes=file_types)
        return selected_file
    
    def open_file(self, file_path):
        ext = file_path.split('.')[-1]
        name = file_path.split('/')[-1]
        if ext == "bvh":
            character = loader.load_bvh(file_path)
            character.set_scale([0.1,0.1,0.1])

        elif ext == "gltf" or ext == "glb":
            character = loader.load_gltf(file_path)
            character.set_position(self.pos_list[self.pos_idx])
        
        if character is not None:
            self.scene.add_character(character)
            self.circles.append(DancerCircle(character,self.xsize_box, self.ysize_box, 10))
            self.pos_idx+=1
        return
    
    def on_key_press(self, symbol, modifiers) -> None:
        pass
                    
    def on_key_release(self, symbol, modifiers) -> None:
        if symbol == pyglet.window.key.F:
            if modifiers == pyglet.window.key.MOD_CTRL:
                for circle in self.circles:
                    circle.add_keyframe(KeyFrame(self.window.frame, (circle.x, circle.y)))
            else:
                if isinstance(self.last_clicked_item, DancerCircle): 
                    self.last_clicked_item.add_keyframe(KeyFrame(self.window.frame, (self.last_clicked_item.x, self.last_clicked_item.y)))
                    
        
        dx = 5 if symbol==pyglet.window.key.D else -5 if symbol==pyglet.window.key.A else 0
        dy = 5 if symbol==pyglet.window.key.S else -5 if symbol==pyglet.window.key.W else 0
        if isinstance(self.last_clicked_item, DancerCircle): 
            self.last_clicked_item.translate(dx, dy)

    def on_mouse_down(self, x, y, button, modifier) -> None:
        new_y = self.window.height - y
        for circle in self.circles:
            if (x-self.x_box-circle.x)**2 + (new_y - self.y_box-circle.y)**2 < circle.radius**2:
                circle.set_is_clicked = True
                break

    def on_mouse_release(self, x, y, button, modifier) -> None:
        for circle in self.circles:
            if circle.get_is_clicked:
                self.last_clicked_item = circle
            circle.set_is_clicked = False

    def on_mouse_drag(self, x, y, dx, dy, button, modifier) -> None:
        for circle in self.circles:
            if circle.get_is_clicked:
                circle.translate(dx, -dy)
                
    def update_ui(self, is_animate) -> None:
        
        if is_animate:
            for circle in self.circles:
                circle.animate(self.window.frame)
                

class DancerCircle:
    def __init__(self, character, xsize_box, ysize_box, position_scale = 10, radius = 10):
        self.target = character
        self.radius = radius
        self.position_scale = position_scale
        self.__clicked = False
        self.keyframe_anim = KeyFrameAnimation()
        
        position = character.get_position()
        self.x = xsize_box/2 + position_scale * position[0]
        self.y = ysize_box/2 + position_scale * position[2]

    @property
    def get_is_clicked(self):
        return self.__clicked
    
    @get_is_clicked.setter
    def set_is_clicked(self, clicked):
        self.__clicked = clicked

    def add_keyframe(self, keyframe):
        self.keyframe_anim.add_keyframe(keyframe)
        
    def animate(self, frame):
        if len(self.keyframe_anim.keyframes) == 0:
            return
        
        position = self.keyframe_anim.interpolate_position(frame)
        self.translate(position[0] - self.x, position[1] - self.y)
        
    def translate(self, dx, dy):
        self.x +=dx
        self.y +=dy
        
        pos_before = self.target.get_position()
        pos_after = [pos_before[0] + dx / self.position_scale, pos_before[1], pos_before[2] + dy / self.position_scale]
        self.target.set_position(pos_after)



class KeyFrameAnimation:
    def __init__(self):
        self.keyframes = []

    def add_keyframe(self, keyframe):
        if len(self.keyframes) == 0:
            self.keyframes.append(keyframe)
            return
        
        for i, kf in enumerate(self.keyframes):
            if keyframe<kf:
                self.keyframes.insert(i, keyframe)
                return
            elif keyframe==kf:
                self.keyframes[i] = keyframe
                return
        
        self.keyframes.append(keyframe)
        return

    def interpolate_position(self, frame):
        if len(self.keyframes) == 0:
            raise ValueError("No keyframes")
        
        if frame <= self.keyframes[0].frame:
            position = self.keyframes[0].position
        elif frame >= self.keyframes[-1].frame:
            position = self.keyframes[-1].position
        else:
            # Find the two keyframes that the frame is between
            for i in range(len(self.keyframes) - 1):
                if self.keyframes[i].frame <= frame < self.keyframes[i + 1].frame:
                    break
            else:
                raise ValueError("Frame is not valid")

            # Interpolate the position
            t = (frame - self.keyframes[i].frame) / (self.keyframes[i + 1].frame - self.keyframes[i].frame)
            position = [self_pos * (1 - t) + other_pos * t for self_pos, other_pos in zip(self.keyframes[i].position, self.keyframes[i + 1].position)]

        return position

class KeyFrame:
    def __init__(self, frame, position):
        self.frame = frame
        self.position = position

    def __eq__(self, other):
        if isinstance(other, KeyFrame):
            return self.frame == other.frame
        elif isinstance(other, int):
            return self.frame == other
        else:
            raise ValueError("Unsupported operand type for <: '{}' and '{}'".format(type(self), type(other)))
        
    def __lt__(self, other):
        if isinstance(other, KeyFrame):
            return self.frame < other.frame
        elif isinstance(other, int):
            return self.frame < other
        else:
            raise TypeError("Unsupported operand type for <: '{}' and '{}'".format(type(self), type(other)))

    def __gt__(self, other):
        if isinstance(other, KeyFrame):
            return self.frame > other.frame
        elif isinstance(other, int):
            return self.frame > other
        else:
            raise TypeError("Unsupported operand type for >: '{}' and '{}'".format(type(self), type(other)))
