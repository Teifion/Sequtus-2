from sequtus.defaults import sim
from sequtus.render import battle_screen

class DefaultBattle (battle_screen.BattleScreen):
    def __init__(self, engine, *args, **kwargs):
        super(DefaultBattle, self).__init__(engine, *args, **kwargs)
        self.background_image = self.engine.images["background"]
    
    def update(self):
        pass




