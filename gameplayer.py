import numpy as np
from controller import Controller
from vision import Vision
from time import sleep

# todo add game constants
# todo optimize everything
# todo exception handling everywhere
# todo remove odd fields and methods


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
        self.vision = Vision(self.static_templates, self.window_name)
        self.control = Controller()

    def read_board(self):
        coords = self.vision.match_templates()
        for key in coords.keys():
            coords[key][0] //= 64
            coords[key][1] //= 64

            self.board[coords[key][0], coords[key][1]] = key

    def find_match(self):
        def has_match(six):
            vals, counts = np.unique(six, return_counts=True)
            if np.sum(counts > 2) == 0:
                return False
            curr_tile = vals[counts.argmax()]
            mask = six == curr_tile
            if counts.max() > 2 and (0 in np.sum(mask, axis=0)):
                return False
            return mask, curr_tile
        for board in (self.board, self.board.T):
            for h in range(2, 9):
                for w in range(3, 9):
                    six = board[h-2:h, w-3:w]
                    if not has_match(six):
                        continue
                    mask, val = has_match(six)
                    y0 = np.sum(mask, axis=1).argmax()
                    y1 = np.sum(mask, axis=1).argmin()
                    x = w - mask[y0].argmin()-1
                    y0 = h-y0-1
                    y1 = h-y1-1

                    top = self.vision.find_window()['top']
                    left = self.vision.find_window()['left']

                    # if not np.array_equal(board, self.board):
                    #     print('ghjhgfghj')
                    #
                    #     y0 = np.sum(mask, axis=1).argmax()
                    #     y1 = np.sum(mask, axis=1).argmin()
                    #     x = h - mask[y0].argmin() - 1
                    #     y0 = w - y0 - 1
                    #     y1 = w - y1 - 1
                    #
                    #     top = self.vision.find_window()['top']
                    #     left = self.vision.find_window()['left']
                    #
                    #     # win = np.array([[top, left], [top, left]])
                    #     # return np.array([(x, y0), (x, y1)])
                    #
                    #     win = np.array([[left, top], [left, top]])
                    #     ans = np.array([(y0, x), (y1, x)])# * 64 + 32 + win
                    #     return ans

                    win = np.array([[left, top], [left, top]])
                    return np.array([(y0, x), (y1, x)]), mask#*64+32+win

    def make_move(self, pos1, pos2):
        self.control.move_mouse(pos1[0], pos1[1])
        self.control.left_mouse_click()
        sleep(2)
        self.control.move_mouse(pos2[0], pos2[1])
        self.control.left_mouse_click()


    def board_is_relevant(self):
        """check if past and present screenshots are equal"""
        if np.allclose(self.vision.take_screenshot(), self.vision.frame):
            return True
        return False

    def play(self):
        # todo
        for i in range(5):
            if not self.board_is_relevant():
                self.vision.refresh_frame()
                self.read_board()
            coords = self.find_match()
            self.make_move(*coords)
            sleep(2)


pl = Gameplayer()
pl.read_board()
# pl.play()

print(np.transpose(pl.board))
print(pl.find_match())


