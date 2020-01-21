import numpy as np
from controller import Controller
from vision import Vision
from time import sleep
import sys


class Gameplayer:
    def __init__(self):
        self.window_name = 'Gemgem'
        self.board = np.zeros((8, 8))
        self.static_templates = {
            1: 'graphics/gem1_background.png',
            2: 'graphics/gem2_background.png',
            3: 'graphics/gem3_background.png',
            4: 'graphics/gem4_background.png',
            5: 'graphics/gem5_background.png',
            6: 'graphics/gem6_background.png',
            7: 'graphics/gem7_background.png',
        }
        self.tile_width = 64
        self.vision = Vision(self.static_templates, self.window_name)
        self.control = Controller()

    def read_board(self):
        coords = self.vision.match_templates()
        for key in coords.keys():
            coords[key][0] //= self.tile_width
            coords[key][1] //= self.tile_width

            self.board[coords[key][0], coords[key][1]] = key

    def find_match(self):
        """Finds a pair of coordinates that can generate a match"""
        def has_match(interval):
            """checks if there is a match in a given 6 or 4 subinterval"""
            vals, counts = np.unique(interval, return_counts=True)
            curr_tile = vals[counts.argmax()]
            mask = interval == curr_tile
            if len(interval.shape) > 1:
                if np.sum(counts > 2) == 0:
                    return False
                if counts.max() > 2 and (0 in np.sum(mask, axis=0)):
                    return False
                return mask, curr_tile
            if counts.max() == 3:
                return mask, curr_tile

        vertically = False
        # firstly check horizontally, then vertically
        for board in (self.board, np.flipud(self.board).T):

            # check for six-matches, like so:
            # @@*
            # #$@
            for h in range(2, 9):
                for w in range(3, 9):
                    six = board[h-2:h, w-3:w]
                    if not has_match(six):
                        continue
                    mask, val = has_match(six)
                    y0 = np.sum(mask, axis=1).argmax()
                    y1 = np.sum(mask, axis=1).argmin()
                    if y0 == y1:
                        y0, y1 = 0, 1
                    x = w - (2-mask[y0].argmin())-1
                    y0 = h-y0-1
                    y1 = h-y1-1
                    coords = np.array([(x, y0), (x, y1)])
                    if vertically:
                        coords = np.array([(y0, 7-x), (y1, 7-x)])
                    return coords

            #  check for four-matches, like so:
            # @@*@
            for y in range(8):
                for w in range(4, 9):
                    four = board[y, w-4:w]
                    if not has_match(four):
                        continue
                    mask, val = has_match(four)
                    x0 = np.sum(mask).argmin()
                    x1 = x0
                    if x0 == 1:
                        x1 -= 1
                    else:
                        x1 += 1
                    x0 = w - x0 - 1
                    x1 = w - x1 - 1
                    coords = np.array([(x0, y), (x1, y)])
                    if vertically:
                        coords = np.array([(y, 7 - x0), (y, 7 - x1)])
                    return coords
            vertically = True

    def make_move(self, game_pos_tpl):
        """calculates the coordinates of matching positions on the screen and clicks on them"""
        top = self.vision.find_window()['top']
        left = self.vision.find_window()['left']
        win = np.array([[left, top], [left, top]])
        pos1, pos2 = game_pos_tpl * self.tile_width + self.tile_width//2 + win

        self.control.move_mouse(pos1[0], pos1[1])
        self.control.left_mouse_click()
        sleep(1)
        self.control.move_mouse(pos2[0], pos2[1])
        self.control.left_mouse_click()

    def board_is_relevant(self):
        """check if past and present screenshots are equal"""
        if np.allclose(self.vision.take_screenshot(), self.vision.frame):
            return True
        return False

    def play(self, n_steps):
        for i in range(n_steps):
            print('========= CURRENT BOARD =========:')
            print(self.board)
            if not self.board_is_relevant():
                self.vision.refresh_frame()
                self.read_board()
            coords = self.find_match()
            print('FOUND A MATCH:')
            print(coords)
            self.make_move(coords)
            sleep(1)


if __name__ == '__main__':
    pl = Gameplayer()
    pl.read_board()
    pl.play(eval(sys.argv[1]))
