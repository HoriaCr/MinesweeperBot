from selenium.webdriver.common.action_chains import ActionChains
from selenium import webdriver
from selenium.webdriver.common.keys import Keys

class MinesweeperSolver(object):

  def __init__(self, h, w, m, driver):
    self.driver = driver
    self.dx = [1, 1, 1, -1, -1, -1, 0, 0]
    self.dy = [-1, 1, 0, -1, 1, 0, -1, 1]
    self.height = h
    self.width = w
    self.mines = m
    self.state = [[-2 for i in range(w + 1)] for j in range(h + 1)]
    self.safeQ = set()
    self.safeB = set()
    self.revealed = set()
    self.unknowns = set()
    self.bombs = set()
    
    for i in range(1, h + 1):
      for j in range(1, w + 1):
        self.unknowns.add((i, j))      

  def getId(self, cell):
      return str(cell[0]) + '_' + str(cell[1])    
  
  def isInside(self, cell):
    return 1 <= cell[0] <= self.height and 1 <= cell[1] <= self.width

  def getMore(self):
    ret = 0
    out = set()
    if True:
      for cell in self.revealed:
        num = [0, 0, 0]
        maybe = []
        for k in range(8):
          x, y = cell[0] + self.dx[k], cell[1] + self.dy[k]
          if self.isInside((x, y)):
            num[2] += 1 # total neighbours for this cell
            if self.state[x][y] == -1:
              num[1] += 1 # this is a bomb
            elif self.state[x][y] != -2:
              num[0] += 1 # it's known and not a bomb
            elif self.state[x][y] == -2:
              maybe.append((x, y))

        if num[1] == self.state[cell[0]][cell[1]]:
          for xcell in maybe:
            self.safeQ.add(xcell)
            ret += 1
        elif len(maybe) > 0 and self.state[cell[0]][cell[1]] - num[1] == len(maybe):
           for xcell in maybe:
             self.safeB.add(xcell)
             #self.unknowns.remove(xcell)
             #out.add(xcell)
             self.state[xcell[0]][xcell[1]] = -1
             ret += 1
    if ret == 0:
      self.safeQ.add(self.unknowns.pop())
  
  def nextSafe(self):
    return self.safeQ.pop()
  
  def nextBomb(self):
    return self.safeB.pop()
  
  def parseCellState(self, cell, cellState):
    if 'bombflagged' in cellState:
      return -1
    if 'blank' in cellState:
      return -2
    return int(cellState[-1])

  def printState(self):
    for i in range(1, self.height + 1):
      print self.state[i]
  
  def updateState(self):
     out = set()
     for cell in self.unknowns:
        pcell = self.driver.find_element_by_id(self.getId(cell))
        cellClass = pcell.get_attribute('class')
        self.state[cell[0]][cell[1]] = self.parseCellState(cell, cellClass)
        if self.state[cell[0]][cell[1]] != -2:
          out.add(cell)
     self.unknowns -= out
     self.revealed |= out
     #print self.printState()

  def clickCell(self, cell, leftClick=True):
    pcell = self.driver.find_element_by_id(self.getId(cell)) 
    if leftClick:
      pcell.click()
    else:
      self.bombs.add(cell)
      ActionChains(self.driver).move_to_element(pcell).context_click(pcell).perform()

  def feedTheMouse(self, cycle):
    print ("At cycle #", cycle)
    if len(self.revealed) == self.height * self.width:
      return
    self.getMore()
    while len(self.safeQ):
      cell = self.nextSafe()
      self.clickCell(cell)
    while len(self.safeB):
      cell = self.nextBomb()
      self.clickCell(cell, False)
    self.updateState()
    self.feedTheMouse(cycle + 1)

  def startPlaying(self):
    self.driver.get("http://www.minesweeperonline.com") # website link  
    self.driver.implicitly_wait(5) # seconds
    self.feedTheMouse(0)    
    #self.driver.close()
  
solver = MinesweeperSolver(16, 30, 99, webdriver.Firefox())
solver.startPlaying()
