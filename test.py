import sys
import cv2
import numpy as np
import matplotlib
matplotlib.use('QtAgg')

import matplotlib.pyplot as plt
from matplotlib.widgets import Cursor
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas, NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure


from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QApplication, QMainWindow, QLabel, QVBoxLayout, QHBoxLayout, QWidget, QPushButton, QLineEdit
from PyQt6.QtGui import QPixmap, QImage, QPainter, QPen
from PyQt6.QtCore import Qt, QTimer
    


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.radius = 50


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

        canvas_circle = self.create_plot_circle() # create canvas
        vertical_layout_circle.addWidget(canvas_circle) 
        toolbar_circle = NavigationToolbar(canvas_circle, self)
        vertical_layout_circle.addWidget(toolbar_circle) 

        canvas_square = self.create_plot_square() # create canvas
        vertical_layout_square.addWidget(canvas_square) 
        toolbar_square = NavigationToolbar(canvas_square, self)
        vertical_layout_square.addWidget(toolbar_square, )
        # vertical_layout_square.setAlignment(Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignVCenter)




        horizontal_layout_imgs.addLayout(vertical_layout_circle)
        horizontal_layout_imgs.addLayout(vertical_layout_square)

        horizontal_layout_imgs.setSpacing(0)
        horizontal_layout_imgs.addStretch()
        # horizontal_layout_imgs.setAlignment(Qt.AlignmentFlag.AlignLeft)
        horizontal_layout_imgs.setContentsMargins(0, 0, 0, 0)





        # self.layout.addLayout(horizontal_layout_imgs)


        # рендер конфигуратора
        # vertical_layout_config
        hole_width = QHBoxLayout()
        self.label_hole_width = QLabel("Ширина дна")
        self.hole_width_input = QLineEdit(str(self.radius))
        self.hole_width_input.setFixedWidth(150)

        self.hole_width_input.returnPressed.connect(self.on_enter_pressed)

        # self.hole_width_input.textChanged.connect(self.check)

        hole_width.addWidget(self.label_hole_width, alignment= Qt.AlignmentFlag.AlignCenter)

        hole_width.addWidget(self.hole_width_input, alignment= Qt.AlignmentFlag.AlignCenter)

        vertical_layout_config.addLayout(hole_width)

        horizontal_layout_imgs.addLayout(vertical_layout_config)
        self.layout.addLayout(horizontal_layout_imgs)


    def on_enter_pressed(self):
        text = self.hole_width_input.text()
        # print("Text from QLineEdit:", text)

        self.radius = int(text)
        self.update_images()


    def check(self):
        for x in self.hole_width_input.text():
            if x < '0' or x > '9':
                print("Invalid Character entered")
                return
            else: print(self.hole_width_input.text())
                

    def mouse_callback(self, event):
        if event.buttons() == Qt.MouseButton.LeftButton:
            print("Clicked Position: x =", event.pos().x(), ", y =", event.pos().y())



    def mouse_press_event(self, event):
        print('press !')
        # self.start_point = event.pos()

    def mouse_move_event(self, event):
        print('move !')

        # if hasattr(self, 'start_point'):
        #     end_point = event.pos()
        #     pixmap = self.image_label_1.pixmap()
        #     painter = QPainter(pixmap)
        #     pen = QPen(Qt.GlobalColor.red)
        #     pen.setWidth(2)
        #     painter.setPen(pen)
        #     painter.drawLine(self.start_point, end_point)
        #     self.image_label_1.setPixmap(pixmap)

    def mouse_release_event(self, event):
        print('update')
        # self.update_plot_circle()


    def create_plot_circle(self):
        fig = Figure(figsize=(1,1), dpi=100)
        ax = fig.add_subplot(111)
        ax.cla()

        ax.plot(self.circle_image[150,:])
        ax.grid()
        ax.set_title('Срез по центру круга')


        cursor = Cursor(ax, horizOn = True, vertOn=True, color='red', linewidth=1, 
                useblit=True)
        # Creating an annotating box
        annot = ax.annotate("", xy=(0,0), xytext=(-40,40),textcoords="offset points",
                            bbox=dict(boxstyle='round4', fc='linen',ec='k',lw=1),
                            arrowprops=dict(arrowstyle='->'))
        annot.set_visible(False)
        coord = []

        def onclick(event):
            # global coord
            coord = []
            coord.append((event.xdata, event.ydata))
            x = event.xdata
            y = event.ydata
            
            # printing the values of the selected point
            print([x,y]) 
            annot.xy = (x,y)
            text = "({:.2f}, {:.2f})".format(x,y)
            annot.set_text(text)
            annot.set_visible(True)
            fig.canvas.draw() #redraw the figure


        fig.canvas.mpl_connect('button_press_event', onclick)
        # x1, y1 = zip(*coord)
        # print(x1, y1)
        canvas_ = FigureCanvas(fig)
        # canvas.toolbar.setVisible(True)
        return canvas_
    
    
    
    def create_plot_square(self):
        fig = Figure(figsize=(1,1), dpi=100)
        ax = fig.add_subplot(111)
        ax.cla()
        ax.plot(self.square_image[150,:])
        ax.grid()
        ax.set_title('Срез по центру квадрата')

        cursor = Cursor(ax, horizOn=True, vertOn=True, useblit=True,
                color = 'r', linewidth = 1)
        # Creating an annotating box
        annot = ax.annotate("", xy=(0,0), xytext=(-40,40),textcoords="offset points",
                            bbox=dict(boxstyle='round4', fc='linen',ec='k',lw=1),
                            arrowprops=dict(arrowstyle='-|>'))
        annot.set_visible(False)

        canvas = FigureCanvas(fig)
        # canvas.toolbar.setVisible(True)

        return canvas
    

    def update_images(self):
        # Создаем изображение с кругом
        circle_image = self.generate_circle_image()
        self.mask_label_1.setPixmap(self.convert_ndarray_to_pixmap(circle_image))

        # Создаем изображение с квадратом
        square_image = self.generate_square_image()
        self.mask_label_2.setPixmap(self.convert_ndarray_to_pixmap(square_image))

        # self.update_plot_circle()
        # self.update_plot_square()



    # def update_plot_circle(self):
    #     # Get the existing canvas from the layout
    #     canvas_circle = self.layout.itemAt(0).itemAt(0).itemAt(0).widget() if self.layout.count() > 0 else None
    #     # canvas_circle = self.layout.itemAt(0).itemAt(0).itemAt(0).widget()
    #     self.clear_plot(canvas_circle)
    #     self.create_plot_circle(canvas_circle)

    # def update_plot_square(self):
    #     canvas_square = self.layout.itemAt(0).itemAt(1).itemAt(0).widget()
    #     self.clear_plot(canvas_square)
    #     self.create_plot_square(canvas_square)

    # def clear_plot(self, canvas):
    #     canvas.figure.clf()
    #     canvas.draw()


    # def generate_images(self):
    #     self.circle_image = 255*np.zeros((300, 300), dtype=np.uint8) # blank image
    #     self.square_image = 255*np.zeros((300, 300), dtype=np.uint8) # blank image
    #     center = (150, 150)

    #     cv2.circle(self.circle_image, center, self.radius, 255, 2)
    #     cv2.circle(self.circle_image, center, self.radius, 255, -1)

    #     self.square_image = cv2.rectangle(self.square_image, (center[0] - (self.radius), center[1]-(self.radius)), 
    #               (center[0] + (self.radius), center[1]+ (self.radius)), 255, 20) 
    #     self.square_image = cv2.rectangle(self.square_image, (center[0] - (self.radius), center[1]-(self.radius)), 
    #               (center[0] + (self.radius), center[1]+ (self.radius)), 255, -1)
        
    #     return self.circle_image, self.square_image
        


    def generate_circle_image(self):
        self.circle_image = 255*np.zeros((300, 300), dtype=np.uint8) # blank image

        center = (150, 150)
        # radius = 50

        cv2.circle(self.circle_image, center, self.radius, 255, 2)
        cv2.circle(self.circle_image, center, self.radius, 255, -1)


        # image = 255 * (cv2.circle(np.zeros((100, 100), dtype=np.uint8), (50, 50), 30, (255, 255, 255), -1) > 0)
        return self.circle_image

    def generate_square_image(self):
        self.square_image = 255*np.zeros((300, 300), dtype=np.uint8) # blank image
        center = (150, 150)
        # radius = 50

        self.square_image = cv2.rectangle(self.square_image, (center[0] - (self.radius), center[1]-(self.radius)), 
                  (center[0] + (self.radius), center[1]+ (self.radius)), 255, 20) 
        self.square_image = cv2.rectangle(self.square_image, (center[0] - (self.radius), center[1]-(self.radius)), 
                  (center[0] + (self.radius), center[1]+ (self.radius)), 255, -1)

        # image = 255 * (cv2.rectangle(np.zeros((100, 100), dtype=np.uint8), (20, 20), (80, 80), (255, 255, 255), -1) > 0)
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