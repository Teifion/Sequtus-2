from sequtus.game import battle_sim

# Currently doesn't actually do anything differently
class DefaultSim (battle_sim.BattleSim):
    pass

# Always kills AI threads after loading
class TestSim (DefaultSim):
    def load_all(self, *args, **kwargs):
        super(DefaultSim, self).load_all(*args, **kwargs)
        
        for k, q in self.out_queues.items():
            q.put({"cmd":"quit"})
