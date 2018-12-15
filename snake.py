import time
import random
import curses

from copy import deepcopy
from pyfiglet import figlet_format

UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)

INIT = "init"
RUNNING = "running"
GAMEOVER = "gameover"
PAUSED = "paused"
EXIT = "exit"

mapping = {
    "w": UP,
    "a": LEFT,
    "s": DOWN,
    "d": RIGHT
}


class Apple(object):
    def __init__(self, width, height, forbidden):
        self.coordinates = (0, 0)
        self.width = width
        self.height = height
        self.respawn(forbidden)

    def respawn(self, forbidden):
        x, y = 0, 0
        while (x, y) in forbidden or x == 0 or y == 0 or x == self.width + 1 or y == self.height + 1:
            x, y = random.randint(1, self.width), random.randint(1, self.height)
            self.coordinates = (x, y)


class Snake(object):
    def __init__(self, body, direction):
        # body is a list of tuples
        # first in the list is the head
        self.body = body
        self.direction = direction

    # add position to front of snake body and pop off the back
    def take_step(self, apple):

        new_position = (self.body[-1][0] + self.direction[0],
                        self.body[-1][1] + self.direction[1])
        if new_position == apple:
            self.body.append(new_position)
        else:
            self.body = self.body[1:] + [new_position]
        return new_position

    def set_direction(self, direction):
        self.direction = direction

    def valid_direction(self, direction):
        return not (set([self.direction, direction]) == set([UP, DOWN]) or set([self.direction, direction]) == set([LEFT, RIGHT]))

    def move(self, apple, direction=None):
        if direction and self.valid_direction(direction):
            self.set_direction(direction)
        return self.take_step(apple)

    def head(self):
        return self.body[-1]


class Game(object):

    def __init__(self, height, width, delay=0.5):
        self.height = height
        self.width = width
        self.delay = delay
        self.state = INIT

        midpoint = (int(width/2), int(height/2))
        self.apple = Apple(width, height, [midpoint])
        self.snake = Snake([midpoint], None)

    def render(self, stdscr):
        k = 0

        # Clear and refresh the screen for a blank canvas
        stdscr.clear()
        stdscr.refresh()

        # Start colors in curses
        curses.start_color()
        curses.init_pair(1, curses.COLOR_CYAN, curses.COLOR_BLACK)
        curses.init_pair(2, curses.COLOR_RED, curses.COLOR_BLACK)
        curses.init_pair(3, curses.COLOR_BLACK, curses.COLOR_WHITE)

        stdscr.addstr(figlet_format('READY PLAYER ONE', font='starwars'))
        stdscr.refresh()
        time.sleep(self.delay * 5)

        # Loop where k is the last character pressed
        while self.state != EXIT:  # (k != ord('q')):

            # Initialization
            stdscr.clear()
            height, width = stdscr.getmaxyx()
            stdscr.nodelay(1)
            old_snake_body = deepcopy(self.snake.body)
            status_str = ""

            # Read and act on input
            k = stdscr.getch()
            if k != -1:
                char = chr(k)
                direction = None if char not in mapping else mapping[char]
                if char == "q":
                    self.state = EXIT
                elif self.state == INIT and direction:
                    self.state = RUNNING
                    x, y = self.snake.move(self.apple.coordinates, direction)
                elif char == "p":
                    if self.state == RUNNING:
                        self.state = PAUSED
                    elif self.state == PAUSED:
                        self.state = RUNNING
                elif char == "r" and self.state == GAMEOVER:
                    midpoint = (int(width/2), int(height/2))
                    self.apple = Apple(width, height, [midpoint])
                    self.snake = Snake([midpoint], None)
                    self.state = INIT
                    stdscr.addstr(figlet_format('READY PLAYER ONE', font='starwars'))
                    stdscr.refresh()
                    time.sleep(self.delay * 5)
                elif self.state == RUNNING and direction:
                    x, y = self.snake.move(self.apple.coordinates, direction)
            elif self.state == RUNNING:
                status_str += "PRESS P TO PAUSE"
                x, y = self.snake.move(self.apple.coordinates)

            if self.state == RUNNING:
                if (x, y) in old_snake_body or x == 0 or y == 0 or x == self.width + 1 or y == self.height + 1:
                    self.state = GAMEOVER
                elif (x, y) == self.apple.coordinates:
                    self.apple.respawn(self.snake.body)
            elif self.state == INIT:
                status_str = "TO BEGIN, USE THE WASD KEYS TO MOVE UP, LEFT, DOWN AND RIGHT RESPECTIVELY"
            elif self.state == PAUSED:
                status_str = "PAUSED: PRESS P TO RESUME"
            elif self.state == GAMEOVER:
                status_str = "GAME OVER: PRESS R TO START NEW GAME"

            gameboard_str = ""
            for y in range(self.height + 2):
                for x in range(self.width + 2):
                    left = x == 0
                    right = x == self.width + 1
                    top = y == 0
                    bottom = y == self.height + 1
                    snake_body = (x, y) in self.snake.body
                    snake_head = (x, y) == self.snake.head()
                    apple = (x, y) == self.apple.coordinates
                    if ((top and left) or (top and right) or
                        (bottom and left) or (bottom and right)):
                        gameboard_str += "+"
                    elif right or left:
                        gameboard_str += "|"
                    elif top or bottom:
                        gameboard_str += "-"
                    elif snake_head:
                        gameboard_str += "x"
                    elif snake_body:
                        gameboard_str += "o"
                    elif apple:
                        gameboard_str += "*"
                    else:
                        gameboard_str += " "
                gameboard_str += "\n"

            status_str += "\nPRESS Q TO QUIT"
            if self.state != EXIT:
                printstr = gameboard_str + "\n\n" + status_str
            stdscr.addstr(printstr)
            stdscr.addstr("\n GAME STATE: {}".format(self.state))
            # Refresh the screen
            stdscr.refresh()
            time.sleep(self.delay)


def main():
    game = Game(30, 30, delay=0.3)
    curses.wrapper(game.render)


if __name__ == '__main__':
    main()
