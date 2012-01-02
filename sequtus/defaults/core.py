from sequtus.game import application_core
from sequtus.defaults import menus, battle, sim

def temp_engine():
    e = DefaultCore()
    e.startup()
    e.set_screen('main menu')
    return e

class DefaultCore (application_core.EngineV4):
    def __init__(self, address=None, port=None, test_sim=True, player_team=1):
        super(DefaultCore, self).__init__()
        
        self.load_static_images(
            ["background", "sequtus/defaults/background.png"],
            ["background", "sequtus/defaults/background_grid.png"],
            ["red_cruiser", "sequtus/defaults/red_cruiser.png"],
            ["red_factory", "sequtus/defaults/red_factory.png"],
        )
        
        self.screens['main menu'] = menus.DefaultMenu(self, [640, 480])
        
        if test_sim:
            s = sim.TestSim(
                player_team = player_team,
                engine = self,
                scenario = "sequtus/defaults/scenario.json",
                game_data = "sequtus/defaults/game_data.json",
                address = address,
                port = port,
            )
        else:
            s = sim.DefaultSim(
                player_team = player_team,
                engine = self,
                scenario = "sequtus/defaults/scenario.json",
                game_data = "sequtus/defaults/game_data.json",
                address = address,
                port = port,
            )
        
        self.screens['battle'] = battle.DefaultBattle(self, [640, 480], sim=s)
