from render import RenderWindow

if __name__ == '__main__':
    width = 2560
    height = 1440

    # Render window.
    renderer = RenderWindow(width, height, "Render view", resizable = True)   
    renderer.set_location(200, 200)
    renderer.run()



