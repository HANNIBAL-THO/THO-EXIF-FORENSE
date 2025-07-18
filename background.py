import sys
import numpy as np
from PySide6.QtWidgets import QWidget, QApplication
from PySide6.QtGui import QPainter, QColor, QPen, QBrush, QIcon
from PySide6.QtCore import Qt, QTimer, QPointF

class NetworkBackground(QWidget):
    def __init__(self, parent=None, num_points=50, line_threshold=150):
        super().__init__(parent)
        self.num_points = num_points
        self.line_threshold = line_threshold
        self.bg_color = QColor("#000000")
        self.dot_color = QColor("#39FF14")
        self.line_color = QColor("#39FF14")

        self.points = None
        self.velocities = None

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_animation)
        self.timer.start(16) 

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if self.points is None:
            self.initialize_points()

    def initialize_points(self):
        size = self.size()
        self.points = np.random.rand(self.num_points, 2) * np.array([size.width(), size.height()])
        self.velocities = (np.random.rand(self.num_points, 2) - 0.5) * 2

    def update_animation(self):
        if self.points is None: 
            return

        size = self.size()
        width, height = size.width(), size.height()

        self.points += self.velocities

        self.velocities[self.points[:, 0] < 0, 0] *= -1
        self.velocities[self.points[:, 0] > width, 0] *= -1
        self.velocities[self.points[:, 1] < 0, 1] *= -1
        self.velocities[self.points[:, 1] > height, 1] *= -1

        self.points[:, 0] = np.clip(self.points[:, 0], 0, width)
        self.points[:, 1] = np.clip(self.points[:, 1], 0, height)

        self.update()

    def paintEvent(self, event):
        if self.points is None:
            return

        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        painter.fillRect(self.rect(), self.bg_color)

        dist_sq = np.sum((self.points[:, np.newaxis, :] - self.points[np.newaxis, :, :]) ** 2, axis=-1)
        adj_matrix = (dist_sq < self.line_threshold ** 2) & (dist_sq > 0)
        
        pen = QPen(self.line_color)
        for i in range(self.num_points):
            for j in range(i + 1, self.num_points):
                if adj_matrix[i, j]:
                    opacity = 1.0 - np.sqrt(dist_sq[i, j]) / self.line_threshold
                    pen.setColor(QColor(self.line_color.red(), self.line_color.green(), self.line_color.blue(), int(255 * opacity)))
                    painter.setPen(pen)
                    painter.drawLine(QPointF(self.points[i, 0], self.points[i, 1]), 
                                     QPointF(self.points[j, 0], self.points[j, 1]))

        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QBrush(self.dot_color))
        for i in range(self.num_points):
            painter.drawEllipse(QPointF(self.points[i, 0], self.points[i, 1]), 2, 2)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = QWidget()
    window.setGeometry(100, 100, 800, 600)
    
    background = NetworkBackground(window)
    
    from PySide6.QtWidgets import QVBoxLayout
    layout = QVBoxLayout(window)
    layout.setContentsMargins(0, 0, 0, 0)
    layout.addWidget(background)
    window.setLayout(layout)
    
    window.show()
    sys.exit(app.exec())
