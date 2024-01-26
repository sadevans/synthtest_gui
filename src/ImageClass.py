import cv2
import numpy as np


class Figure():
    def __init__(self, hole_contour):
        self.hole_contour = hole_contour.copy()
        self.border_width = 0
        self.border_contour = hole_contour.copy()
        
class Image():
    def __init__(self, mask: np.array):
        self.mask = mask
        self.color_map = np.zeros_like(mask)
        self.angles_map = np.zeros_like(mask)
        self.width_map = np.zeros_like(mask)

        self.signal = np.zeros_like(mask)
        self.noisy = np.zeros_like(mask)


        self.objects = []

    
    def detect_cont(self, img):
        cont, _ = cv2.findContours(img, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
        return cont


    def init_contours(self):
        mask_hole = cv2.inRange(self.mask, 255, 255)
        mask_border = cv2.inRange(self.mask, 128, 128)

        c_int_ = self.detect_cont(mask_hole)
        c_ext_ = self.detect_cont(mask_border)

        for i in range(len(c_ext_)):
            for j in range(len(c_int_)):
                temp_bord = np.zeros_like(self.mask)
                cv2.drawContours(temp_bord, [c_ext_[i]], -1, 128, -1)
                temp_hole = np.zeros_like(self.mask)
                cv2.drawContours(temp_hole, [c_int_[j]], -1, 255, -1)
                set_border = set(map(tuple, np.argwhere(temp_bord==128)))
                set_hole = set(map(tuple, np.argwhere(temp_hole==255)))
                if set_hole.issubset(set_border):
                    obj = Figure(c_int_[j].reshape(-1, 2)) # создаем объекты класса Figure
                    obj.border_contour = c_ext_[i].reshape(-1, 2).copy()
                    self.objects.append(obj)