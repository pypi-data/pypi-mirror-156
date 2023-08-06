"""This main module will run the game.

Type python -m thehouse and the game will run.
"""

from thehouse.characters import Player
from thehouse.thehouse import TheHouse

player = Player()
game = TheHouse(player)

game.play()
