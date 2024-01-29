import sys
import cv2
import numpy as np
import matplotlib
matplotlib.use('QtAgg')

import matplotlib.pyplot as plt
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas, NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QApplication, QMainWindow, QLabel, QVBoxLayout, QHBoxLayout, QWidget, QPushButton, QLineEdit, QSlider
from PyQt6.QtGui import QPixmap, QImage, QCursor
from PyQt6.QtCore import Qt

from src.Solver import *
from src.PlotsClass import *
from src.Bezier import *


# class Plots(QMainWindow):
#     def __init__(self, parent, img_object, flag_figure):
#         super().__init__()
#         self.parent_ = parent
#         self.img_object = img_object
#         self.flag_figure = flag_figure
#         self.init_UI()

#     def init_UI(self):
#         if self.flag_figure=='circle': self.setWindowTitle("Графики для круга")
#         elif self.flag_figure=='square': self.setWindowTitle("Графики для квадрата")

#         self.setGeometry(100, 100, 600, 600)  # Устанавливаем размеры окна на весь экран

#         self.central_widget = QWidget(self)
#         self.setCentralWidget(self.central_widget)

#         self.layout = QVBoxLayout(self.central_widget)
#         self.figure, self.ax = plt.subplots(2, 3, figsize=(100, 100), dpi=100)
#         self.canvas = FigureCanvas(self.figure)
#         self.toolbar = NavigationToolbar(self.canvas, self)

#         self.layout.addWidget(self.canvas)
#         self.layout.addWidget(self.toolbar)

#         # toolbar_square = NavigationToolbar(self.canvas_square, self)
#         self.render_plots()
#         # vertical_layout_square.addWidget(toolbar_square) 
    

#     def render_plots(self):
#         self.ax[0,0].cla()
#         self.ax[0,1].cla()
#         self.ax[0,2].cla()

#         self.ax[1,0].cla()
#         self.ax[1,1].cla()
#         self.ax[1,2].cla()

#         self.ax[0,0].imshow(self.img_object.width_map)
#         self.ax[0,0].set_title('Визуализация значений ширины границы')
#         self.ax[1,0].plot(self.img_object.width_map[200,:])
#         self.ax[1,0].grid()


#         self.ax[0,1].imshow(self.img_object.angles_map)
#         self.ax[0,1].set_title('Визуализация значений углов')
#         self.ax[1,1].plot(self.img_object.angles_map[200,:])
#         self.ax[1,1].grid()

#         self.ax[0,2].imshow(self.img_object.color_map)
#         self.ax[0,2].set_title('Визуализация значений цветов')
#         self.ax[1,2].plot(self.img_object.color_map[200,:])
#         self.ax[1,2].grid()

#         self.canvas.draw()

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.mask_w = 400
        self.mask_h = 400
        self.slice_y1 = 200
        self.label1_slice_y1 = 200
        self.label2_slice_y1 = 200

        self.label1_slice_x1 = 200
        self.label2_slice_x1 = 200


        self.radius = 50
        self.border_width = 10

        self.resist_thickness = 700
        self.silicon_thickness = 100
        self.pixel_size = 12
        self.transform_algo = 'bezier'
        self.algo = 'algo1'
        self.k_value = 0.125
        self.E_value = 25
        self.signal_formula = 'formula_k'
        
        self.y = 0

        self.prev_cursor_pos =QCursor.pos()
        self.cursor_pos = QCursor.pos()
        self.flag_render_circle = 'horizontally'
        self.flag_render_square = 'horizontally'

        self.dp3 = (0, 1)
        self.dp2 = (1, 0)




        self.init_ui()

    def init_ui(self):
        self.setWindowTitle('GUI')
        self.setGeometry(0, 0, 1920, 1080)  # Устанавливаем размеры окна на весь экран

        self.central_widget = QWidget(self)
        self.setCentralWidget(self.central_widget)

        self.layout = QVBoxLayout(self.central_widget)

        horizontal_layout_imgs = QHBoxLayout() # для размещения картинок

        vertical_layout_circle = QVBoxLayout() # для круга
        vertical_layout_square = QVBoxLayout() # для квадрата

        vertical_layout_config = QVBoxLayout() # для конфигурации

        # рендер картинок

        self.mask_label_1 = QLabel(self)
        self.mask_label_1.setCursor(Qt.CursorShape.CrossCursor)
        self.mask_label_1.mouseMoveEvent = self.mouseMoveEvent_label1
        vertical_layout_circle.addWidget(self.mask_label_1)
        vertical_layout_circle.setAlignment(self.mask_label_1, Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignVCenter)


        self.button_show_maps_label1 = QPushButton('Графики ширин, углов, цветов для круга')
        self.button_show_maps_label1.clicked.connect(self.show_plots_circle)
        vertical_layout_circle.addWidget(self.button_show_maps_label1)
        
        self.mask_label_2 = QLabel(self)
        self.mask_label_2.setCursor(Qt.CursorShape.CrossCursor)
        self.mask_label_2.mouseMoveEvent = self.mouseMoveEvent_label2

        vertical_layout_square.addWidget(self.mask_label_2)
        vertical_layout_square.setAlignment(self.mask_label_2, Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignVCenter)

        self.button_show_maps_label2 = QPushButton('Графики ширин, углов, цветов для квадрата')
        self.button_show_maps_label2.clicked.connect(self.show_plots_square)
        vertical_layout_square.addWidget(self.button_show_maps_label2)


        self.update_images()

        # render plots
        self.figure_circle, self.ax_circle = plt.subplots(figsize=(1,1), dpi=100)
        self.canvas_circle = FigureCanvas(self.figure_circle)
        vertical_layout_circle.addWidget(self.canvas_circle) 

        toolbar_circle = NavigationToolbar(self.canvas_circle, self)
        vertical_layout_circle.addWidget(toolbar_circle) 

        self.figure_square, self.ax_square = plt.subplots(figsize=(1,1), dpi=100)
        self.canvas_square = FigureCanvas(self.figure_square)
        vertical_layout_square.addWidget(self.canvas_square) 

        toolbar_square = NavigationToolbar(self.canvas_square, self)
        vertical_layout_square.addWidget(toolbar_square) 


        self.update_plots()

        horizontal_layout_imgs.addLayout(vertical_layout_circle)
        horizontal_layout_imgs.addLayout(vertical_layout_square)

        horizontal_layout_imgs.setSpacing(20)
        horizontal_layout_imgs.addStretch()
        # horizontal_layout_imgs.setAlignment(Qt.AlignmentFlag.AlignLeft)
        horizontal_layout_imgs.setContentsMargins(0, 0, 0, 0)


        # рендер конфигуратора
        # border algo
        choose_algo_box = QHBoxLayout()
        self.label_choose_algo_box = QLabel("Алгоритм вычисления ширины границ")
        self.button_1 = QPushButton('Поиск ближайшей точки в массиве')
        self.button_2 = QPushButton('Увеличение радиуса из точки границы')
        self.button_1.clicked.connect(lambda: self.update_algo('algo1'))
        self.button_2.clicked.connect(lambda: self.update_algo('algo2'))
        choose_algo_box.addWidget(self.label_choose_algo_box, alignment= Qt.AlignmentFlag.AlignLeft)
        choose_algo_box.addWidget(self.button_1, alignment= Qt.AlignmentFlag.AlignCenter)
        choose_algo_box.addWidget(self.button_2, alignment= Qt.AlignmentFlag.AlignRight)
        vertical_layout_config.addLayout(choose_algo_box)

        # bezier curve params
        choose_bezier_box = QHBoxLayout()
        self.label_bezier = QLabel("Выберите расположение точек 2 и 3 кривой  безье\n(для сброса кликнете правой кнопкой мыши)")
        self.bezier_curve_widget = BezierCurveWidget(self, self.pixel_size, self.resist_thickness, self.silicon_thickness)
        choose_bezier_box.addWidget(self.label_bezier, alignment= Qt.AlignmentFlag.AlignLeft)
        
        choose_bezier_box.addWidget(self.bezier_curve_widget, alignment= Qt.AlignmentFlag.AlignTop)
        vertical_layout_config.addLayout(choose_bezier_box)



        # hole width
        hole_width_box = QHBoxLayout()
        self.label_hole_width = QLabel("Ширина дна")
        self.hole_width_input = QLineEdit(str(2*self.radius))
        self.hole_width_input.setFixedWidth(150)
        self.hole_width_input.returnPressed.connect(self.change_hole_width_on_enter_pressed)
        hole_width_box.addWidget(self.label_hole_width, alignment= Qt.AlignmentFlag.AlignLeft)
        hole_width_box.addWidget(self.hole_width_input, alignment= Qt.AlignmentFlag.AlignCenter)
        vertical_layout_config.addLayout(hole_width_box)

        # border width
        border_width_box = QHBoxLayout()
        self.label_border_width = QLabel("Толщина границы")
        self.border_width_slider = QSlider(Qt.Orientation.Horizontal)
        self.border_width_slider.setRange(1, 50)
        self.border_width_slider.setValue(self.border_width)
        self.border_width_slider.setFixedWidth(150)
        self.border_width_slider.setTickPosition(QSlider.TickPosition.TicksAbove)
        self.result_border_label = QLabel(f'Текущее значение: {self.border_width}', self)
        self.border_width_slider.valueChanged.connect(self.update_border_width_slider)
        border_width_box.addWidget(self.label_border_width, alignment= Qt.AlignmentFlag.AlignLeft)
        border_width_box.addWidget(self.border_width_slider, alignment= Qt.AlignmentFlag.AlignCenter)
        border_width_box.addWidget(self.result_border_label, alignment= Qt.AlignmentFlag.AlignRight)
        vertical_layout_config.addLayout(border_width_box)

        # resist thickness
        resist_thickness_box = QHBoxLayout()
        self.label_resist_thickness = QLabel("Толщина слоя резиста (нм)")
        self.resist_thickness_input = QLineEdit(str(self.resist_thickness))
        self.resist_thickness_input.setFixedWidth(150)
        self.resist_thickness_input.returnPressed.connect(self.change_resist_thick_enter_press)
        resist_thickness_box.addWidget(self.label_resist_thickness, alignment= Qt.AlignmentFlag.AlignLeft)
        resist_thickness_box.addWidget(self.resist_thickness_input, alignment= Qt.AlignmentFlag.AlignCenter)
        vertical_layout_config.addLayout(resist_thickness_box)

        # pixel size
        pixel_size_box = QHBoxLayout()
        self.label_pixel_size = QLabel("Размер пикселя (нм)")
        self.pixel_size_input = QLineEdit(str(self.pixel_size))
        self.pixel_size_input.setFixedWidth(150)
        self.pixel_size_input.returnPressed.connect(self.change_pixel_size_enter_press)
        pixel_size_box.addWidget(self.label_pixel_size, alignment= Qt.AlignmentFlag.AlignLeft)
        pixel_size_box.addWidget(self.pixel_size_input, alignment= Qt.AlignmentFlag.AlignCenter)
        vertical_layout_config.addLayout(pixel_size_box)

        
        formula_signal_box = QHBoxLayout()
        self.label_formulas_signal = QLabel("Выберите формулу для расчета сигнала")

        formula1 = r'$(k(\frac{1}{\cos^n(\alpha)} - 1) + 1)color$'
        self.label_formula_signal_k = QLabel()
        self.render_latex(self.label_formula_signal_k,formula1)
        self.button_formula_signal_k = QPushButton('Выбрать')

        formula2 = r'$\frac{E}{\cos^n(\alpha)} + color$'
        self.label_formula_signal_e = QLabel()
        self.render_latex(self.label_formula_signal_e,formula2)
        self.button_formula_signal_e = QPushButton('Выбрать')

        self.button_formula_signal_k.clicked.connect(lambda: self.update_signal_formula('formula_k'))
        self.button_formula_signal_e.clicked.connect(lambda: self.update_signal_formula('formula_e'))

  
        formula_signal_box.addWidget(self.label_formulas_signal)
        formula_signal_box.addWidget(self.label_formula_signal_k)
        formula_signal_box.addWidget(self.button_formula_signal_k)

        formula_signal_box.addWidget(self.label_formula_signal_e)
        formula_signal_box.addWidget(self.button_formula_signal_e)


        vertical_layout_config.addLayout(formula_signal_box)
        
        vals_4angles_box = QHBoxLayout()
        self.label_k_val = QLabel("Значение k ")
        self.k_val_input = QLineEdit(str(self.k_value))
        self.k_val_input.setFixedWidth(150)
        self.k_val_input.returnPressed.connect(self.change_k_value_enter_press)
        vals_4angles_box.addWidget(self.label_k_val)
        vals_4angles_box.addWidget(self.k_val_input)

        self.label_e_val = QLabel("Значение E ")
        self.e_val_input = QLineEdit(str(self.E_value))
        self.e_val_input.setFixedWidth(150)
        self.e_val_input.returnPressed.connect(self.change_e_value_enter_press)
        vals_4angles_box.addWidget(self.label_e_val)
        vals_4angles_box.addWidget(self.e_val_input)

        vertical_layout_config.addLayout(vals_4angles_box)

        horizontal_layout_imgs.addLayout(vertical_layout_config)
        self.layout.addLayout(horizontal_layout_imgs)


    def render_latex(self, label, latex_formula):
        figure = Figure(figsize=(2, 0.4))
        canvas = FigureCanvas(figure)
        figure.text(0.0, 0.4, latex_formula, fontsize=12)

        canvas.draw()
        pixmap = canvas.grab()
        label.setPixmap(pixmap)


    def show_plots_circle(self):
        self.plots_circle_ = Plots(self, self.solv.mask_objects[0], flag_figure='circle')
        self.plots_circle_.show()

    def show_plots_square(self):
        self.plots_square_ = Plots(self, self.solv.mask_objects[1], flag_figure='square')
        self.plots_square_.show()

    def mouseMoveEvent_label1(self, event):
        flag_label=1
        self.prev_cursor_pos = self.cursor_pos
        self.cursor_pos = event.position()

        diff_x = self.cursor_pos.x() - self.prev_cursor_pos.x()
        diff_y = self.cursor_pos.y() - self.prev_cursor_pos.y()
        if abs(diff_x) > abs(diff_y):
            self.flag_render_circle  = 'vertically'
        else:
            self.flag_render_circle = 'horizontally'


        self.label1_slice_y1 = int(self.cursor_pos.y())
        self.label1_slice_x1 = int(self.cursor_pos.x())

        if self.label1_slice_y1 < 0: self.label1_slice_y1 = 0
        if self.label1_slice_y1 >= self.mask_h: self.label1_slice_y1 = self.mask_h-1

        if self.label1_slice_x1 < 0: self.label1_slice_x1 = 0
        if self.label1_slice_x1 >= self.mask_w: self.label1_slice_x1 = self.mask_w-1

        self.update_plots(flag_label=flag_label)
        self.statusBar().showMessage(f'Cursor Position: {self.cursor_pos.x()}, {self.cursor_pos.y()}')


    def mouseMoveEvent_label2(self, event):
        flag_label=2
        self.prev_cursor_pos = self.cursor_pos
        self.cursor_pos = event.position()

        diff_x = self.cursor_pos.x() - self.prev_cursor_pos.x()
        diff_y = self.cursor_pos.y() - self.prev_cursor_pos.y()
        if abs(diff_x) > abs(diff_y):
            self.flag_render_square = 'vertically'
        else:
            self.flag_render_square = 'horizontally'


        self.label2_slice_y1 = int(self.cursor_pos.y())
        self.label2_slice_x1 = int(self.cursor_pos.x())

        if self.label2_slice_y1 < 0: self.label2_slice_y1 = 0
        if self.label2_slice_y1 >= self.mask_h: self.label2_slice_y1 = self.mask_h-1

        if self.label2_slice_x1 < 0: self.label2_slice_x1 = 0
        if self.label2_slice_x1 >= self.mask_w: self.label2_slice_x1 = self.mask_w-1

        self.update_plots(flag_label=flag_label)
        self.statusBar().showMessage(f'Cursor Position: {self.cursor_pos.x()}, {self.cursor_pos.y()}')


    def update_algo(self, value):
        self.algo = value
        self.update_images(flag_draw=False)
        self.update_plots()


    def update_border_width_slider(self, value):
        self.result_border_label.setText(f'Текущее значение: {value}')
        self.border_width = value
        self.update_images()
        self.update_plots()


    def change_resist_thick_enter_press(self):
        text = self.resist_thickness_input.text()
        self.resist_thickness = int(text)
        self.update_images(flag_draw=False)
        self.update_plots()
        self.bezier_curve_widget.resist_thickness = self.resist_thickness
        self.bezier_curve_widget.update()


    def change_pixel_size_enter_press(self):
        text = self.pixel_size_input.text()
        self.pixel_size = int(text)
        self.update_images(flag_draw=False)
        self.update_plots()
        self.bezier_curve_widget.pixel_size = self.pixel_size
        self.bezier_curve_widget.update()


    
    def change_k_value_enter_press(self):
        text = self.k_val_input.text()
        self.k_value = float(text)
        self.update_images(flag_draw=False, flag_recalculate=False)
        self.update_plots()

    
    def change_e_value_enter_press(self):
        text = self.e_val_input.text()
        self.E_value = float(text)
        self.update_images(flag_draw=False, flag_recalculate=False)
        self.update_plots()



    def update_signal_formula(self, value):
        self.signal_formula = value
        self.update_images(flag_draw=False, flag_recalculate=False)
        self.update_plots()




    def change_hole_width_on_enter_pressed(self):
        text = self.hole_width_input.text()
        self.radius = int(text)//2
        self.update_images()
        self.update_plots()


    def check(self):
        for x in self.hole_width_input.text():
            if x < '0' or x > '9':
                print("Invalid Character entered")
                return
            else: print(self.hole_width_input.text())
    

    def update_images(self, flag_draw=True, flag_recalculate=True):
        if flag_draw:
            self.circle_image = self.generate_circle_image()
            self.square_image = self.generate_square_image()
        
        if not flag_recalculate:
            if self.signal_formula == 'formula_k':
                self.solv.signal_formula = self.signal_formula
                self.solv.k = self.k_value
                self.solv.mask_objects[0].signal = self.solv.GetSignal(self.solv.mask_objects[0])
                self.solv.mask_objects[1].signal = self.solv.GetSignal(self.solv.mask_objects[1])
                # self.solv.mask_objects[0].signal = self.solv.GetSignalk(self.solv.mask_objects[0].mask, self.solv.mask_objects[0].angles_map, self.solv.mask_objects[0].color_map).astype(np.uint8)
                # self.solv.mask_objects[1].signal = self.solv.GetSignalk(self.solv.mask_objects[1].mask, self.solv.mask_objects[1].angles_map, self.solv.mask_objects[1].color_map).astype(np.uint8)
            elif self.signal_formula == 'formula_e':
                self.solv.signal_formula = self.signal_formula
                self.solv.E = self.E_value
                self.solv.mask_objects[0].signal = self.solv.GetSignal(self.solv.mask_objects[0])
                self.solv.mask_objects[1].signal = self.solv.GetSignal(self.solv.mask_objects[1])
                # self.solv.mask_objects[0].signal = self.solv.GetSignalE(self.solv.mask_objects[0].mask, self.solv.mask_objects[0].angles_map, self.solv.mask_objects[0].color_map).astype(np.uint8)
                # self.solv.mask_objects[1].signal = self.solv.GetSignalE(self.solv.mask_objects[1].mask, self.solv.mask_objects[1].angles_map, self.solv.mask_objects[1].color_map).astype(np.uint8)
        else:
            QApplication.setOverrideCursor(Qt.CursorShape.BusyCursor)

            self.solv = Solver(algo=self.algo, signal_formula = self.signal_formula, pixel_size=self.pixel_size, \
                      resist_thickness=self.resist_thickness, k=self.k_value, E=self.E_value, masks = [self.circle_image, self.square_image],\
                        recalculate=flag_recalculate, dp2=self.dp2, dp3=self.dp3)
            QApplication.restoreOverrideCursor()

        self.circle_signal = self.solv.mask_objects[0].signal
        self.square_signal = self.solv.mask_objects[1].signal

        self.mask_label_1.setPixmap(self.convert_ndarray_to_pixmap(self.solv.mask_objects[0].signal))
        self.mask_label_2.setPixmap(self.convert_ndarray_to_pixmap(self.solv.mask_objects[1].signal))



    # def update_icons(self):
    #     # Создаем изображение с кругом
    #     self.icon_circle_image = self.generate_circle_image()
    #     # self.icon_label_1.setPixmap(self.convert_ndarray_to_pixmap(circle_image))
    #     # Создаем изображение с квадратом
    #     self.icon_square_image = self.generate_square_image()
    #     # self.icon_label_2.setPixmap(self.convert_ndarray_to_pixmap(circle_image))
    #     self.icon_label_1.setPixmap(self.convert_ndarray_to_pixmap(self.icon_square_image))
    #     # self.create_plot_circle(self.circle_image)


    def update_plots(self, flag_label=0):
        if flag_label!=2:
            self.ax_circle.cla()
        # self.ax_circle.plot(self.circle_image[self.slice_y1, :])
            if self.flag_render_circle=='horizontally':
                self.ax_circle.plot(self.circle_signal[self.label1_slice_y1, :])
                self.ax_circle.set_title(f'Срез по y = {self.label1_slice_y1} круга')
            elif self.flag_render_circle=='vertically':
                self.ax_circle.plot(self.circle_signal[:, self.label1_slice_x1])
                self.ax_circle.set_title(f'Срез по x = {self.label1_slice_x1} круга')
            self.ax_circle.grid()
            self.canvas_circle.draw()

        if flag_label != 1:
            self.ax_square.cla()
            if self.flag_render_square=='horizontally':
                self.ax_square.plot(self.square_signal[self.label2_slice_y1, :])
                self.ax_square.set_title(f'Срез по y = {self.label2_slice_y1} квадрата')
            elif self.flag_render_square=='vertically':
                self.ax_square.plot(self.square_signal[:, self.label2_slice_x1])
                self.ax_square.set_title(f'Срез по x = {self.label2_slice_x1} квадрата')

            self.ax_square.grid()
            self.canvas_square.draw()


    def generate_circle_image(self):
        self.circle_image = 255*np.zeros((self.mask_w, self.mask_h), dtype=np.uint8) # blank image

        center = (self.mask_w//2, self.mask_h//2)

        if self.border_width==1:
            cv2.circle(self.circle_image, center, self.radius, 255, 2)
            cv2.circle(self.circle_image, center, self.radius, 255, -1)
            cont, _ = cv2.findContours(self.circle_image, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
            self.circle_image = 255*np.zeros((self.mask_w, self.mask_h), dtype=np.uint8) # blank image
            cv2.drawContours(self.circle_image, cont, 0, 128, 2)
            cv2.circle(self.circle_image, center, self.radius, 255, 2)
            cv2.circle(self.circle_image, center, self.radius, 255, -1)
        else:
            cv2.circle(self.circle_image, center, self.radius+self.border_width, 128, 2)
            cv2.circle(self.circle_image, center, self.radius+self.border_width, 128, -1)
            cv2.circle(self.circle_image, center, self.radius, 255, 2)
            cv2.circle(self.circle_image, center, self.radius, 255, -1)

        return self.circle_image


    def generate_square_image(self):
        self.square_image = 255*np.zeros((self.mask_w, self.mask_h), dtype=np.uint8) # blank image
        center = (self.mask_w//2, self.mask_h//2)
    
        self.square_image = cv2.rectangle(self.square_image, (center[0] - (self.radius + self.border_width), center[1]-(self.radius + self.border_width)), 
                  (center[0] + (self.radius + self.border_width), center[1]+ (self.radius + self.border_width)), 128, 20) 
        self.square_image = cv2.rectangle(self.square_image, (center[0] - (self.radius + self.border_width), center[1]-(self.radius + self.border_width)), 
                  (center[0] + (self.radius + self.border_width), center[1]+ (self.radius + self.border_width)), 128, -1)

        self.square_image = cv2.rectangle(self.square_image, (center[0] - (self.radius), center[1]-(self.radius)), 
                  (center[0] + (self.radius), center[1]+ (self.radius)), 255, 20) 
        self.square_image = cv2.rectangle(self.square_image, (center[0] - (self.radius), center[1]-(self.radius)), 
                  (center[0] + (self.radius), center[1]+ (self.radius)), 255, -1)

        return self.square_image
    

    def convert_ndarray_to_pixmap(self, image):
        height, width = image.shape
        bytes_per_line = 1 * width
        q_image = QImage(image.data, width, height, bytes_per_line, QImage.Format.Format_Grayscale8)
        pixmap = QPixmap.fromImage(q_image)
        return pixmap

    

if __name__ == '__main__':
    app = QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec())