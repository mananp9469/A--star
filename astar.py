import pygame
import math
from queue import PriorityQueue
from random import randint

WIDTH = 600
WIN = pygame.display.set_mode((WIDTH, WIDTH))
# square everything for display
pygame.display.set_caption("A* PATH FINDER")

# colors:
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
PURPLE = (128, 0, 128)
ORANGE = (255, 165, 0)
GREY = (128, 128, 128)
TURQUOISE = (64, 224, 208)

# SPOT CLASS:


class Spot:
    def __init__(self, row, col, width, total_rows):
        self.row = row
        self.col = col
        self.x = row * width
        self.y = col * width
        self.color = WHITE
        self.neighbours = []
        self.width = width
        self.total_rows = total_rows

    def get_pos(self):
        return self.row, self.col

    def is_closed(self):
        return self.color == RED  # already looked at the spot if its red

    def is_open(self):
        return self.color == GREEN  #spot updated neighbour yet to be looked

    def is_barrier(self):  # obstacle/barrier
        return self.color == BLACK

    def is_start(self):
        return self.color == ORANGE  # start spot

    def is_end(self):
        return self.color == TURQUOISE  # end spot

# these are to make the spots change color accordingly
    def reset(self):
        self.color = WHITE

    def make_start(self):
        self.color = ORANGE

    def make_closed(self):
        self.color = RED

    def make_open(self):
        self.color = GREEN

    def make_barrier(self):
        self.color = BLACK

    def make_end(self):
        self.color = TURQUOISE

    def make_path(self):
        self.color = PURPLE

    def draw(self, win):
        pygame.draw.ellipse(win, self.color, (self.x, self.y, self.width, self.width))
    
    def drawparent(self,win):
        pygame.draw.rect(win, self.color, (self.x, self.y, self.width, self.width))

    def update_neighbours(self, grid):
        self.neighbours = []

        # down
        if self.row < self.total_rows - 1 and not grid[self.row+1][self.col].is_barrier():
          self.neighbours.append(grid[self.row + 1][self.col])
        
        # up
        if self.row > 0 and not grid[self.row-1][self.col].is_barrier():  
          self.neighbours.append(grid[self.row - 1][self.col])

        # right
        if self.col < self.total_rows - 1 and not grid[self.row][self.col+1].is_barrier():
          self.neighbours.append(grid[self.row][self.col+1])

        # left
        if self.col > 0 and not grid[self.row][self.col-1].is_barrier():  
          self.neighbours.append(grid[self.row][self.col-1])

        # diagnol right down
        if self.row < self.total_rows - 1 and self.col < self.total_rows - 1 and not grid[self.row + 1][self.col + 1].is_barrier():
          self.neighbours.append(grid[self.row + 1][self.col + 1])

        # diagnol left down
        if self.row < self.total_rows - 1 and self.col > 0 and not grid[self.row + 1][self.col - 1].is_barrier():
          self.neighbours.append(grid[self.row + 1][self.col - 1])

        # diagnol right up
        if self.row > 0 and self.col < self.total_rows - 1 and not grid[self.row - 1][self.col + 1].is_barrier():
          self.neighbours.append(grid[self.row - 1][self.col + 1])

        # diagnol left up
        if self.row > 0 and self.col > 0 and not grid[self.row - 1][self.col - 1].is_barrier():
          self.neighbours.append(grid[self.row - 1][self.col - 1])
 
    def __lt__(self, other):  # stands for less than
        # when we need to compare two spots together
        return False

# END OF CLASS__________________________________________________________________________________
# heuristics function


def h(p1, p2):
    x1, y1 = p1
    x2, y2 = p2
    return ((x1-x2)**2 + (y1-y2)**2)**0.5        

def reconstruct_path(came_from, current, draw):
    while current in came_from:
        current = came_from[current]
        current.make_path()
        draw()

def algorithm(draw, grid, start, end):
    count = 0
    open_set = PriorityQueue()  # helps us get the min element fscore wise effeciently
    # adding the start node into the priorty queue
    # 0 represents the 'fscore for start value which is obviously 0
    # count is basically a tie breaker for when updating neighbors with same score then the first one inserted wins
    # start is the node which is inserted
    open_set.put((0, count, start))
    # parent nodes
    came_from = {}
    # list comprehension
    # every spot gets key value as infinity
    g_score = {spot: float("inf") for row in grid for spot in row}
    g_score[start] = 0
    # total f score = g_score + heuristics
    f_score = {spot: float("inf") for row in grid for spot in row}
    f_score[start] = h(start.get_pos(), end.get_pos())

    # this is a set
    # keeps track of items in the p.queue and which are not
    # so this set stores all the items as p.queue
    open_set_hash = {start}

    # until all the spots havent been covered
    while not open_set.empty():
        for event in pygame.event.get():
            # if the quit cross option is pressed then we quit the pygame
            if event.type == pygame.QUIT:
                pygame.quit()

        # this gets us the node from(fscore,count,node) in the open set we made
        current = open_set.get()[2]
        # this also removes the current node that we just popped out of the p.queue and removes the same from its set
        # to be sure that we are in sync with p.queue and set
        open_set_hash.remove(current)

        # when we have found the end node so now make the path
        if current == end:
            reconstruct_path(came_from, end, draw)
            # recolors the start and node back to original colors instead of purple
            start.make_start()
            end.make_end()
            return True

        for neighbour in current.neighbours:
            temp_g_score = g_score[current] + 1

            # if we found better way to reach the neighbour update the path
            if temp_g_score < g_score[neighbour]:
                came_from[neighbour] = current
                g_score[neighbour] = temp_g_score
                f_score[neighbour] = temp_g_score + h(neighbour.get_pos(), end.get_pos())

                # if this neighbor is not yet checked and added to our sets than add it
                # then we put in the neighbour and consider it too
                if neighbour not in open_set_hash:
                    count += 1
                    open_set.put((f_score[neighbour], count, neighbour))
                    open_set_hash.add(neighbour)
                    neighbour.make_open()

        draw()

        # this shows that if the current node that we just considered is not the start node than we make it closed
        #
        if current != start:
            current.make_closed()

    return False


def make_grid(rows, width):
    grid = []
    # 2d list (bunch of lists inside of lists)
    gap = width // rows  # that is the width of each cube in the grid
    for i in range(rows):
        grid.append([])
        for j in range(rows):
            spot = Spot(i, j, gap, rows)
            grid[i].append(spot)  # NOT Spot

    return grid

# drawing grid lines:
def draw_grid(win, rows, width):
    gap = width // rows
    for i in range(rows):
        pygame.draw.line(win, GREY, (0, i*gap), (width, i * gap))
        for j in range(rows):
            pygame.draw.line(win, GREY, (j*gap, 0), (j*gap, width))


def draw(win, grid, rows, width):
    # fills the entire screen with one color
    win.fill(WHITE)

    for row in grid:  # traverse through the 2d list grid
        for spot in row:
            if spot.color ==PURPLE:
                spot.drawparent(win)        #for path reconstruction rectangle
            else:
                spot.draw(win)      #draws the color of the spot

    draw_grid(win, rows, width)  # drawing the grid lines
    pygame.display.update()

# TRANSLATES THE MOUSE POSITION INTO AN ACTUAL ROW AND COLOUMN CUBE THAT WE CLICKED


def get_clicked_pos(pos, rows, width):
    gap = width // rows  # width of one cube
    y, x = pos

    row = y//gap
    col = x//gap

    return row, col

# main function:
# does all of the collision checks,changing the cube colors etc


def main(win, width):
    ROWS = 50
    grid = make_grid(ROWS, width)  # makes the grid 2d array of spots

    start = None
    end = None

    started = False
    # variables to keep track if we started or not and the start end positions
    run = True
    while run:
        draw(win, grid, ROWS, width)
        for event in pygame.event.get():
            # for whatever event happens in the pygame(click of mouse, end of search etc it loops through them)
            if event.type == pygame.QUIT:
                run = False

            if pygame.mouse.get_pressed()[0]:  # left click of mouse
                pos = pygame.mouse.get_pos()  # this just gets the position of the mouse
                # this gets us our exact cube that was chosen
                row, col = get_clicked_pos(pos, ROWS, width)
                spot = grid[row][col]  # indexed it in the grid
                if not start and spot != end:
                    start = spot
                    start.make_start()

                elif not end and spot != start:
                    end = spot
                    end.make_end()

                elif spot != end and spot != start:
                    spot.make_barrier()

            elif pygame.mouse.get_pressed()[2]:  # right click of mouse
                pos = pygame.mouse.get_pos()
                row, col = get_clicked_pos(pos, ROWS, width)
                spot = grid[row][col]
                spot.reset()
                if spot == start:
                    start = None
                elif spot == end:
                    end = None

            if event.type == pygame.KEYDOWN:  # did we press a key on the keyboard down or not
                # if the pressed dpwn key is space bar and the we havent already started then start
                if event.key == pygame.K_SPACE and start and end:
                    for row in grid:
                        for spot in row:
                            spot.update_neighbours(grid)

                    # passes the draw function as an atual argument inside the algo function
                    algorithm(lambda: draw(win, grid, ROWS, width),grid, start, end)

                #maze_generator
                if event.key == pygame.K_m:
                    i=0
                    while i<400:
                        a = randint(0,ROWS-1)
                        b = randint(0,ROWS-1)
                        spot = grid[a][b]
                        if spot != end and spot != start:
                            spot.make_barrier()
                            i +=1
                            
                # resets the whole thing
                if event.key == pygame.K_c:
                    start = None
                    end = None
                    grid = make_grid(ROWS, width)

    pygame.quit()


main(WIN, WIDTH)
