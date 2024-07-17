import imgui
import imgui.core

class SequencerMenu:
    def __init__(self, parent_window):
        self.parent_window = parent_window
        
        
        self.x_origin = 0
        self.y_origin = 0
        
        self.update = False
        self.selected = False

    
    def render(self,x,y):
        if self.update:
            imgui.core.set_next_window_position(*imgui.get_mouse_pos())
            self.update = False

        
        imgui.open_popup("my_popup")
        if imgui.begin_popup_context_window("my_popup"):
            if imgui.menu_item("Load Motion")[0]:
                print("Option 1 selected")

            if imgui.menu_item("Option 2")[0]:
                print("Option 2 selected")
            if imgui.menu_item("BVH", None)[0]:
                file_descriptions = "BVH Files"
                file_ext = "*.bvh"
                is_open_file = True

            imgui.end_popup()
        # if imgui.begin_menu("Open"):
        #     #     pass
        #     if imgui.menu_item("BVH", None)[0]:
        #         file_descriptions = "BVH Files"
        #         file_ext = "*.bvh"
        #         is_open_file = True

        #     if imgui.menu_item("GLTF", None)[0]:
        #         file_descriptions = "GLTF Files"
        #         file_ext = ["*.gltf","*.glb"]
        #         is_open_file = True
                
        #     if imgui.menu_item("FBX", None)[0]:
        #         file_descriptions = "FBX Files"
        #         file_ext = ["*.fbx"]
        #         is_open_file = True

            # imgui.end_menu()
            
    def update_position(self):
        self.update = True
        
        return
        