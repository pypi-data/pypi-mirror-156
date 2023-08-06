import sys
from getkey import getkey, keys
import cursor

def clear():
  print("\033c", end = "")

black = '\033[30m'
red = '\033[31m'
green = '\033[32m'
yellow = '\033[33m'
blue = '\033[34m'
purple = '\033[35m'
cyan = '\033[36m'
reset = '\033[37m'

map = []

cursor.hide()

class set: 
  def mapsize(size): #hmmm collumns...
    map.append(['b', 'b', 'b', 'b', 'b', 'b', 'b', 'b', 'b', 'b', 'b', 'b', 'b', 'b', 'b', 'b', 'b', 'b', 'b', 'b', 'b', 'b', 'b', 'b', 'b', 'b', 'b', 'b'])
    for x in range(size-2):
      map.append(['b', 'p', 'p', 'p', 'p', 'p', 'p', 'p', 'p', 'p', 'p', 'p', 'p', 'p', 'p', 'p', 'p', 'p', 'p', 'p', 'p', 'p', 'p', 'p', 'p','p', 'p', 'b'])
    map.append(['b', 'b', 'b', 'b', 'b', 'b', 'b', 'b', 'b', 'b', 'b', 'b', 'b', 'b', 'b', 'b', 'b', 'b', 'b', 'b', 'b', 'b', 'b', 'b', 'b', 'b', 'b', 'b'])

  def playerstartpos(xpos, ypos):
    global x, y
    if xpos == 0 and ypos == 0:
      print("You can't start at 0, 0")
      sys.exit()
    x = xpos
    y = ypos
  
  def playercolor(color):
    global pcolor
    pcolor = color

  def bordercolor(bcolor):
    global bdcolor
    bdcolor = bcolor

set.mapsize(10)
set.bordercolor(blue)
set.playercolor(red)
set.playerstartpos(1,1)

def print_map():
  for x in map:
    out = ''
    for i in x:
      if i == 'p':
        out += ' '
      elif i == 'b':
        out += f'{bdcolor}░{reset}'
      elif i == 'u':
        out += f'{pcolor}█{reset}'
      elif i == 'd':
          out += 'o'
      elif i == 'e':
        out +='■'
    print(out)

while True:
  clear()
  map[y][x] = 'u'
  print_map()
  try:
    map[y][x] = 'p'
    keyPressed = getkey()

    if keyPressed == 's' and map[y+1][x] != 'b' or keyPressed == keys.DOWN and map[y+1][x] != 'b':
      y += 1

    elif keyPressed == 'w' and map[y-1][x] != 'b' or keyPressed == keys.UP and map[y-1][x] != 'b':
      y -= 1

    elif keyPressed == 'd' and map[y][x+1] != 'b' or keyPressed == keys.RIGHT and map[y][x+1] != 'b':
      x += 1

    elif keyPressed == 'a' and map[y][x-1] != 'b' or keyPressed == keys.LEFT and map[y][x-1] != 'b':
      x -= 1

  except:
    pass 