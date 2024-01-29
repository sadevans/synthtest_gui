import sys
from PyQt6.QtWidgets import QApplication, QWidget
from PyQt6.QtGui import QPainter, QPen
from PyQt6.QtCore import Qt, QPoint
from run import *


class BezierCurveWidget(QWidget):
    def __init__(self, parent, pixel_size:int, resist_thickness:int, silicon_thickness:int):
        super().__init__()
        self.border_width = 3
        self.max_border_width = 50
        self.pixel_size = pixel_size
        self.resist_thickness = resist_thickness
        self.silicon_thickness = silicon_thickness
        # self.scale_factor = 50/self.border_width
        self.scale_factor = 0.5
        self.parent_=parent
        
        self.setFixedSize(int(max(self.resist_thickness, self.pixel_size*self.max_border_width)*self.scale_factor)+10,int(max(self.resist_thickness, self.pixel_size*self.max_border_width)*self.scale_factor)+10)

        self.initUI()

    def initUI(self):
        self.point1 = QPoint(0, self.silicon_thickness)
        self.point2 = QPoint(self.pixel_size*self.max_border_width, self.silicon_thickness)
        self.point3 = QPoint(0, self.resist_thickness)
        self.point4 = QPoint(self.pixel_size*self.max_border_width, self.resist_thickness)
        

        self.dragging_point = None

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        painter.scale(self.scale_factor, self.scale_factor)

        font = painter.font()
        font.setPointSize(16)
        painter.setFont(font)

        # Draw control points
        painter.setPen(QPen(Qt.GlobalColor.blue, 8, Qt.PenStyle.SolidLine))
        painter.drawPoint(self.point2)
        painter.drawText(self.point2 + QPoint(5, -5), "Точка 2")
        painter.drawPoint(self.point3)
        painter.drawText(self.point3 + QPoint(5, -5), "Точка 3")


        # Draw bezier curve
        painter.setPen(QPen(Qt.GlobalColor.black, 2, Qt.PenStyle.SolidLine))
        t = 0
        while t <= 1:
            x = int((self.point1.x() * (1 - t) ** 3 + self.point2.x() * 3 * t * (1 - t) ** 2 +
                 self.point3.x() * 3 * t ** 2 * (1 - t) + self.point4.x() * t ** 3))
            y = int((self.point1.y() * (1 - t) ** 3 + self.point2.y() * 3 * t * (1 - t) ** 2 +
                 self.point3.y() * 3 * t ** 2 * (1 - t) + self.point4.y() * t ** 3))
            painter.drawPoint(x, y)
            t += 0.001  # step

    def mousePressEvent(self, event):
        scaled_mouse_pos = event.pos() / self.scale_factor
        if (self.point2 - scaled_mouse_pos).manhattanLength() < 10:
            self.dragging_point = 'point2'
        elif (self.point3 - scaled_mouse_pos).manhattanLength() < 10:
            self.dragging_point = 'point3'

        if event.button() == Qt.MouseButton.RightButton:
            self.point2 = QPoint(self.pixel_size*self.max_border_width, 100)
            self.point3 = QPoint(0, 700)
            self.update()



    def mouseMoveEvent(self, event):
        if self.dragging_point == 'point2':
            scaled_mouse_pos = event.pos() / self.scale_factor
            self.point2 = scaled_mouse_pos
            self.update()


        elif self.dragging_point == 'point3':
            scaled_mouse_pos = event.pos() / self.scale_factor
            self.point3 = scaled_mouse_pos
            self.update()

    def mouseReleaseEvent(self, event):
        self.dragging_point = None

        p3_change_x = self.point3.x()/(self.pixel_size*self.max_border_width)
        p3_change_y = (self.point3.y() - 100)/(self.resist_thickness - 100)
        self.parent_.dp3 = (p3_change_x, p3_change_y)

        p2_change_x = self.point2.x()/(self.pixel_size*self.max_border_width)
        p2_change_y = (self.point2.y() - 100)/(self.resist_thickness - 100)
        self.parent_.dp2 = (p2_change_x, p2_change_y)
        self.parent_.update_images()
        self.parent_.update_plots()



def main():
    app = QApplication(sys.argv)
    window = BezierCurveWidget(3, 12)
    window.show()
    sys.exit(app.exec())


if __name__ == '__main__':
    main()