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

from fonts import Fonts
from frame_bar import FrameBar
from box_item import BoxItem
from sequencer import Sequencer
from sequence import Sequence

class MotionCreator(BoxItem):
    def __init__(self, parent_window):
        super().__init__()
        self.parent_window = parent_window        
        # self.update = False
        self.is_show = False
        
        self.video_timestep = 0.5
        
        self.player = pyglet.media.Player()
        self.video_length = 0
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
            
    def render(self):
        # if self.update:
        #     imgui.core.set_next_window_position(*imgui.get_mouse_pos())
        #     self.update = False
            
        if self.is_show is True:
            expanded, self.is_show = imgui.begin("Motion Creator", True)
            
            canvas_pos = imgui.get_window_position()
            self.update_position(x = canvas_pos.x, 
                                    y = canvas_pos.y,
                                    xsize_box = imgui.get_window_width()-40, 
                                    ysize_box = imgui.get_window_height()-40)
            
            self.sequence_width = self.xsize_box

            if self.is_show:
                if imgui.button("Upload video"):
                    file_path = self.parent_window.render_file_dialog("Video Files", ["*.mp4", "*.avi", "*.wav"])
                    if file_path:
                        self.load_video(file_path)
                imgui.same_line()
                if imgui.button("Clear"):
                    self.clear()
                
                if self.player.get_texture() is not None:
                    texture = self.player.get_texture()
                    aspect_ratio = texture.height /texture.width 
                    video_viewer_width = imgui.get_window_size()[0] - 30
                    video_viewer_height = video_viewer_width * aspect_ratio
                    imgui.begin_child("Video Window", video_viewer_width, video_viewer_height, border=True)   
                    imgui.image(texture.id, video_viewer_width, video_viewer_height)
                    imgui.end_child()
                else:
                    video_viewer_width,video_viewer_height = imgui.get_window_size()
                    imgui.begin_child("Video Window", self.sequence_width, video_viewer_height-500, border=True)   
                    imgui.end_child()
        
                # imgui.image(self.texture.id, 300, 300)
                # if self.player.source and self.player.source.video_format:
                    # self.player.get_texture().blit(0,0)
                    
                imgui.begin_child("Video Sequencer", self.sequence_width, 300, border=True)   
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
                            self.player.play()
                    imgui.same_line()      
                    if imgui.button("Next"):
                        self.next()
                        self.player.pause()
                    imgui.same_line() 
                    if imgui.button(">|"):
                        self.goto_end()
                        self.player.pause()
                        
                self.video_sequence.render(0, 0)
                
                draw_list = imgui.get_window_draw_list()
                bar_pos = (self.player.time/ (self.video_length+1e-6))* self.sequence_width
                x, y = imgui.get_cursor_screen_pos()
                self.frame_bar.update_position(x, y)
                self.frame_bar.render(draw_list, bar_pos)
                imgui.end_child()


            imgui.end()
                        
        # if self.parent_window.is_playing() is True:
        #     self.player.seek_next_frame()
            
    def show(self, is_show):
        self.is_show = is_show
        
    def prev(self):
        curr_time = self.player.time
        self.player.seek(curr_time - self.video_timestep)
        
    def next(self):
        if self.player.time < self.player.source.duration:
            curr_time = self.player.time
            self.player.seek(curr_time + self.video_timestep)
        return
        
    def goto_first(self):
        self.player.seek(0)
        
    def goto_end(self):
        time = self.player.source.duration - 0.1
        self.player.seek(time)
        
    def on_eos(self):
        print("The player has finished playing its current source.")
            
    def load_video(self, file_path):
        video = pyglet.media.load(file_path)
        self.player.queue(video)
        self.player.seek(0)
        self.player.on_eos = self.on_eos
        
        self.video_length = video.duration
        self.video_sequence.fill_sequence(0,  imgui.get_window_size()[0] - self.padding_x-10)

    def clear(self):
        self.player.delete()
        
    def on_mouse_release(self, x, y, button, modifier):
        pass
        # if self.is_picked(x,y):                
        #     if self.frame_bar.selected is True:
        #         self.frame_bar.select(False)

        
    def on_mouse_drag(self, x, y, dx, dy):
        pass
        # if self.frame_bar.is_picked(x,y) or self.frame_bar.selected is True:
        #     dt = dx * (self.video_length+1e-6) / self.sequence_width
        #     self.player.seek(self.player.time + dt)
        #     self.frame_bar.select(True)