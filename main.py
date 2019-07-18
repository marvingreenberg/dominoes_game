import random
from doublesix import Player, Board, Game


p1 = Player('Lucio')
p2 = Player('Cupcake')
p3 = Player('Gustav')
p4 = Player('Harrison')

g = Game([p1, p2, p3, p4])
print (g.board)
print (g.players)
g.deal()
g.play_game()
print (g.board)