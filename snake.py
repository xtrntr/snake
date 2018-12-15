import time
import curses

UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)

mapping = {
    "w": UP,
    "a": LEFT,
    "s": DOWN,
    "d": RIGHT,
}


class Snake(object):
    def __init__(self, body, direction):
        # body is a list of tuples
        # first in the list is the head
        self.body = body
        self.direction = direction

    # add position to front of snake body and pop off the back
    def take_step(self):

        new_position = (self.body[-1][0] + self.direction[0],
                        self.body[-1][1] + self.direction[1])
        self.body = self.body[1:] + [new_position]
        return new_position

    def set_direction(self, direction):
        self.direction = direction

    def valid_direction(self, direction):
        return not (set([self.direction, direction]) == set([UP, DOWN]) or set([self.direction, direction]) == set([LEFT, RIGHT]))

    def move(self, direction=None):
        if direction and self.valid_direction(direction):
            self.set_direction(direction)
        return self.take_step()

    def head(self):
        return self.body[-1]


class Game(object):

    def __init__(self, height, width):
        self.height = height
        self.width = width
        self.gameboard = [ [" "] * self.height for i in range(self.width) ]
        self.state = True

        head = (int(width/2), int(height/2))
        tail = (int(width/2), int(height/2) - 1)
        self.snake = Snake([tail, head], DOWN)

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

        # Loop where k is the last character pressed
        while self.state:  # (k != ord('q')):

            # Initialization
            stdscr.clear()
            height, width = stdscr.getmaxyx()
            old_snake_body = self.snake.body

            # do not wait for input when calling getch
            stdscr.nodelay(1)
            k = stdscr.getch()
            if k != -1:
                char = chr(k)
                direction = None if char not in mapping else mapping[char]
                x, y = self.snake.move(direction)
            else:
                x, y = self.snake.move()

            if (x, y) in old_snake_body or x == 0 or y == 0 or x == self.width + 1 or y == self.height + 1:
                stdscr.refresh()
                self.state = False

            rtn_string = ""
            for y in range(self.height + 2):
                for x in range(self.width + 2):
                    left = x == 0
                    right = x == self.width + 1
                    top = y == 0
                    bottom = y == self.height + 1
                    snake_body = (x, y) in self.snake.body
                    snake_head = (x, y) == self.snake.head()
                    if ((top and left) or (top and right) or
                        (bottom and left) or (bottom and right)):
                        rtn_string += "+"
                    elif right or left:
                        rtn_string += "|"
                    elif top or bottom:
                        rtn_string += "-"
                    elif snake_head:
                        rtn_string += "x"
                    elif snake_body:
                        rtn_string += "o"
                    else:
                        rtn_string += self.gameboard[x-1][y-1]
                rtn_string += "\n"

            stdscr.addstr(rtn_string)
            stdscr.addstr("\nHeight: {}\n".format(self.height))
            stdscr.addstr("Width: {}\n".format(self.width))
            stdscr.addstr("Snake head: {}, body: {}, direction: {}".format(self.snake.head(), self.snake.body, self.snake.direction))
            # Refresh the screen
            stdscr.refresh()
            time.sleep(0.5)

def main():
    game = Game(5, 5)
    curses.wrapper(game.render)

if __name__ == '__main__':
   main()
