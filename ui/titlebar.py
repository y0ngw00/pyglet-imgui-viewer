
import pyglet

import imgui
import imgui.core
from imgui.integrations.pyglet import create_renderer


class TitleBar:
    def __init__(self, parent_window):
        
        self.parent_window = parent_window
        self.is_open_file = False
        self.is_record = False


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
            
            imgui.end_main_menu_bar()


        if self.is_open_file is True:
            self.is_open_file = False
            selected_file = ""
            imgui.open_popup("Open File")

            if imgui.begin_popup_modal("Open File", None, imgui.WINDOW_ALWAYS_AUTO_RESIZE)[0]:
                selected_file = self.parent_window.render_file_dialog(file_descriptions, file_ext)

            imgui.end_popup()

            if selected_file:
                print(f"Open File: {selected_file}")
                self.parent_window.open_file(selected_file)
                
        return
    
    def render_menu_tab(self):
        imgui.menu_item("(demo menu)", None, False, False)
        if imgui.menu_item("New")[0]:
            pass
        
        if imgui.begin_menu("Open"):
        #     pass
            if imgui.menu_item("BVH", None)[0]:
                file_descriptions = "BVH Files"
                file_ext = "*.bvh"
                self.is_open_file = True

            if imgui.menu_item("GLTF", None)[0]:
                file_descriptions = "GLTF Files"
                file_ext = ["*.gltf","*.glb"]
                self.is_open_file = True
                
            if imgui.menu_item("FBX", None)[0]:
                file_descriptions = "FBX Files"
                file_ext = ["*.fbx"]
                self.is_open_file = True

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
            
    def render_tool_tab(self):
        record_text = "Record" if not self.is_record else "Stop"
        if imgui.menu_item(record_text)[0]:
            self.is_record = not self.is_record
            if self.is_record is True:
                print("Start recording")
                self.parent_window.start_recording()
            else:
                print("Finish recording")
                self.parent_window.stop_recording()