import numpy as np
import matplotlib
matplotlib.use('QtAgg')
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas, NavigationToolbar2QT as NavigationToolbar
from PyQt6.QtWidgets import QMainWindow, QVBoxLayout, QWidget


class Plots(QMainWindow):
    def __init__(self, parent, img_object, flag_figure):
        super().__init__()
        self.parent_ = parent
        self.img_object = img_object
        self.flag_figure = flag_figure
        self.init_UI()

    def init_UI(self):
        if self.flag_figure=='circle': self.setWindowTitle("Графики для круга")
        elif self.flag_figure=='square': self.setWindowTitle("Графики для квадрата")

        self.setGeometry(100, 100, 600, 600)  # Устанавливаем размеры окна на весь экран

        self.central_widget = QWidget(self)
        self.setCentralWidget(self.central_widget)

        self.layout = QVBoxLayout(self.central_widget)
        self.figure, self.ax = plt.subplots(2, 3, figsize=(100, 100), dpi=100)
        self.canvas = FigureCanvas(self.figure)
        self.toolbar = NavigationToolbar(self.canvas, self)

        self.layout.addWidget(self.canvas)
        self.layout.addWidget(self.toolbar)

        # toolbar_square = NavigationToolbar(self.canvas_square, self)
        self.render_plots()
        # vertical_layout_square.addWidget(toolbar_square) 
    

    def render_plots(self):
        self.ax[0,0].cla()
        self.ax[0,1].cla()
        self.ax[0,2].cla()

        self.ax[1,0].cla()
        self.ax[1,1].cla()
        self.ax[1,2].cla()

        self.ax[0,0].imshow(self.img_object.width_map)
        self.ax[0,0].set_title('Визуализация значений ширины границы')
        self.ax[1,0].plot(self.img_object.width_map[200,:])
        self.ax[1,0].grid()


        self.ax[0,1].imshow(self.img_object.angles_map)
        self.ax[0,1].set_title('Визуализация значений углов')
        self.ax[1,1].plot(self.img_object.angles_map[200,:])
        self.ax[1,1].grid()

        self.ax[0,2].imshow(self.img_object.color_map)
        self.ax[0,2].set_title('Визуализация значений цветов')
        self.ax[1,2].plot(self.img_object.color_map[200,:])
        self.ax[1,2].grid()

        self.canvas.draw()