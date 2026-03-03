from PySide6.QtCore import Qt, QEvent, QPoint, Property, Signal, QEasingCurve
from PySide6.QtWidgets import QWidget, QStackedWidget, QLabel, QVBoxLayout
from PySide6.QtGui import QMouseEvent, QPainter, QTransform
from PySide6.QtCore import QPropertyAnimation

class FlashCard(QWidget):
    known = Signal(bool)

    def __init__(self, deutsch="", englisch="", parent=None):
        super().__init__(parent)
        self._angle = 0.0
        self._offset = 0.0
        self._flipped = False
        self._sliding = False
        self._anim = None
        self._pending_direction = None

        self.setMinimumSize(240, 140)

        self.front = QLabel(deutsch, alignment=Qt.AlignCenter)
        self.back  = QLabel(englisch, alignment=Qt.AlignCenter)
        self.front.setStyleSheet("font-size:18pt; padding:12px; background: white; border-radius:8px;")
        self.back.setStyleSheet("font-size:18pt; padding:12px; background: white; border-radius:8px;")

        self.stack = QStackedWidget(self)
        self.stack.addWidget(self.front)
        self.stack.addWidget(self.back)

        lay = QVBoxLayout(self)
        lay.addWidget(self.stack)
        lay.setContentsMargins(0,0,0,0)

        self.grabGesture(Qt.SwipeGesture)
        self._start_pos = QPoint()

        # anpassbare Dauern (ms)
        self.flip_duration = 200
        self.slide_duration = 300

    def event(self, ev):
        if ev.type() == QEvent.Gesture:
            return self._gestureEvent(ev)
        return super().event(ev)

    def _gestureEvent(self, ev):
        swipe = ev.gesture(Qt.SwipeGesture)
        if swipe and swipe.state() == Qt.GestureFinished:
            self.slide_out(swipe.horizontalDirection() == Qt.Right)
            return True
        return False

    def mousePressEvent(self, ev: QMouseEvent):
        self._start_pos = ev.pos()

    def mouseReleaseEvent(self, ev: QMouseEvent):
        dx = ev.pos().x() - self._start_pos.x()
        if abs(dx) > 40:
            self.slide_out(dx > 0)
        else:
            self.flip()

    def keyPressEvent(self, ev):
        # Pfeiltasten: rechts = kennt, links = kennt nicht
        if ev.key() == Qt.Key_Right:
            self.slide_out(True)
        elif ev.key() == Qt.Key_Left:
            self.slide_out(False)
        elif ev.key() == Qt.Key_Space:
            self.flip()
        else:
            super().keyPressEvent(ev)

    def flip(self):
        if getattr(self, "_flipping", False):
            return
        self._flipping = True
        self._anim = QPropertyAnimation(self, b"angle", duration=self.flip_duration)
        self._anim.setStartValue(0.0)
        self._anim.setEndValue(180.0)
        self._anim.setEasingCurve(QEasingCurve.InOutQuad)
        def on_finished():
            self.stack.setCurrentIndex(1 if self._flipped else 0)
            self._angle = 0.0
            self._flipping = False
            self.update()
        self._anim.finished.connect(on_finished)
        self._flipped = not self._flipped
        self._anim.start()

    def slide_out(self, to_right: bool):
        if self._sliding:
            return
        self._sliding = True
        w = max(1, self.width())
        end = float(int(w * 1.2) * (1 if to_right else -1))
        self._pending_direction = to_right

        # Debug optional: print("slide_out", to_right, "end", end)
        self._anim = QPropertyAnimation(self, b"offset", duration=self.slide_duration)
        self._anim.setStartValue(0.0)
        self._anim.setEndValue(end)
        self._anim.setEasingCurve(QEasingCurve.InCubic)
        def on_finished():
            self._offset = 0.0
            self._sliding = False
            self.update()
            self.known.emit(self._pending_direction)
            self._pending_direction = None
        self._anim.finished.connect(on_finished)
        self._anim.start()

    def paintEvent(self, ev):
        if self._angle != 0.0:
            painter = QPainter(self)
            try:
                w, h = self.width(), self.height()
                t = QTransform()
                t.translate(w/2, h/2)
                t.rotate(self._angle, Qt.YAxis)
                t.translate(-w/2, -h/2)
                painter.setTransform(t)
                # correct signature: render(painter, targetOffset)
                self.stack.render(painter, QPoint(0,0))
            finally:
                painter.end()
        elif self._offset != 0.0:
            painter = QPainter(self)
            try:
                painter.translate(self._offset, 0)
                self.stack.render(painter, QPoint(0,0))
            finally:
                painter.end()
        else:
            super().paintEvent(ev)

    def getAngle(self) -> float:
        return float(self._angle)
    def setAngle(self, a):
        self._angle = float(a)
        self.update()
    angle = Property(float, getAngle, setAngle)

    def getOffset(self) -> float:
        return float(self._offset)
    def setOffset(self, o):
        # optional debug: print("offset", o)
        self._offset = float(o)
        self.update()
    offset = Property(float, getOffset, setOffset)

    def setTexts(self, deutsch, englisch):
        self.front.setText(deutsch)
        self.back.setText(englisch)
        self.stack.setCurrentIndex(0)
        self._flipped = False
        self._offset = 0.0
        self.update()