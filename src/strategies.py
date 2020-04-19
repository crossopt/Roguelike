import src.fighter
import src.model

def sing(x):
    if x > 0:
        return 1
    elif x < 0:
        return -1
    else:
        return 0

class FightingStrategy:

    def choose_move(current_model: 'src.model.Model', mob: 'src.fighter.Mob'):
        raise NotImplementedError()

class AggressiveStrategy(FightingStrategy):

    def choose_move(current_model: 'src.model.Model', mob: 'src.fighter.Mob'):
        player = current_model.player
        dx = -player.position.x + mob.position.x
        dy = -player.position.y + mob.position.y
        dx = sign(-dx)
        dy = sign(-dy)
        return (dx, dy)

class CowardlyStrategy(FightingStrategy):

    def choose_move(current_model: 'src.model.Model', mob: 'src.fighter.Mob'):
        player = current_model.player
        dx = -player.position.x + mob.position.x
        dy = -player.position.y + mob.position.y
        dx = (dx > 0) * 2 - 1
        dy = (dy > 0) * 2 - 1
        return (dx, dy)

class PassiveStrategy(FightingStrategy):

    def choose_move(current_model: 'src.model.Model', mob: 'src.fighter.Mob'):
        return (0, 0)