import sys
import cv2
import numpy as np
import matplotlib
matplotlib.use('QtAgg')

import matplotlib.pyplot as plt
# from matplotlib.widgets import Cursor
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas, NavigationToolbar2QT as NavigationToolbar
# from matplotlib.figure import Figure

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QApplication, QMainWindow, QLabel, QVBoxLayout, QHBoxLayout, QWidget, QPushButton, QLineEdit, QSlider
from PyQt6.QtGui import QPixmap, QImage
from PyQt6.QtCore import Qt

from src.Solver import *
    

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.mask_w = 400
        self.mask_h = 400
        self.slice_y1 = 200

        self.radius = 50
        self.border_width = 10

        self.resist_thickness = 700
        self.silicon_thickness = 100
        self.pixel_size = 12
        self.transform_algo = 'bezier'
        self.algo = 'algo1'

        # self.ax = None


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
        vertical_layout_circle.addWidget(self.mask_label_1)
        vertical_layout_circle.setAlignment(self.mask_label_1, Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignVCenter)

        self.mask_label_2 = QLabel(self)
        vertical_layout_square.addWidget(self.mask_label_2)
        vertical_layout_square.setAlignment(self.mask_label_2, Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignVCenter)



        self.update_images()

        # self.solv = Solver(algo=self.algo, transform_algo = self.transform_algo, pixel_size=self.pixel_size, \
                    #   resist_thickness=self.resist_thickness, masks = [self.circle_image, self.square_image])

        # self.icon_label_1 = QLabel()
        # self.icon_label_1.mousePressEvent = self.on_icon_click
        # vertical_layout_circle.addWidget(self.icon_label_1)

        # self.update_icons()



        # self.mask_label_1 = QLabel(self)
        # vertical_layout_circle.addWidget(self.mask_label_1)
        # vertical_layout_circle.setAlignment(self.mask_label_1, Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignVCenter)

        # self.mask_label_2 = QLabel(self)
        # vertical_layout_square.addWidget(self.mask_label_2)
        # vertical_layout_square.setAlignment(self.mask_label_2, Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignVCenter)



        # self.update_images()

        # self.image_label_1.setCursor(Qt.CursorShape.CrossCursor)
        # self.image_label_1.mousePressEvent = self.mouse_callback

        # self.image_label_2.setCursor(Qt.CursorShape.CrossCursor)
        # self.image_label_2.mousePressEvent = self.mouse_callback


        # self.image_label_1.mousePressEvent = self.mouse_press_event
        # self.image_label_1.mouseMoveEvent = self.mouse_move_event
        # self.image_label_1.mouseReleaseEvent = self.mouse_release_event

        # self.image_label_2.mousePressEvent = self.mouse_press_event
        # self.image_label_2.mouseMoveEvent = self.mouse_move_event
        # self.image_label_2.mouseReleaseEvent = self.mouse_release_event


        # self.image_label_1 = QLabel(self)
        # vertical_layout_circle.addWidget(self.image_label_1)
        # vertical_layout_circle.setAlignment(self.image_label_1, Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignVCenter)

        # self.image_label_2 = QLabel(self)
        # vertical_layout_square.addWidget(self.image_label_2)
        # vertical_layout_square.setAlignment(self.image_label_2, Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignVCenter)


        # self.update_images()
        # self.canvas_circle = FigureCanvas(plt.Figure(figsize=(1,1), dpi=100))

        # self.insert_ax()
        # self.update_plots

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


        # canvas_circle = self.create_plot_circle() # create canvas
        # vertical_layout_circle.addWidget(canvas_circle) 
        
        # toolbar_circle = NavigationToolbar(canvas_circle, self)
        # vertical_layout_circle.addWidget(toolbar_circle) 

        # canvas_square = self.create_plot_square() # create canvas
        # vertical_layout_square.addWidget(canvas_square) 
        # toolbar_square = NavigationToolbar(canvas_square, self)
        # vertical_layout_square.addWidget(toolbar_square, )
        # vertical_layout_square.setAlignment(Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignVCenter)

        horizontal_layout_imgs.addLayout(vertical_layout_circle)
        horizontal_layout_imgs.addLayout(vertical_layout_square)

        horizontal_layout_imgs.setSpacing(20)
        horizontal_layout_imgs.addStretch()
        # horizontal_layout_imgs.setAlignment(Qt.AlignmentFlag.AlignLeft)
        horizontal_layout_imgs.setContentsMargins(0, 0, 0, 0)


        # рендер конфигуратора
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


        # transform angle algo
        # choose_transform_algo_box = QHBoxLayout()
        # self.label_choose_transform_algo_box = QLabel("Алгоритм преобразования углов")
        # self.button_transform_bezier = QPushButton('Безье')
        # self.button_transform_parabola = QPushButton('Парабола')
        # self.button_transform_bezier.clicked.connect(lambda: self.update_algo_transform('bezier'))
        # self.button_transform_parabola.clicked.connect(lambda: self.update_algo_transform('parabola'))
        # choose_transform_algo_box.addWidget(self.label_choose_transform_algo_box, alignment= Qt.AlignmentFlag.AlignLeft)
        # choose_transform_algo_box.addWidget(self.button_transform_bezier, alignment= Qt.AlignmentFlag.AlignCenter)
        # choose_transform_algo_box.addWidget(self.button_transform_parabola, alignment= Qt.AlignmentFlag.AlignRight)
        # vertical_layout_config.addLayout(choose_transform_algo_box)


        horizontal_layout_imgs.addLayout(vertical_layout_config)
        self.layout.addLayout(horizontal_layout_imgs)


    # def on_icon_click(self, event):
        # tmp = self.mask_label_1
        # self.mask_label_1 = self.icon_label_1
        # self.icon_label_1 = tmp
        # self.mask_label_1.setPixmap(self.convert_ndarray_to_pixmap(self.icon_square_image))
        # self.icon_label_1.setPixmap(self.convert_ndarray_to_pixmap(self.circle_image))

        # tmp = self.icon_square_image
        # ttmp = self.circle_image


    def update_algo(self, value):
        self.border_width_algo = value


    def update_algo_transform(self, value):
        self.transform_algo = value


    def update_border_width_slider(self, value):
        self.result_border_label.setText(f'Текущее значение: {value}')
        self.border_width = value
        self.update_images()
        self.update_plots()



    def change_resist_thick_enter_press(self):
        text = self.resist_thickness_input.text()
        self.resist_thickness = int(text)
        self.update_images()
        self.update_plots()


    def change_pixel_size_enter_press(self):
        text = self.pixel_size_input.text()
        self.pixel_size = int(text)
        self.update_images()
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
    

    def update_images(self):
        self.circle_image = self.generate_circle_image()
        self.square_image = self.generate_square_image()

        solv = Solver(algo=self.algo, transform_algo = self.transform_algo, pixel_size=self.pixel_size, \
                      resist_thickness=self.resist_thickness, masks = [self.circle_image, self.square_image])
        # print(len(solv.mask_objects))
        self.circle_signal = solv.mask_objects[0].signal
        self.square_signal = solv.mask_objects[1].signal

        self.mask_label_1.setPixmap(self.convert_ndarray_to_pixmap(self.circle_signal))
        self.mask_label_2.setPixmap(self.convert_ndarray_to_pixmap(self.square_signal))



        # self.mask_label_1.setPixmap(self.convert_ndarray_to_pixmap(circle_image))

        # square_image = self.generate_square_image()
        # self.mask_label_2.setPixmap(self.convert_ndarray_to_pixmap(square_image))


    # def update_icons(self):
    #     # Создаем изображение с кругом
    #     self.icon_circle_image = self.generate_circle_image()
    #     # self.icon_label_1.setPixmap(self.convert_ndarray_to_pixmap(circle_image))
    #     # Создаем изображение с квадратом
    #     self.icon_square_image = self.generate_square_image()
    #     # self.icon_label_2.setPixmap(self.convert_ndarray_to_pixmap(circle_image))
    #     self.icon_label_1.setPixmap(self.convert_ndarray_to_pixmap(self.icon_square_image))
    #     # self.create_plot_circle(self.circle_image)


    def update_plots(self):
        self.ax_circle.cla()
        # self.ax_circle.plot(self.circle_image[self.slice_y1, :])
        self.ax_circle.plot(self.circle_signal[self.slice_y1, :])

        self.ax_circle.grid()
        self.ax_circle.set_title('Срез по центру круга')
        self.canvas_circle.draw()

        self.ax_square.cla()
        # self.ax_square.plot(self.square_image[self.slice_y1, :])
        self.ax_square.plot(self.square_signal[self.slice_y1, :])

        self.ax_square.grid()
        self.ax_square.set_title('Срез по центру квадрата')
        self.canvas_square.draw()


    def generate_circle_image(self):
        self.circle_image = 255*np.zeros((self.mask_w, self.mask_h), dtype=np.uint8) # blank image

        center = (self.mask_w//2, self.mask_h//2)
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