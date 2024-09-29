import imgui
import math


def draw_arrow(draw_list, p1, p2, color):
    '''
    Draw an arrow
    '''
    arrow_head_size = 10.0
    arrow_body_thickness = 2.0

    draw_list.add_line(p1[0], p1[1], p2[0], p2[1], color, arrow_body_thickness)

    draw_list.add_triangle_filled(
        p2[0], p2[1],
        p2[0] - arrow_head_size, p2[1] - arrow_head_size,
        p2[0] + arrow_head_size, p2[1] - arrow_head_size,
        color
    )

def draw_curved_arrow(draw_list, p1, cp1, cp2, p2, color):
    '''
    Draw a curved arrow
    '''
    arrow_head_size = 10.0
    arrow_body_thickness = 2.0

    draw_list.add_bezier_cubic(
        p1[0], p1[1], cp1[0], cp1[1], cp2[0], cp2[1], p2[0], p2[1], 
        color, arrow_body_thickness
    )

    draw_list.add_triangle_filled(
        p2[0], p2[1],
        p2[0] - arrow_head_size, p2[1] - arrow_head_size,
        p2[0] + arrow_head_size, p2[1] - arrow_head_size,
        color
    )
    
def draw_arc_arrow(draw_list, center, radius, start_angle, end_angle, color):
    arrow_head_size = 100.0
    arc_thickness = 5.0
    
    dtheta = arrow_head_size / (2 * math.pi * radius)

    arrow_theta = end_angle
    # Draw the arc part of the arrow
    if start_angle > end_angle:
        start_angle, end_angle = end_angle, start_angle
        arrow_theta = start_angle
        dtheta = -dtheta
    draw_list.path_arc_to(center[0], center[1], radius, start_angle, end_angle, 12)
    draw_list.path_stroke(color, False, arc_thickness)

    # Calculate the end point of the arrow
    p2 = (
        center[0] + (radius-arc_thickness/2) * math.cos(arrow_theta),
        center[1] + (radius-arc_thickness/2) * math.sin(arrow_theta)
    )
    arrow_direction = math.atan2(center[1] - p2[1], center[0] - p2[0])
    # Calculate the points of the arrowhead
    p3 = (
        center[0] + (radius-arc_thickness/2) * math.cos(arrow_theta+dtheta),
        center[1] + (radius-arc_thickness/2) * math.sin(arrow_theta+dtheta)
    )
    p4 = (
        center[0] + (radius+arc_thickness *2) * math.cos(arrow_theta),
        center[1] + (radius+arc_thickness *2) * math.sin(arrow_theta)
    )


    # Draw the arrowhead
    draw_list.add_triangle_filled(p2[0], p2[1], p3[0], p3[1], p4[0], p4[1], color)
