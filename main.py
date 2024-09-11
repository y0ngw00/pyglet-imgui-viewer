from render import RenderWindow
from interface import UI

if __name__ == '__main__':
    width = 1440
    height = 900

    # Render window.
    renderer = RenderWindow(width, height, "Render view", resizable = True)
    renderer.set_location(200, 200)
    UI.connect_renderer(renderer)
    renderer.run()



