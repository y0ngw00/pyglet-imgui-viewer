import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import glob

from typing import Tuple
from pathlib import Path

import pyglet
from pyglet.gl import *
from pyglet.math import Vec2

import imgui
import imgui.core
import cv2

from utils import process_poses, export_animated_mesh

from fonts import Fonts
from frame_bar import FrameBar
from box_item import BoxItem
from sequencer import Sequencer
from sequence import Sequence
import loader
class MotionCreator(BoxItem):
    def __init__(self, parent_window, x_pos, y_pos, x_size, y_size):
        super().__init__()
        self.parent_window = parent_window
        self.x_pos = x_pos
        self.y_pos = y_pos
        self.x_size = x_size
        self.y_size = y_size
        # self.update = False
        self.is_show = False
        
        self.control_frame = 0
        self.video_timestep = 0.5
        
        self.player = pyglet.media.Player()
        self.current_filepath = ""
        self.time_length_scale = 0
        self.sequence_width = 0
        self.sequence_pos_start = 0
        self.sequence_height = 200
        
        self.button_font_medium = Fonts["button_font_medium"]["font"]
        
        self.padding_x = 30
        self.video_sequence = Sequence("", 
                                       None, 
                                       self.sequence_pos_start, 
                                       self.sequence_height)
        
        self.frame_bar = FrameBar(self, length = 400,
                                x_offset= self.sequence_pos_start, 
                                y_offset = 500, 
                                color = imgui.get_color_u32_rgba(1,0,0,1))
        
        # Apply Motion popup
        self.checkbox_applied_dancers = [False for i in range(self.parent_window.get_num_dancers())]
        self.start_frame_applied = 0
        self.fbx_path = ""
            
    def render(self):
        x_scale, y_scale = imgui.get_io().display_size 
        x_pos = self.x_pos * x_scale
        y_pos = self.y_pos * y_scale
        x_size = self.x_size * x_scale
        y_size = self.y_size * y_scale
        imgui.set_next_window_position(x_pos, y_pos, imgui.ONCE)
        imgui.set_next_window_size(x_size, y_size, imgui.ONCE)
            
        if self.is_show is True:
            expanded, self.is_show = imgui.begin("Motion Creator", True)
            
            canvas_pos = imgui.get_window_position()
            self.update_position(x = canvas_pos.x, 
                                    y = canvas_pos.y,
                                    xsize_box = imgui.get_window_width()-40, 
                                    ysize_box = imgui.get_window_height()-40)
            
            self.sequence_width = self.xsize_box - 30

            if self.is_show:
                self.render_menu()
                
                if self.player.texture is not None:
                    texture = self.player.texture
                    aspect_ratio = texture.height /texture.width 
                    video_viewer_width = imgui.get_window_size()[0] - 30
                    video_viewer_height = video_viewer_width * aspect_ratio
                    imgui.begin_child("Video Window", video_viewer_width, video_viewer_height, border=True)   
                    imgui.image(texture.id, video_viewer_width, video_viewer_height)
                    imgui.end_child()
                else:
                    video_viewer_width,video_viewer_height = imgui.get_window_size()
                    imgui.begin_child("Video Window", self.xsize_box, video_viewer_height-500, border=True)   
                    imgui.end_child()
        
                # imgui.image(self.texture.id, 300, 300)
                # if self.player.source and self.player.source.video_format:
                    # self.player.get_texture().blit(0,0)
                    
                imgui.begin_child("Video Sequencer",  self.xsize_box, 300, border=True)   
                imgui.same_line(spacing=imgui.get_window_size()[0]/2 - 120)
                with imgui.font(self.button_font_medium):
                    if imgui.button("|<"):
                        self.goto_first()
                        self.player.pause()
                    imgui.same_line()
                    if imgui.button("Prev"):
                        self.prev()
                        self.player.pause()
                    imgui.same_line()
                    if self.player.playing is True:
                        if imgui.button("Stop"):
                            self.player.pause()
                    else:                
                        if imgui.button("Play"):
                            if len(self.video_sequence.children) > 0:
                                start_frame = self.video_sequence.children[0].frame_start
                                end_frame = self.video_sequence.children[0].frame_end
                                if self.control_frame < start_frame:
                                    self.control_frame = start_frame
                                if self.control_frame <= end_frame:
                                    time = self.control_frame * self.time_length_scale
                                    self.player.seek(time)
                                    self.player.play()
                            
                    imgui.same_line()      
                    if imgui.button("Next"):
                        self.next()
                        self.player.pause()
                    imgui.same_line() 
                    if imgui.button(">|"):
                        self.goto_end()
                        self.player.pause()
                        
                    imgui.text("Current : {:0.2f}".format(self.player.time))

                if self.player.playing is True:
                    self.control_frame = self.player.time / (self.time_length_scale + 1e-6)
                
                draw_list = imgui.get_window_draw_list()

                #Sequencer render
                self.video_sequence.render(0, 0)
                
                x, y = imgui.get_cursor_screen_pos()
                # Time line
                self.draw_time_line(draw_list, x, y-5)
                # Frame bar
                self.frame_bar.update_position(x, y)
                self.frame_bar.render(draw_list, self.control_frame)
                imgui.end_child()


            imgui.end()
                        
        # if self.parent_window.is_playing() is True:
        #     self.player.seek_next_frame()
            
    def show(self, is_show):
        self.is_show = is_show
        
    def prev(self):
        # curr_time = self.player.time
        self.control_frame -=1
        # self.player.seek(curr_time - self.video_timestep)
        
    def next(self):
        if self.player.time < self.player.source.duration:
            self.control_frame +=1
            # curr_time = self.player.time
            # self.player.seek(curr_time + self.video_timestep)
        return
        
    def goto_first(self):
        self.control_frame = self.video_sequence.children[0].frame_start
        # time = self.video_sequence.children[0].frame_start * self.time_length_scale
        # self.player.seek(time)
        
    def goto_end(self):
        self.control_frame = self.video_sequence.children[0].frame_end
        # time = self.video_sequence.children[0].frame_end * self.time_length_scale
        # self.player.seek(time)
        
    def on_eos(self):
        print("The player has finished playing its current source.")
        
    def render_menu(self):
        with imgui.font(self.button_font_medium):
            if imgui.button("Upload video"):
                file_path = self.parent_window.render_file_dialog("Video Files", ["*.mp4", "*.avi","*.mov" ,"*.wav"])
                if file_path:
                    self.load_video(file_path)
            imgui.same_line()
            if imgui.button("Clear"):
                self.clear()
            imgui.same_line()
            if imgui.button("Save video"):
                if self.current_filepath:
                    name, ext = os.path.splitext(self.current_filepath)
                    file_path = f"{name}_trim{ext}"
                    self.save_video(file_path)
            imgui.same_line()
            if imgui.button("Create motion"):
                self.create_motion()
            imgui.same_line()
            if imgui.button("Apply motion"):
                imgui.open_popup("Message: Apply motion")
            if imgui.begin_popup_modal("Message: Apply motion").opened:
                if self.fbx_path == "" or len(self.video_sequence.children) == 0:
                    imgui.text("No motion is generated.")
                    imgui.text("Please create motion first.")
                    imgui.dummy(0, imgui.get_content_region_available()[1] - imgui.get_text_line_height_with_spacing())
                    imgui.dummy((imgui.get_content_region_available()[0] - imgui.calc_text_size("OK")[0])/2,0)
                    imgui.same_line()
                    imgui.selectable("OK", width = 30)
                    imgui.end_popup()
                else:
                    _, self.start_frame_applied = imgui.input_int("Start frame", self.start_frame_applied)
                    imgui.text("Select dancers:")
                    imgui.separator()
                    dancers = self.parent_window.get_dancers()
                    num_dancers = self.parent_window.get_num_dancers()
                    if num_dancers > len(self.checkbox_applied_dancers):
                        self.checkbox_applied_dancers = [False for i in range(num_dancers)]
                    for idx, dancer in enumerate(dancers):
                        _, self.checkbox_applied_dancers[idx] = imgui.checkbox(dancer.get_name, self.checkbox_applied_dancers[idx])
                    imgui.dummy(0, imgui.get_content_region_available()[1] - imgui.get_text_line_height_with_spacing())
                    imgui.dummy((imgui.get_content_region_available()[0] - 100)/2,0)
                    imgui.same_line()
                    if imgui.selectable("Apply", width = 50)[0]:
                        self.apply_motion(self.start_frame_applied)
                    imgui.same_line()
                    imgui.selectable("Close", width = 50)
                    imgui.end_popup()
            
    def load_video(self, file_path):
        video = pyglet.media.load(file_path)
        self.current_filepath = file_path
        
        self.player.queue(video)
        self.player.seek(0)
        self.player.on_eos = self.on_eos
        
        self.time_length_scale = video.duration / self.sequence_width  # time seconds per 1 pixel
        self.video_sequence.fill_sequence(0, self.sequence_width)
        self.video_sequence.children[0].lock_translate(True)

    def clear(self):
        self.player.delete()
        self.player = pyglet.media.Player()
        self.video_sequence.clear_all_track()
        self.current_filepath = ""        
        self.time_length_scale = 0
        self.fbx_path = ""
        
    def save_video(self, file_path):
        # Could not find a way to save the video using pyglet. Used OpenCV instead.
        start_time = self.video_sequence.children[0].frame_start * self.time_length_scale
        end_time = self.video_sequence.children[0].frame_end * self.time_length_scale
        
        cap = cv2.VideoCapture(self.current_filepath)
        fps = cap.get(cv2.CAP_PROP_FPS)
        start_frame = int(start_time * fps)
        end_frame = int(end_time * fps)
        
        # Create a VideoWriter object
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')  # or use 'XVID'
        out = cv2.VideoWriter(file_path, fourcc, fps, (int(cap.get(3)), int(cap.get(4))))

        # Read frames from the video
        frame_number = 0
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break

            # Write the frame to the output video if it is in the desired time region
            if start_frame <= frame_number <= end_frame:
                out.write(frame)

            frame_number += 1

        # Release the VideoCapture and VideoWriter
        cap.release()
        out.release()
        return
    
    def create_motion(self):
        if self.current_filepath == "":
            return
        
        name, ext = os.path.splitext(self.current_filepath)
        file_path = f"{name}_trim{ext}"
        self.save_video(file_path)
        
        output_dir = name
        os.makedirs(output_dir, exist_ok=True)
        
        pkl_path = output_dir + "/output.pkl"
        
        from wham import WHAM_API
        wham_model = WHAM_API()
        results, tracking_results, slam_results = wham_model(video = file_path, output_dir = output_dir, visualize = True, pkl_path = pkl_path)
        
        self.clear()
        
        save_dir = Path(__file__).resolve().parents[2]  / "data" / "smpl" #DanceTransfer/data/smpl
        filename = os.path.basename(name)
        if not os.path.exists(save_dir):
            os.makedirs(save_dir, exist_ok=True)
        self.fbx_path = str(save_dir) + f"/{filename}.fbx"
        loader.save_smpl_fbx(pkl_path, self.fbx_path)

        self.load_video(output_dir + "/output.mp4")
        
    def apply_motion(self, start_frame):           
        file_path = self.fbx_path
                
        # Check dancers to apply motion
        dancers = self.parent_window.get_dancers()
        for idx, dancer in enumerate(dancers):
            dancer.target.select(False)
            if self.checkbox_applied_dancers[idx]:
                dancer.target.select(True)
                
        self.parent_window.insert_motion(file_path, start_frame)
            
    def draw_time_line(self, draw_list, x,y):
        time_length_scale = self.time_length_scale if self.time_length_scale > 0 else 0.1
        short_line = 10
        long_line = 15
        draw_list.add_line(x, 
                            y + 25, 
                            x + 3000, 
                            y + 25, imgui.get_color_u32_rgba(1,1,1,1), 1)
        for sec in range(0, 300):
            if sec % 5 == 0:
                draw_list.add_text(x+sec/time_length_scale, y, imgui.get_color_u32_rgba(1,1,1,1), "{}".format(sec))
                draw_list.add_line(x + sec/time_length_scale, 
                                y + 25, 
                                x + sec/time_length_scale, 
                                y + short_line, imgui.get_color_u32_rgba(1,1,1,1), 1)
            else :
                draw_list.add_line(x + sec/time_length_scale, 
                                y + 25, 
                                x + sec/time_length_scale, 
                                y + long_line, imgui.get_color_u32_rgba(1,1,1,1), 1)

        
    def on_mouse_release(self, x, y, button, modifier):        
        if self.is_picked(x,y):                
            if self.frame_bar.selected is True:
                self.frame_bar.select(False)
        self.video_sequence.on_mouse_release(x, y, button, modifier)
        return
    
    def on_mouse_press(self, x, y, button, modifier) -> None:
        if self.is_picked(x,y):
            if self.video_sequence.is_picked(x,y):
                self.video_sequence.on_mouse_press(x,y,button,modifier)

        
    def on_mouse_drag(self, x, y, dx, dy):
        if self.frame_bar.is_picked(x,y) or self.frame_bar.selected is True:
            self.control_frame += dx
            self.frame_bar.select(True)
        self.video_sequence.on_mouse_drag(x, y, dx, dy)
        
        return