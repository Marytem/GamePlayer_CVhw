import cv2
from mss import mss
from PIL import Image
import numpy as np
from subprocess import Popen, PIPE, STDOUT


class Vision:
    def __init__(self, static_templates, window_name):
        self.static_templates = static_templates
        self.templates = {k: cv2.imread(v, 0) for (k, v) in self.static_templates.items()}

        self.window_name = window_name
        self.monitor = self.find_window()
        self.screen = mss()
        self.frame = self.take_screenshot()

    def find_window(self):
        out = Popen(['xwininfo', '-name', self.window_name],
                    stdout=PIPE,
                    stderr=STDOUT)
        stdout, stderr = out.communicate()
        out_rows = stdout.decode().split('\n')
        x, y = (eval(row.split()[-1]) for row in out_rows if "Absolute upper-left" in row)
        # todo explain nunbers add variables
        return {'top': y + 44, 'left': x + 44, 'width': 512, 'height': 512}

    def take_screenshot(self):
        sct_img = self.screen.grab(self.monitor)
        img = Image.frombytes('RGB', sct_img.size, sct_img.rgb)
        img = np.array(img)
        img = self.convert_rgb_to_bgr(img)
        img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        return img_gray

    def convert_rgb_to_bgr(self, img):
        return img[:, :, ::-1]

    def match_templates(self, threshold=0.95):
        """
        Matches template image in a target grayscaled image
        """
        matches = {}
        for label, template in self.templates.items():
            res = cv2.matchTemplate(self.frame, template, cv2.TM_CCOEFF_NORMED)
            loc = np.array(np.where(res >= threshold))
            matches[label] = loc
        return matches

    def refresh_frame(self):
        self.frame = self.take_screenshot()

    # def get_image(self, path):
    #     return cv2.imread(path, 0)
    #
    # def bgr_to_rgb(self, img):
    #     b, g, r = cv2.split(img)
    #     return cv2.merge([r, g, b])

# vis = Vision({
#             1: 'graphics/gem1_background.png',
#             2: 'graphics/gem2_background.png',
#             3: 'graphics/gem3_background.png',
#             4: 'graphics/gem4_background.png',
#             5: 'graphics/gem5_background.png',
#             6: 'graphics/gem6_background.png',
#             7: 'graphics/gem7_background.png',
#         }, 'Gemgem')
#
# print(vis.match_templates())