from sequtus.game import application_core
from sequtus.defaults import menus, battle, sim

def temp_engine():
    e = DefaultCore()
    e.startup()
    e.set_screen('main menu')
    return e

class DefaultCore (application_core.EngineV4):
    def __init__(self):
        super(DefaultCore, self).__init__()
        
        self.load_static_images(
            ["background", "sequtus/defaults/background.png"]
        )
        
        self.screens['main menu'] = menus.DefaultMenu(self, [640, 480])
        self.screens['battle'] = battle.DefaultBattle(self, [640, 480], sim=sim.DefaultSim(
            engine = self, scenario = "sequtus/defaults/scenario.json",
            game_data = "sequtus/defaults/game_data.json"))