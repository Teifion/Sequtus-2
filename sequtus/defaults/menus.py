from sequtus.render import screen

class DefaultMenu (screen.Screen):
    def __init__(self, *args, **kwargs):
        super(DefaultMenu, self).__init__(*args, **kwargs)
        self.background_image = self.engine.images["background"]
    
    def update(self):
        pass




