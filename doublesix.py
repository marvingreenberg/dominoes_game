import random

class Player:
  def __init__(self, name):
    self.dominoes = []
    self.myname = name

  def assign (self, d):
    self.dominoes = d

  def play(self):
    return self.dominoes.pop()

  def __repr__(self):
    return str(self.myname) + str(self.dominoes)



class Board:
  def __init__(self):
    self.played_dominoes = []

  def available_plays(self):
    #if the list is empty allow any plays
    if self.played_dominoes:
      #if there are played dominoes the available plays are the first value of the first domino or the last value of the last domino
      available = [self.played_dominoes[0][0],self.played_dominoes[-1][-1]]
    else:
      available=[0,1,2,3,4,5,6]
    return available

  def putdown (self, domino):
    '''Put down a domino'''
    domino= list(domino)

    if self.played_dominoes:
      beginning = self.played_dominoes[0][0]
      if beginning in domino:
        if beginning == domino[0]:
          domino.reverse()
        self.played_dominoes.insert(0,domino)
      else:
        end = self.played_dominoes[-1][-1]
        if end in domino:
          if end == domino[1]:
            domino.reverse()
          self.played_dominoes.append(domino)
        else:
          print ("Can't play that dummy",domino)
    else:
      self.played_dominoes.insert(0,domino)

  def __repr__(self):
    return str(self.played_dominoes)




class Game:
  def __init__(self, players):
    self.board = Board()
    #players is a list of 4 player objects
    self.players = players
    assert isinstance(players, list) and len(players) == 4

  def deal(self):
    dominoes=[]
    for i in range (0,7):
      for j in range (i,7):
        dominoes.append( [i,j] )
    random.shuffle(dominoes)
    self.players[0].assign(dominoes[0:7])
    self.players[1].assign(dominoes[7:14])
    self.players[2].assign(dominoes[14:21])
    self.players[3].assign(dominoes[21:28])

  def play_game(self):
    while any( [sp.dominoes for sp in self.players] ):
      for p in self.players:
        d= p.play()
        print (p.myname, "played", d, "has", p.dominoes)
        print ("")
        self.board.putdown(d)