import pyglet

import imgui
import imgui.core

import numpy as np
from imgui_color import COLORS

from interface import UI
class GroupingStatus:
    def __init__(self):
        self.sequencer = UI.Sequencer
        self.formation = UI.DancerFormation
        
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
            
            dancers = UI.get_dancers()
            
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
                               
            imgui.end_table()
            
        
 