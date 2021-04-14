import pygame
import math,time
from queue import PriorityQueue
from random import randint

WIDTH = 600
win = pygame.display.set_mode((WIDTH, WIDTH))
# square everything for display
pygame.display.set_caption("Dijkstra PATH FINDER")
pygame.init()
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
    def __init__(self, row, col, gap, total_rows):
        self.row = row #numbers
        self.col = col
        self.x = row * gap #position of the spot
        self.y = col * gap
        self.color = WHITE
        self.neighbours = []
        self.gap = gap
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
        pygame.draw.ellipse(win, self.color, (self.x, self.y, self.gap, self.gap))
    
    def drawparent(self,win):
        pygame.draw.ellipse(win, self.color, (self.x, self.y, self.gap, self.gap))

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
 
    def __lt__(self, other):
        return False

def reconstruct_path(came_from, current, draw):
    while current in came_from:
        current = came_from[current]
        current.make_path()
        draw()

def algorithm(draw, grid, start, end):
    pri_queue = PriorityQueue()  # helps us get the min element fscore wise effeciently
    came_from = {}
    
    # total f score = g_score
    f_score = {spot: float("inf") for row in grid for spot in row}
    f_score[start] = 0
    # start is the node which is inserted
    pri_queue.put((f_score[start], start))
    track_set = {start}

    # until all the spots havent been covered
    while not pri_queue.empty():
        for event in pygame.event.get():
            # if the quit cross option is pressed then we quit the pygame
            if event.type == pygame.QUIT:
                pygame.quit()

        # this gets us the node from(fscore,count,node) in the open set we made
        current = pri_queue.get()[1]
        track_set.remove(current)

        # when we have found the end node so now make the path
        if current == end:
            reconstruct_path(came_from, end, draw)
            # recolors the start and node back to original colors instead of purple
            start.make_start()
            end.make_end()
            return True

        for neighbour in current.neighbours:
            temp_f_score = f_score[current] + 1

            # if we found better way to reach the neighbour update the path
            if temp_f_score < f_score[neighbour]:
                came_from[neighbour] = current
                f_score[neighbour] = temp_f_score

                # if this neighbor is not yet checked and added to our sets than add it
                # then we put in the neighbour and consider it too
                if neighbour not in track_set:
                    pri_queue.put((f_score[neighbour],neighbour))
                    track_set.add(neighbour)
                    neighbour.make_open()

        draw()

        # this shows that if the current node that we just considered is not the start node than we make it closed
        if current != start:
            current.make_closed()

    return False


def make_grid(rows, width):
    grid = []
    # 2d list (contains Spots (class))
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
    win.fill(GREY)

    for row in grid:  # traverse through the 2d list grid
        for spot in row:
            if spot.color == PURPLE:
                spot.drawparent(win)        #for path reconstruction rectangle
            else:
                spot.draw(win)      #draws the color of the spot

    draw_grid(win, rows, width)  # drawing the grid lines
    pygame.display.update()

# TRANSLATES THE MOUSE POSITION INTO AN ACTUAL ROW AND COLOUMN CUBE THAT WE CLICKED


def get_clicked_pos(pos, rows, width):
    gap = width // rows  # width = width of the diplay screen
    y, x = pos

    row = y//gap    #row,col of our grid calculated
    col = x//gap

    return row, col

# main function:
# does all of the collision checks,changing the cube colors etc


def main(win, width):
    TOTAL_ROWS = 40
    grid = make_grid(TOTAL_ROWS, width)  # makes the grid 2d array of spots

    start = None    # to make them not local variables
    end = None
    
    run = True
    while run:
        draw(win, grid, TOTAL_ROWS, width)
        for event in pygame.event.get():
            # for whatever event happens in the pygame(click of mouse, end of search etc it loops through them)
            if event.type == pygame.QUIT:
                run = False

            if pygame.mouse.get_pressed()[0]:  # left click of mouse
                pos = pygame.mouse.get_pos()  # this just gets the position of the mouse
                # this gets us our exact cube that was chosen
                row, col = get_clicked_pos(pos, TOTAL_ROWS, width)
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
                row, col = get_clicked_pos(pos, TOTAL_ROWS, width)
                spot = grid[row][col]
                spot.reset()
                if spot == start:
                    start = None
                elif spot == end:
                    end = None

            if event.type == pygame.KEYDOWN:  # did we press a key on the keyboard down or not
                # if the pressed down key is space bar and the we havent already started then start
                if event.key == pygame.K_SPACE and start and end:
                    for row in grid:
                        for spot in row:
                            spot.update_neighbours(grid)

                    # passes the draw function as an atual argument inside the algo function
                    mission =algorithm(lambda: draw(win, grid, TOTAL_ROWS, width),grid, start, end)
                    batado = ''
                    if mission:
                        batado = 'MISSION SUCCESS!'
                    else:
                        batado = 'MISSION FAILURE!'
                    font = pygame.font.Font('freesansbold.ttf', 40)
                    text = font.render(batado,True,BLUE,GREEN)
                    text_rect = text.get_rect()
                    text_rect.center = (width//2,width//2)
                    win.blit(text,text_rect)
                    pygame.display.update()
                    time.sleep(3)

                #maze_generator
                if event.key == pygame.K_m:
                    i=0
                    while i<TOTAL_ROWS*TOTAL_ROWS//7:
                        a = randint(0,TOTAL_ROWS-1)
                        b = randint(0,TOTAL_ROWS-1)
                        spot = grid[a][b]
                        if spot != end and spot != start and not spot.is_barrier():
                            spot.make_barrier()
                            i +=1
                            
                # resets the whole thing
                if event.key == pygame.K_c:
                    start = None
                    end = None
                    grid = make_grid(TOTAL_ROWS, width)

    pygame.quit()


main(win, WIDTH)