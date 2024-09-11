from render import RenderWindow
from interface import UI
from control import CONTROLLER

if __name__ == '__main__':
    width = 1440
    height = 900

    # Render window.
    renderer = RenderWindow(width, height, "Render view", resizable = True)
    renderer.set_location(200, 200)
    
    CONTROLLER.connect_renderer(renderer)
    UI.connect_renderer(renderer)
    renderer.run()



