import numpy as np
import scipy
import matplotlib.pyplot as plt
import cv2
import random
import torch
import multiprocessing
import time
from functools import lru_cache
from skimage.draw import line
from src.ImageClass import *
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QApplication



class Solver():
    def __init__(self, algo: str, signal_formula: str, pixel_size: int, resist_thickness: int, k: float, E: float, masks: list, recalculate: bool,\
                 dp2:tuple, dp3:tuple):
        # self.parent_ = parent
        self.algo = algo
        self.signal_formula = signal_formula
        self.pixel_size = pixel_size
        self.resist_thickness = resist_thickness

        self.masks_list = masks
        self.mask_objects = []

        self.color_back = 110
        self.color_hole = 85
        self.k = k
        self.E = E
        self.recalculate = recalculate

        self.dp2 = dp2
        self.dp3 = dp3

        self.i = 0


        self.cpu_count = multiprocessing.cpu_count()
        # self.process()
        if self.recalculate: self.process_pool()


    def draw_gradient_line(self, img, start_point, points, colors, thickness=4):
        start = start_point
        for i in range(1, len(points) - 1):
            # if img[start[1], start[0]] == 0 or img[start[1], start[0]] == 255 or img[start[1], start[0]]==128:
            if i+1 != len(points)-1:
                cv2.line(img, start, points[i+1], colors[i], thickness)
            start = points[i]
    


    def closest_point(self, point, array):
        diff = array - point
        distance = np.einsum('ij,ij->i', diff, diff)
        return np.argmin(distance), distance
    

    def compute_previous_pixel(self, first_pixel, last_pixel, distance=1):
        x1, y1 = first_pixel
        x2, y2 = last_pixel

        length = np.sqrt((x2 - x1)**2 + (y2 - y1)**2)
        length = 1 if length == 0 else length
        t = -distance / length
        x_t = np.round((x1 + t * (x2 - x1)), 0).astype(np.int32)
        y_t = np.round((y1 + t * (y2 - y1)), 0).astype(np.int32)

        return (x_t, y_t)
    

    def compute_next_pixel(self, first_point, last_point, distance=1):
        x1, y1 = first_point
        x2, y2 = last_point

        length = np.sqrt((x2 - x1)**2 + (y2 - y1)**2)

        t = 1 + distance / length
        x_t = np.round((x1 + t * (x2 - x1)), 0).astype(np.int32)
        y_t = np.round((y1 + t * (y2 - y1)), 0).astype(np.int32)

        return (x_t, y_t)
    

    def detect_cont(self, img):
        cont, _ = cv2.findContours(img, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
        return cont
    
    # @lru_cache
    def bezier(self, line, t, prev, color_back, color_hole):
        if prev == 0.0:
            point1 = (0, color_back)
            point4 = (len(line), color_hole)
            point2 = (self.dp3[0]*len(line), self.dp3[1]*(color_back - color_hole) + color_hole) # default: (len(line), color_back)
            # point3 = (self.dp3[0]*len(line), self.dp3[1]*(np.abs(color_hole - color_back)) - color_back)
            point3 = (self.dp2[0]*len(line), self.dp2[1]*(color_back - color_hole) + color_hole) #default: (0, color_hole)
            # point2 = (self.dp2[0]*len(line), self.dp2[1]*(np.abs(color_hole - color_back)) - color_back)

        if prev == 255.0:
            point1 = (0, color_hole)
            point4 = (len(line), color_back)
            point3 = (self.dp3[0]*len(line), self.dp3[1]*(color_back - color_hole) + color_hole) # dafault: (0, color_back)
            # point3 = (self.dp3[0]*len(line), self.dp3[1]*(color_hole - color_back) + color_back)
            point2 = (self.dp2[0]*len(line), self.dp2[1]*(color_back - color_hole) + color_hole) # default: (len(line), color_hole)
            # point2 = (self.dp2[0]*len(line), self.dp2[1]*(color_hole - color_back) + color_back)
        x = point1[0]*(1-t)**3 + point2[0]*3*t*(1-t)**2 + point3[0]*3*t**2*(1-t) + point4[0]*t**3
        vals = point1[1]*(1-t)**3 + point2[1]*3*t*(1-t)**2 + point3[1]*3*t**2*(1-t) + point4[1]*t**3
        return x, vals


    def transform_bezier(self, img, ext, int):
        width_img = np.zeros_like(img, dtype=np.float32)
        new_angles = np.zeros_like(img, dtype=np.float32)
        color_map = np.zeros_like(img, dtype=np.float32)

        for cont_ext, cont_int in zip(ext, int):
            for point in cont_ext:
                    min_dist = float('inf')
                    index, dist = self.closest_point(point, cont_int)
                    if dist[index] < min_dist :
                        min_dist = dist[index].item()
                        nearest_point = cont_int[index] 
                        prev = [self.compute_previous_pixel(point, nearest_point)]
                        discrete_line = list(zip(*line(*prev[0], *nearest_point))) # find all pixels from the line
                        dist_ = len(discrete_line) - 2

                    if dist_ > 1:
                        new_line = np.zeros(dist_*self.pixel_size, dtype=np.float32)
                        # x, y = self.bezier(new_line, np.linspace(0, 1, len(new_line)), 0.0, 100, self.resist_thickness)
                        x, y = self.bezier(new_line, np.linspace(0, 1, len(new_line)), 0.0, self.resist_thickness, 100)

                        # x, colors = self.bezier(new_line, np.linspace(0, 1, len(new_line)), 0.0, self.color_hole, self.color_back)
                        x, colors = self.bezier(new_line, np.linspace(0, 1, len(new_line)), 0.0, self.color_back, self.color_hole)

                        reshaped_y  = np.array(y).reshape(-1, self.pixel_size)  # Разбиваем на подмассивы по self.pixel_size элементов
                        averages_y = np.max(reshaped_y, axis=1)

                        reshaped_colors  = np.array(colors).reshape(-1, self.pixel_size)  # Разбиваем на подмассивы по self.pixel_size элементов
                        angles = np.arctan(np.abs(np.gradient(y)))
                        # if dist_==2:print(angles)
                        new_angl = angles[::self.pixel_size]
                        reshaped_angls  = np.array(angles).reshape(-1, self.pixel_size)  # Разбиваем на подмассивы по self.pixel_size элементов
                        averages_angls = np.max(reshaped_angls, axis=1)
                        max_indices = np.argmax(reshaped_angls, axis=1)
                        averages_colors = reshaped_colors[np.arange(len(reshaped_colors)), max_indices]
                    
                        self.draw_gradient_line(color_map, point, discrete_line, averages_colors, thickness=2)
                        if dist_>40: self.draw_gradient_line(new_angles, point, discrete_line, averages_angls, thickness=3)
                        else:self.draw_gradient_line(new_angles, point, discrete_line, averages_angls, thickness=2)
                            

                    elif dist_ == 1:
                        y = [self.resist_thickness-10]
                        averages_colors = [(self.color_back - 2)]
                        angles = [np.arctan(y[0]/(dist_*self.pixel_size))]
                        cv2.line(new_angles, point, nearest_point, np.deg2rad(89), 2)
                        cv2.line(color_map, point, nearest_point, (np.tan(np.deg2rad(89))*self.pixel_size * 110)/self.resist_thickness, 2)

                    cv2.line(width_img, point, nearest_point, dist_, 3)


        for cont_ext, cont_int in zip(ext, int):
            for point in cont_int:
                    min_dist = float('inf')
                    index, dist = self.closest_point(point, cont_ext)
                    if dist[index] < min_dist :
                        min_dist = dist[index].item()
                        nearest_point = cont_ext[index]
                        next = [self.compute_next_pixel(point, nearest_point)]
                        discrete_line = list(zip(*line(*point, *next[0]))) # find all pixels from the line
                        dist_ = len(discrete_line) - 2

                    if dist_ == 0:
                        dist_ = 1

                    if dist_ > 1:
                        new_line = np.zeros(dist_*self.pixel_size, dtype=np.float32)
                        # x, y = self.bezier(new_line, np.linspace(0, 1, len(new_line)), 255.0, 100, self.resist_thickness)
                        x, y = self.bezier(new_line, np.linspace(0, 1, len(new_line)), 255.0, self.resist_thickness, 100)

                        # x, colors = self.bezier(new_line, np.linspace(0, 1, len(new_line)), 255.0, self.color_hole, self.color_back)
                        x, colors = self.bezier(new_line, np.linspace(0, 1, len(new_line)), 255.0, self.color_back, self.color_hole)
                        
                        reshaped_y  = np.array(y).reshape(-1, self.pixel_size)  # Разбиваем на подмассивы по self.pixel_size элементов
                        averages_y = np.max(reshaped_y, axis=1)
                        reshaped_colors  = np.array(colors).reshape(-1, self.pixel_size)  # Разбиваем на подмассивы по self.pixel_size элементов
                        angles = np.arctan(np.abs(np.gradient(y)))
                        # if dist_==2:print(angles)
                        
                        reshaped_angls  = np.array(angles).reshape(-1, self.pixel_size)  # Разбиваем на подмассивы по self.pixel_size элементов
                        averages_angls = np.max(reshaped_angls, axis=1)
                        max_indices = np.argmax(reshaped_angls, axis=1)
                        averages_colors = reshaped_colors[np.arange(len(reshaped_colors)), max_indices]

                    elif dist_ == 1:
                        y = [self.resist_thickness-10]
                        averages_colors = [(self.color_back - 2)]
                        angles = [np.arctan(y[0]/(dist_*self.pixel_size))]
                        cv2.line(new_angles, point, nearest_point, np.deg2rad(89), 2)
                        cv2.line(color_map, point, nearest_point, (np.tan(np.deg2rad(89))*self.pixel_size * 110)/self.resist_thickness, 2)
                    
                    if new_angles[point[1], point[0]]  == 0:
                        # self.draw_gradient_line(new_angles, next[0], discrete_line[-1::-1], averages_angls[-1::-1], thickness=2)
                        self.draw_gradient_line(new_angles, point, discrete_line[-1::-1], averages_angls[-1::-1], thickness=2)
                        # self.draw_gradient_line(new_angles, next[0], discrete_line, averages_angls, thickness=2)
                        # self.draw_gradient_line(new_angles, point, discrete_line, averages_angls, thickness=2)

                    if color_map[point[1], point[0]]  == 0:
                        # self.draw_gradient_line(color_map, next[0], discrete_line[-1::-1], averages_colors[-1::-1], thickness=2)
                        self.draw_gradient_line(color_map, point, discrete_line[-1::-1], averages_colors[-1::-1], thickness=2)
                        # self.draw_gradient_line(color_map, next[0], discrete_line, averages_colors, thickness=1)
                        # self.draw_gradient_line(color_map, point, discrete_line, averages_colors, thickness=1)

                    cv2.line(width_img, point, nearest_point, dist_, 2)


        img_cp = img.copy()
        mask = img_cp != 128 
        width_img[mask] = 0
        new_angles[mask] = 0
        color_map[img == 0] = self.color_back
        color_map[img == 255] = self.color_hole

        zeros = np.where((color_map==0) & (img==128))
        if len(zeros[0]) > 0:
            tmp = np.zeros_like(img)
            cv2.drawContours(tmp, [ext[0]], -1, 255, 0)
            c = self.detect_cont(tmp)
            ext = np.argwhere(tmp > 0)
            ext = np.array([list(reversed(ex)) for ex in ext])
            
            for i in range(len(zeros[0])):
                point = (zeros[0][i], zeros[1][i])

                index_int, dist_int = self.closest_point(point, cont_int)
                index_ext, dist_ext = self.closest_point(point, ext)
                nearest_point_int = cont_int[index_int]
                nearest_point_ext = ext[index_ext]
                discrete_line_int = list(zip(*line(*point, *nearest_point_int)))
                discrete_line_ext = list(zip(*line(*point, *nearest_point_ext)))
                distance_int = len(discrete_line_int)
                distance_ext = len(discrete_line_ext)
                if distance_int < distance_ext:
                    val = self.color_back - distance_int*np.tan(new_angles[point[0], point[1]])/(distance_ext + distance_int)
                else:
                    val = self.color_hole + distance_ext*np.tan(new_angles[point[0], point[1]])/(distance_ext + distance_int)

                if val == 85.0:
                    val = (110.0 + 85.0)/2 -random.randint(10, 14)
                elif val == 110.0:
                    val = (110.0 + 85.0)/2 -random.randint(10, 14)
                color_map[point[0], point[1]] = np.abs(val)
        color_map[img == 0] = 0
        color_map[img == 255] = 0
        return width_img, new_angles, color_map
    

    def transform_radius(self, img, ext, int):

        width_img = np.zeros_like(img, dtype=np.float32)
        new_angles = np.zeros_like(img, dtype=np.float32)
        color_map = np.zeros_like(img, dtype=np.float32)

        flag = True
        for cont_ext, cont_int in zip(ext, int):
            for point in cont_ext:
                radius = 1
                flag = True
                while flag:
                    mask = np.zeros_like(img)
                    mask = cv2.circle(mask, point, radius, 255, -1)
                    mask = cv2.inRange(mask, 255,255)
                    cont_mask, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
                    mask_cont = np.zeros_like(img)
                    cv2.drawContours(mask_cont, cont_mask,  -1, 1, 0)
                    nonzero = np.argwhere(mask_cont > 0)
                    nonzero = np.array([list(reversed(nonz)) for nonz in nonzero])
                    intersect = np.array([x for x in set(tuple(x) for x in nonzero) & set(tuple(x) for x in cont_int)])
                    if len(intersect) != 0:
                        flag=False
                    else:
                        radius += 1

                dist = float('inf')
                for dot in intersect:
                    dist_ = np.sqrt((point[0] - dot[0])**2 + (point[1] - dot[1])**2)
                    if dist_ < dist:
                        dist = ((np.round(dist_, 0)).astype(np.int32)).item() + 1
                        nearest_point = dot
                
                dist_ = dist - 1
                discrete_line = list(zip(*line(*point, *nearest_point))) # find all pixels from the line
                # discrete_line_x = np.array(list(zip(*discrete_line))[0])
                
                next = [self.compute_next_pixel(point, nearest_point)]

                if dist_ > 2:
                    new_line = np.zeros(dist_*self.pixel_size, dtype=np.float32)
                    x, y = self.bezier(new_line, np.linspace(0, 1, len(new_line)), 0.0, 100, self.resist_thickness)

                    x, colors = self.bezier(new_line, np.linspace(0, 1, len(new_line)), 0.0, self.color_hole, self.color_back)

                    reshaped_colors  = np.array(colors).reshape(-1, self.pixel_size)  # Разбиваем на подмассивы по self.pixel_size элементов
                    angles = np.arctan(np.abs(np.gradient(y)))
                    reshaped_angls  = np.array(angles).reshape(-1, self.pixel_size)  # Разбиваем на подмассивы по self.pixel_size элементов
                    averages_angls = np.max(reshaped_angls, axis=1)
                    max_indices = np.argmax(reshaped_angls, axis=1)
                    averages_colors = reshaped_colors[np.arange(len(reshaped_colors)), max_indices]
                
                    self.draw_gradient_line(color_map, point, discrete_line, averages_colors, thickness=2)
                    self.draw_gradient_line(new_angles, point, discrete_line, averages_angls, thickness=1)
                elif dist_ == 2:
                    new_line = [0] * 2 * self.pixel_size
                    x, y = self.bezier(new_line, np.linspace(0, 1, len(new_line)),0.0, self.resist_thickness, 100)
                    x, colors = self.bezier(new_line, np.linspace(0, 1, len(new_line)), 0.0, self.color_back, self.color_hole)

                    angles = np.arctan(np.abs(np.gradient(y)))
                    reshaped_angls  = np.array(angles).reshape(-1, self.pixel_size)  # Разбиваем на подмассивы по self.pixel_size элементов
                    averages_angls = np.max(reshaped_angls, axis=1)
                    max_indices = np.argmax(reshaped_angls, axis=1)
                    reshaped_colors  = np.array(colors).reshape(-1, self.pixel_size)  # Разбиваем на подмассивы по self.pixel_size элементов
                    averages_colors = reshaped_colors[np.arange(len(reshaped_colors)), max_indices]
                    averages_angls = [averages_angls[0], averages_angls[0], averages_angls[1], averages_angls[1]]
                    averages_colors = [averages_colors[0], averages_colors[0], averages_colors[1], averages_colors[1]]

                    self.draw_gradient_line(color_map, point, discrete_line, averages_colors, thickness=2)
                    self.draw_gradient_line(new_angles, point, discrete_line, averages_angls, thickness=1)

                elif dist_ == 1:
                    y = [self.resist_thickness-10]
                    averages_colors = [(self.color_back - 2)]
                    angles = [np.arctan(y[0]/(dist_*self.pixel_size))]
                    cv2.line(new_angles, point, nearest_point, np.deg2rad(89), 2)
                    cv2.line(color_map, point, nearest_point, (np.tan(np.deg2rad(89))*self.pixel_size * 110)/self.resist_thickness, 2)

                cv2.line(width_img, point, nearest_point, dist_, 3)


        for cont_ext, cont_int in zip(ext, int):
            for point in cont_int:
                radius = 1
                flag = True
                while flag:
                    mask = np.zeros_like(img)
                    mask = cv2.circle(mask, point, radius, 255, -1)
                    mask = cv2.inRange(mask, 255,255)
                    cont_mask, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
                    mask_cont = np.zeros_like(img)
                    cv2.drawContours(mask_cont, cont_mask,  -1, 1, 0)
                    nonzero = np.argwhere(mask_cont > 0)
                    nonzero = np.array([list(reversed(nonz)) for nonz in nonzero])
                    
                    intersect = np.array([x for x in set(tuple(x) for x in nonzero) & set(tuple(x) for x in cont_ext)])
                    if len(intersect) != 0:
                        flag=False
                    else:
                        radius += 1

                dist = float('inf')
                for dot in intersect:
                    dist_ = np.sqrt((point[0] - dot[0])**2 + (point[1] - dot[1])**2)
                    if dist_ < dist:
                        dist = ((np.round(dist_, 0)).astype(np.int32)).item() + 1
                        nearest_point = dot
                dist_ = dist - 1
                discrete_line = list(zip(*line(*point, *nearest_point))) # find all pixels from the line
                
                next = [self.compute_next_pixel(point, nearest_point)]

                if dist_ == 0:
                    dist_ = 1

                if dist_ > 2:
                    new_line = np.zeros(dist_*self.pixel_size, dtype=np.float32)
                    x, y = self.bezier(new_line, np.linspace(0, 1, len(new_line)), 255.0, 100, self.resist_thickness)
                    x, colors = self.bezier(new_line, np.linspace(0, 1, len(new_line)), 255.0, self.color_hole, self.color_back)
                    reshaped_colors  = np.array(colors).reshape(-1, self.pixel_size)  # Разбиваем на подмассивы по self.pixel_size элементов
                    angles = np.arctan(np.abs(np.gradient(y)))
                    reshaped_angls  = np.array(angles).reshape(-1, self.pixel_size)  # Разбиваем на подмассивы по self.pixel_size элементов
                    averages_angls = np.max(reshaped_angls, axis=1)
                    max_indices = np.argmax(reshaped_angls, axis=1)
                    averages_colors = reshaped_colors[np.arange(len(reshaped_colors)), max_indices]

                elif dist_ == 2:
                    new_line = [0] * 2 * self.pixel_size
                    x, y = self.bezier(new_line, np.linspace(0, 1, len(new_line)),0.0, self.resist_thickness, 100)
                    x, colors = self.bezier(new_line, np.linspace(0, 1, len(new_line)), 0.0, self.color_back, self.color_hole)
                    angles = np.arctan(np.abs(np.gradient(y)))
                    reshaped_angls  = np.array(angles).reshape(-1, self.pixel_size)  # Разбиваем на подмассивы по self.pixel_size элементов
                    averages_angls = np.max(reshaped_angls, axis=1)
                    max_indices = np.argmax(reshaped_angls, axis=1)
                    reshaped_colors  = np.array(colors).reshape(-1, self.pixel_size)  # Разбиваем на подмассивы по self.pixel_size элементов
                    averages_colors = reshaped_colors[np.arange(len(reshaped_colors)), max_indices]
                    averages_angls = [averages_angls[0], averages_angls[0], averages_angls[1], averages_angls[1]]
                    averages_colors = [averages_colors[0], averages_colors[0], averages_colors[1], averages_colors[1]]

                    # draw_gradient_line(color_map, point, discrete_line, averages_colors, thickness=2)
                    # draw_gradient_line(new_angles, point, discrete_line, averages_angls, thickness=1)

                elif dist_ == 1:
                    y = [self.resist_thickness-10]
                    averages_colors = [(self.color_back - 2)]
                    angles = [np.arctan(y[0]/(dist_*self.pixel_size))]
                    cv2.line(new_angles, point, nearest_point, np.deg2rad(89), 2)
                    cv2.line(color_map, point, nearest_point, (np.tan(np.deg2rad(89))*self.pixel_size * 110)/self.resist_thickness, 2)
                
                if new_angles[point[1], point[0]]  == 0:
                    # self.draw_gradient_line(new_angles, next[0], discrete_line[-1::-1], averages_angls[-1::-1], thickness=2)
                    self.draw_gradient_line(new_angles, point, discrete_line[-1::-1], averages_angls[-1::-1], thickness=2)

                if color_map[point[1], point[0]]  == 0:
                    # self.draw_gradient_line(color_map, next[0], discrete_line[-1::-1], averages_colors[-1::-1], thickness=2)
                    self.draw_gradient_line(color_map, point, discrete_line[-1::-1], averages_colors[-1::-1], thickness=2)

                cv2.line(width_img, point, nearest_point, dist_, 2)


        img_cp = img.copy()
        mask = img_cp != 128 
        width_img[mask] = 0
        new_angles[mask] = 0
        color_map[img == 0] = self.color_back
        color_map[img == 255] = self.color_hole
        
        zeros = np.where((color_map==0) & (img==128))
        if len(zeros[0]) > 0:
            tmp = np.zeros_like(img)
            cv2.drawContours(tmp, [ext[0]], -1, 255, 0)
            ext = np.argwhere(tmp > 0)
            ext = np.array([list(reversed(ex)) for ex in ext])
            
            for i in range(len(zeros[0])):
                point = (zeros[0][i], zeros[1][i])

                index_int, dist_int = self.closest_point(point, cont_int)
                index_ext, dist_ext = self.closest_point(point, ext)
                nearest_point_int = cont_int[index_int]
                nearest_point_ext = ext[index_ext]
                discrete_line_int = list(zip(*line(*point, *nearest_point_int)))
                discrete_line_ext = list(zip(*line(*point, *nearest_point_ext)))
                distance_int = len(discrete_line_int)
                distance_ext = len(discrete_line_ext)
                if distance_int < distance_ext:
                    val = self.color_back - distance_int*np.tan(new_angles[point[0], point[1]])/(distance_ext + distance_int)
                else:
                    val = self.color_hole + distance_ext*np.tan(new_angles[point[0], point[1]])/(distance_ext + distance_int)

                if val == 85.0:
                    val = (110.0 + 85.0)/2 -random.randint(10, 14)
                elif val == 110.0:
                    val = (110.0 + 85.0)/2 -random.randint(10, 14)
                color_map[point[0], point[1]] = np.abs(val)
        color_map[img == 0] = 0
        color_map[img == 255] = 0
        return width_img, new_angles, color_map
    
    # original
    def GetSignalk(self, img, angles, color_map):
        signal = np.zeros_like(img, dtype=np.float32)
        alpha_bord = angles[img == 128].copy()
        # alpha_bord[alpha_bord==alpha_bord.min()] = np.radians(1)
        # print(alpha_bord.max(), color_map[angles==alpha_bord.max()])
        alpha_bord[alpha_bord==0.0] = np.radians(1)

        alpha_back = angles[img == 0].copy()
        alpha_hole = angles[img == 255].copy()
        signal[img == 0] = (self.k*(1/(np.abs(np.cos(np.radians(alpha_back + 1)))**(0.87)) - 1) + 1) * color_map[img==0]

        # signal[img == 128] = (self.k * (1/(np.abs(np.cos(np.radians(90)-(np.radians(180 - 90) - alpha_bord)))**(0.87)) - 1) + 1) *color_map[img==128]
        signal[img == 128] = (self.k * (1/(np.abs(np.cos((alpha_bord)))**(0.87)) - 1) + 1) *color_map[img==128]
        
        signal[img == 255] = (self.k * (1 / (np.abs(np.cos(np.radians(alpha_hole + 1)))**(1.1)) - 1) + 1) * color_map[img==255]

        signal = np.clip(signal, 0, 255)

        # signal = cv2.GaussianBlur(signal, (11,11), 0)
        # signal = cv2.GaussianBlur(signal, (9,9), 0)
        return signal  

    def GetSignalE(self, img, angles, color_map):
        signal = np.zeros_like(img, dtype=np.float32)

        alpha_bord = angles[img == 128].copy()
        alpha_bord[alpha_bord==0.0] = np.radians(1)

        alpha_back = angles[img == 0].copy()
        alpha_hole = angles[img == 255].copy()

        signal[img == 0] =  (self.E / (np.abs(np.cos(np.radians(alpha_back + 1)))**(0.87))) + color_map[img==0]

        # signal[crop == 128] = E / np.cos(np.radians(90)-(np.radians(180 - 90) - alpha_bord))**(0.87) + 120
        # signal[crop == 128] = E / np.abs(np.cos(np.radians(90) - alpha_bord))**(0.87) + color_map[crop==128]
        signal[img == 128] = (self.E / (np.abs(np.cos(np.radians(90) - (np.radians(180 - 90) - alpha_bord)))**(0.87))) + color_map[img==128]
        # signal[crop == 255] = E / np.cos(alpha_hole + 1)**(1.1) + 60
        signal[img == 255] = (self.E / (np.abs(np.cos(np.radians(alpha_hole + 1)))**(1.1))) + color_map[img==255]

        signal = np.clip(signal, 0, 255)
        return signal



    def process(self):
        start_ = time.time()
        # QApplication.setOverrideCursor(Qt.CursorShape.WaitCursor)
        for mask in self.masks_list:
            self.mask_objects.append(self.process_single_image(mask))

        # QApplication.restoreOverrideCursor()
        print('Processing time: {0} [sec]'.format(time.time() - start_))

            # print(mask_obj.objects[0].hole_contour, mask_obj.objects[0].border_contour)

    # @staticmethod
    def process_single_image(self, mask):
        mask_obj = Image(mask)
        mask_obj.init_contours()
        for i in range(len(mask_obj.objects)):
            if mask_obj.objects[i] is not None:
                if self.algo == 'algo1':
                    mask_obj.width_map, mask_obj.angles_map, mask_obj.color_map = self.transform_bezier(mask_obj.mask, [mask_obj.objects[i].border_contour], [mask_obj.objects[i].hole_contour])
                elif self.algo == 'algo2': 
                    mask_obj.width_map, mask_obj.angles_map, mask_obj.color_map = self.transform_radius(mask_obj.mask, [mask_obj.objects[i].border_contour], [mask_obj.objects[i].hole_contour])

                mask_obj.color_map[mask_obj.mask == 0] = self.color_back
                mask_obj.color_map[mask_obj.mask == 255] = self.color_hole
                mask_obj.angles_map[mask_obj.mask != 128] = 0.0

                mask_obj.signal = self.GetSignal(mask_obj).copy()
        return mask_obj


    def GetSignal(self, mask_obj):
        if self.signal_formula == 'formula_k' : signal = self.GetSignalk(mask_obj.mask, mask_obj.angles_map, mask_obj.color_map)
        elif self.signal_formula == 'formula_e' : signal = self.GetSignalE(mask_obj.mask, mask_obj.angles_map, mask_obj.color_map)

        nonzero = np.argwhere(signal != 0)
        for pixel in nonzero:
            if mask_obj.mask[pixel[0], pixel[1]] != 0:
                mask_obj.signal[pixel[0], pixel[1]] = signal[pixel[0], pixel[1]]

            elif mask_obj.mask[pixel[0], pixel[1]] == 0:
                mask_obj.signal[pixel[0], pixel[1]] = signal[pixel[0], pixel[1]]

        mask_obj.signal[mask_obj.signal == 0] = np.unique(mask_obj.signal)[1] + 1
        # before = mask_obj.signal[mask_obj.mask==128]
        before = mask_obj.signal[mask_obj.width_map < 3]
        mask_obj.signal = np.clip(cv2.GaussianBlur(mask_obj.signal, (11,11), 0), 0, 255)
        # after = mask_obj.signal[mask_obj.mask==128]
        after = mask_obj.signal[mask_obj.width_map < 3]

        if 1 in mask_obj.width_map or 2 in mask_obj.width_map:
            new_line = np.zeros(3*self.pixel_size, dtype=np.float32)
            x, y = self.bezier(new_line, np.linspace(0, 1, len(new_line)), 0.0, 100, self.resist_thickness)
            x, colors = self.bezier(new_line, np.linspace(0, 1, len(new_line)), 0.0, self.color_hole, self.color_back)
            reshaped_colors  = np.array(colors).reshape(-1, self.pixel_size)  # Разбиваем на подмассивы по self.pixel_size элементов
            angles = np.arctan(np.abs(np.gradient(y)))
            reshaped_angls  = np.array(angles).reshape(-1, self.pixel_size)  # Разбиваем на подмассивы по self.pixel_size элементов
            averages_angls = np.max(reshaped_angls, axis=1)
            max_indices = np.argmax(reshaped_angls, axis=1)
            averages_colors = reshaped_colors[np.arange(len(reshaped_colors)), max_indices]
            mask_3px = np.array([0, 0, 0, 128, 128, 128, 255, 255, 255])
            signal_3px = self.GetSignalk(mask_3px, np.array([0,0,0] + list(averages_angls) + [0,0,0]), np.array([self.color_back,self.color_back,self.color_back] \
                                                                                    + list(averages_colors) + [self.color_hole,self.color_hole,self.color_hole]))
            signal_3px = signal_3px * after.max()/before.max()

        if 3 in mask_obj.width_map and 4 in mask_obj.width_map:
            mask_obj.signal[mask_obj.width_map > 0 ] = mask_obj.signal[mask_obj.width_map > 0] * 0.9
        if 2 in mask_obj.width_map and 3 not in mask_obj.width_map:
            mask_obj.signal[mask_obj.width_map == 2] = np.clip(signal_3px.max() * 1.1,0,255)
            mask_obj.signal[mask_obj.width_map == 1] = np.clip(signal_3px.max() * 1.2,0,255)
        elif 1 in mask_obj.width_map:
            mask_obj.signal[mask_obj.width_map == 2] = np.clip(signal_3px.max() * 1.3,0,255)
            mask_obj.signal[mask_obj.width_map == 1] = np.clip(signal_3px.max() * 1.5,0,255)

        mask_obj.signal = mask_obj.signal.astype(np.uint8)
        # print('MAX VALUE: ', mask_obj.signal.max())

        return mask_obj.signal


    def process_pool(self):
        start_multi_time_v1 = time.time()

        try:
            pool = multiprocessing.Pool(processes = self.cpu_count)
            for mask in pool.map(self.process_single_image, self.masks_list):
                self.mask_objects.append(mask)
        finally:
            pool.close()
            pool.join()
        print('Processing time: {0} [sec]'.format(time.time() - start_multi_time_v1))
