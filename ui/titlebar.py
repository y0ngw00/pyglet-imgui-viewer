
import pyglet

import imgui
import imgui.core
from imgui.integrations.pyglet import create_renderer

from enum_list import LayoutMode
from interface import UI
class TitleBar:
    def __init__(self):
        
        self.renderer = UI.window
        self.is_open_file = False
        self.file_ext = ""
        self.file_descriptions = ""
        self.is_capture_screen = False


    def render(self):
        file_ext = ""
        file_descriptions = ""
        if imgui.begin_main_menu_bar():
            if imgui.begin_menu("File"):
                self.render_menu_tab()
                imgui.end_menu()
                
            if imgui.begin_menu("Tool"):
                self.render_tool_tab()
                imgui.end_menu()
                
            if imgui.begin_menu("Layout"):
                self.render_layout_tab()
                imgui.end_menu()
            
            imgui.end_main_menu_bar()


        if self.is_open_file is True:
            self.is_open_file = False
            selected_file = ""
            imgui.open_popup("Open File")

            if imgui.begin_popup_modal("Open File", None, imgui.WINDOW_ALWAYS_AUTO_RESIZE)[0]:
                selected_file = UI.render_open_file_dialog(self.file_descriptions, self.file_ext)

            imgui.end_popup()

            if selected_file:
                print(f"Open File: {selected_file}")
                UI.open_file(selected_file)
                
        return
    
    def render_menu_tab(self):
        imgui.menu_item("(demo menu)", None, False, False)
        if imgui.menu_item("New")[0]:
            UI.new_project()
        
        if imgui.menu_item("Load")[0]:
            UI.load_project()
        
        if imgui.menu_item("Save")[0]:
            UI.save_project()
        
        if imgui.begin_menu("Import"):
        #     pass
            if imgui.menu_item("BVH", None)[0]:
                self.file_descriptions = "BVH Files"
                self.file_ext = "*.bvh"
                self.is_open_file = True

            if imgui.menu_item("GLTF", None)[0]:
                self.file_descriptions = "GLTF Files"
                self.file_ext = ["*.gltf","*.glb"]
                self.is_open_file = True
                
            if imgui.menu_item("FBX", None)[0]:
                self.file_descriptions = "FBX Files"
                self.file_ext = ["*.fbx"]
                self.is_open_file = True

            imgui.end_menu()
        imgui.separator()
        
        if imgui.begin_menu("Options"):
            use_shadow = self.renderer.use_shadow
            _, self.renderer.set_shadow = imgui.checkbox("Use shadow mapping", use_shadow)
            
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
            
    def render_tool_tab(self):
        # Screen Capture
        if self.is_capture_screen is True:
            self.is_capture_screen = False
        if imgui.menu_item("Screen Capture")[0]:
            self.renderer.capture_screen()
            self.is_capture_screen = True
        
        # Record
        record_text = "Record"
        if imgui.menu_item(record_text)[0]:
            self.renderer.start_recording()
            
    def render_layout_tab(self):
        if imgui.begin_menu("Formation View"):
        #     pass
            if imgui.menu_item("Full", None)[0]:
                UI.window.adjust_scene_layout(LayoutMode.FULL)
                UI.adjust_formation_layout(LayoutMode.FULL)

            if imgui.menu_item("1 by 1", None)[0]:
                UI.window.adjust_scene_layout(LayoutMode.HALF)
                UI.adjust_formation_layout(LayoutMode.HALF)
            imgui.end_menu()

