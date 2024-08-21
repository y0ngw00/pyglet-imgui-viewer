import pyglet

import imgui
import imgui.core

import numpy as np
from imgui_color import COLORS
class GroupingStatus:
    def __init__(self, parent_window):
        self.parent_window = parent_window
        self.sequencer = parent_window.Sequencer
        self.formation = parent_window.DancerFormation
        
        self.new_pair_input = dict({"dancer1": "", "dancer2": "", "start": "", "last": ""})
        self.pairs = np.zeros([0,4], dtype = np.int32)       
        
    def render(self):
        if imgui.begin_table("Dancer pairing", 2):  
            imgui.table_next_row()
            imgui.table_next_column()
            imgui.push_item_width(200)
            imgui.text("Dancer Name")
            imgui.table_next_column()
            imgui.push_item_width(200)
            imgui.text("Group")
            
            dancers = self.parent_window.get_dancers()
            
            for idx, dancer in enumerate(dancers):
                imgui.table_next_row()
                imgui.table_set_column_index(0)
                imgui.push_item_width(200) 
                changed, dancer.set_name = imgui.input_text("##{}".format(idx), dancer.get_name, buffer_length = 200)
                imgui.table_next_column()
                group_idx = dancer.get_group_index
                with imgui.begin_combo("##Dancer {}'s group".format(idx), f'{group_idx} ({COLORS[group_idx]})', flags = imgui.COMBO_HEIGHT_REGULAR) as combo:
                    if combo.opened:
                        for i, item in enumerate(COLORS):
                            if imgui.selectable(f'{i} ({item})')[0]:
                                dancer.set_group_index = i
                               
                # imgui.table_next_column()
                # imgui.text(str(pair_info[3]))
            
            # imgui.table_next_row()
            # imgui.table_set_column_index(0)
            # _, self.new_pair_input["dancer1"] = imgui.input_text("##dancer1", self.new_pair_input["dancer1"])
            # imgui.table_next_column()
            # _, self.new_pair_input["dancer2"]= imgui.input_text("##dancer2", self.new_pair_input["dancer2"])
            # imgui.table_next_column()
            # _, self.new_pair_input["start"]= imgui.input_text("##first", self.new_pair_input["start"])
            # imgui.table_next_column()
            # _, self.new_pair_input["last"]= imgui.input_text("##last", self.new_pair_input["last"])
            # imgui.table_next_column()

            imgui.end_table()
            
        
 
        #     if self.new_pair_input["dancer1"]!="" and self.new_pair_input["dancer2"]!="" and self.new_pair_input["start"]!="" and self.new_pair_input["last"]!="":
        #         print("Add pair")
        #         print(self.new_pair_input)
        #         self.pairs = np.vstack([self.pairs, [int(self.new_pair_input["dancer1"]), int(self.new_pair_input["dancer2"]), int(self.new_pair_input["start"]), int(self.new_pair_input["last"]) ]])
        #         self.new_pair_input = dict({"dancer1": "", "dancer2": "", "start": "", "last": ""})
                
        # imgui.same_line()
        # if imgui.button("Clear"):
        #     self.pairs = np.zeros([0,4], dtype = np.int32)
        #     self.new_pair_input = dict({"dancer1": "", "dancer2": "", "start": "", "last": ""})
            

            
        # if imgui.button("Add Main dancer"):
            
        #     if self.new_main_input["dancer_index"]!="" and self.new_main_input["start"]!="" and self.new_main_input["last"]!="":
        #         print("Add Main dancer part")
        #         print(self.new_main_input)
        #         self.mains = np.vstack([self.mains, [int(self.new_main_input["dancer_index"]), int(self.new_main_input["start"]), int(self.new_main_input["last"]) ]])
        #         self.new_main_input = dict({"dancer_index": "", "start": "", "last": ""})
                
        # imgui.same_line()
        # if imgui.button("Clear all parts"):
        #     self.mains = np.zeros([0,3], dtype = np.int32)
        #     self.new_main_input = dict({"dancer_index": "", "start": "", "last": ""})
