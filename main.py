# main.py
# KAISEL — The Haunted Terminal (Always-On Spirit, Violet / Dark Blue Theme)
# Requirements: PyQt5
# Optional: ollama (local model), psutil (real CPU/mem)
#
# Usage:
#   pip install PyQt5
#   pip install psutil   # optional for real stats
#   pip install ollama   # optional for local model responses
#   python main.py

import sys
import threading
import time
import random
import math

from PyQt5 import QtCore, QtGui, QtWidgets

# optional imports
try:
    import ollama
except Exception:
    ollama = None

try:
    import psutil
except Exception:
    psutil = None

APP_TITLE = "KAISEL — The Haunted Terminal (Violet Spirit)"

# -----------------------
# Particle overlay widget (violet / blue particles)
# -----------------------
class Particle:
    def __init__(self, w, h):
        self.reset(w, h)

    def reset(self, w, h):
        self.x = random.uniform(0, w)
        self.y = random.uniform(0, h)
        speed = random.uniform(0.12, 0.9)
        angle = random.uniform(-math.pi/3, math.pi/3) - math.pi/2  # mostly upwards
        self.vx = math.cos(angle) * speed
        self.vy = math.sin(angle) * speed
        self.size = random.uniform(1.5, 6.0)
        self.alpha = random.uniform(0.06, 0.36)
        self.life = random.uniform(4.0, 12.0)  # seconds
        self.age = random.uniform(0, self.life)

    def step(self, dt, w, h):
        self.x += self.vx * dt * 60
        self.y += self.vy * dt * 60
        self.age += dt
        if self.age >= self.life or self.x < -10 or self.x > w+10 or self.y < -10 or self.y > h+10:
            self.reset(w, h)

class ParticleOverlay(QtWidgets.QWidget):
    def __init__(self, parent=None, count=90):
        super().__init__(parent)
        self.setAttribute(QtCore.Qt.WA_TransparentForMouseEvents)
        self.setAttribute(QtCore.Qt.WA_NoSystemBackground)
        self.particles = []
        self.last = time.time()
        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.on_tick)
        self.timer.start(16)  # ~60fps repaint
        self.count = count
        self._init_particles()

    def _init_particles(self):
        self.particles = [Particle(self.width() or 800, self.height() or 400) for _ in range(self.count)]

    def resizeEvent(self, e):
        for p in self.particles:
            p.reset(self.width(), self.height())
        super().resizeEvent(e)

    def on_tick(self):
        now = time.time()
        dt = max(0.0001, now - self.last)
        w, h = max(1, self.width()), max(1, self.height())
        for p in self.particles:
            p.step(dt, w, h)
        self.last = now
        self.update()

    def paintEvent(self, e):
        painter = QtGui.QPainter(self)
        painter.setRenderHint(QtGui.QPainter.Antialiasing)
        w, h = self.width(), self.height()
        for p in self.particles:
            grad = QtGui.QRadialGradient(QtCore.QPointF(p.x, p.y), p.size*6)
            # violet-to-deep-blue particle colors
            c1 = QtGui.QColor(140, 100, 255, int(p.alpha*255))  # violet
            c2 = QtGui.QColor(20, 30, 70, 0)                     # transparent deep-blue
            grad.setColorAt(0.0, c1)
            grad.setColorAt(1.0, c2)
            brush = QtGui.QBrush(grad)
            painter.setBrush(brush)
            painter.setPen(QtCore.Qt.NoPen)
            painter.drawEllipse(QtCore.QPointF(p.x, p.y), p.size*3, p.size*3)
        painter.end()

# -----------------------
# Sweep overlay (violet light sweep + vignette)
# -----------------------
class SweepOverlay(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAttribute(QtCore.Qt.WA_TransparentForMouseEvents)
        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.update)
        self.timer.start(25)
        self.phase = 0.0

    def paintEvent(self, e):
        painter = QtGui.QPainter(self)
        painter.setRenderHint(QtGui.QPainter.SmoothPixmapTransform)
        w, h = self.width(), self.height()

        # vignette (subtle darkening)
        grad = QtGui.QRadialGradient(w/2, h/2, max(w,h)*0.8)
        grad.setColorAt(0.0, QtGui.QColor(0, 0, 0, 0))
        grad.setColorAt(1.0, QtGui.QColor(0, 0, 24, 120))
        painter.fillRect(0,0,w,h, QtGui.QBrush(grad))

        # moving violet-blue sweep
        self.phase += 0.01
        sweep_x = (math.sin(self.phase)*0.5 + 0.5) * w
        sweep_rect = QtCore.QRectF(sweep_x - w*0.18, 0, w*0.36, h)
        grad2 = QtGui.QLinearGradient(sweep_rect.topLeft(), sweep_rect.topRight())
        grad2.setColorAt(0.0, QtGui.QColor(200,160,255,8))
        grad2.setColorAt(0.5, QtGui.QColor(120,100,255,36))
        grad2.setColorAt(1.0, QtGui.QColor(200,160,255,8))
        painter.setCompositionMode(QtGui.QPainter.CompositionMode_Plus)
        painter.fillRect(sweep_rect, QtGui.QBrush(grad2))
        painter.end()

# -----------------------
# Sidebar (violet/dark-blue theme)
# -----------------------
class Sidebar(QtWidgets.QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedWidth(220)
        self.setObjectName("sidebar")
        self.layout = QtWidgets.QVBoxLayout(self)
        self.layout.setContentsMargins(10,10,10,10)
        self.layout.setSpacing(8)
        self.add_tiles()
        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.update_stats)
        self.timer.start(1200)
        self.update_stats()

    def add_tiles(self):
        self.title = QtWidgets.QLabel("SYSTEM")
        self.title.setAlignment(QtCore.Qt.AlignCenter)
        self.title.setStyleSheet("font-weight:700; color: #e9e7ff;")
        self.layout.addWidget(self.title)
        self.cpu_label = QtWidgets.QLabel("CPU: --%")
        self.mem_label = QtWidgets.QLabel("RAM: --%")
        self.net_label = QtWidgets.QLabel("NET: -- kb/s")
        for lbl in (self.cpu_label, self.mem_label, self.net_label):
            lbl.setStyleSheet(
                "background: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:1, stop:0 rgba(18,14,40,180), stop:1 rgba(28,20,60,170)); "
                "padding:10px; border-radius:8px; color:#dfe8ff;"
            )
            self.layout.addWidget(lbl)
        self.layout.addStretch(1)

    def update_stats(self):
        if psutil:
            cpu = psutil.cpu_percent(interval=None)
            mem = psutil.virtual_memory().percent
            net = psutil.net_io_counters()
            sent = net.bytes_sent // 1024
            recv = net.bytes_recv // 1024
            self.net_label.setText(f"NET: {sent}k / {recv}k")
            self.cpu_label.setText(f"CPU: {int(cpu)}%")
            self.mem_label.setText(f"RAM: {int(mem)}%")
        else:
            t = int(time.time())
            self.cpu_label.setText(f"CPU: {30 + (t%40)}%")
            self.mem_label.setText(f"RAM: {48 + (t%30)}%")
            self.net_label.setText(f"NET: {(t%120)} kb/s")

# -----------------------
# Main window (Spirit always on, no voice)
# -----------------------
class NeonTerminal(QtWidgets.QMainWindow):
    output_signal = QtCore.pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.setWindowTitle(APP_TITLE)
        self.setMinimumSize(1100, 640)
        self.output_signal.connect(self.write_output)

        # Build layout: main area + right sidebar
        central = QtWidgets.QWidget()
        self.setCentralWidget(central)
        main_h = QtWidgets.QHBoxLayout(central)
        main_h.setContentsMargins(8,8,8,8)
        main_h.setSpacing(10)

        # Left main column
        left_col = QtWidgets.QVBoxLayout()
        left_col.setSpacing(8)
        main_h.addLayout(left_col, 1)

        # header
        self.header = QtWidgets.QLabel("K A I S E L")
        self.header.setAlignment(QtCore.Qt.AlignCenter)
        header_font = QtGui.QFont("Consolas", 34, QtGui.QFont.Bold)
        self.header.setFont(header_font)
        self.header.setStyleSheet("color: #dcd6ff; letter-spacing:8px;")
        left_col.addWidget(self.header)

        # terminal frame
        self.terminal_frame = QtWidgets.QFrame()
        self.terminal_frame.setStyleSheet("background: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:1, stop:0 #040418, stop:1 #07102a); border-radius: 8px; padding:6px;")
        t_layout = QtWidgets.QVBoxLayout(self.terminal_frame)
        t_layout.setContentsMargins(6,6,6,6)
        self.output = QtWidgets.QTextEdit(readOnly=True)
        self.output.setStyleSheet("background: transparent; border: none; color: #cfe9ff;")
        self.output.setFontPointSize(11)
        t_layout.addWidget(self.output)
        left_col.addWidget(self.terminal_frame, 1)

        # input row
        row = QtWidgets.QHBoxLayout()
        self.input_line = QtWidgets.QLineEdit()
        self.input_line.setPlaceholderText("Ask KAISEL... or type 'help'")
        self.input_line.returnPressed.connect(self.on_send_clicked)
        self.apply_input_style()
        row.addWidget(self.input_line, 1)

        send_btn = QtWidgets.QPushButton("Send")
        send_btn.clicked.connect(self.on_send_clicked)
        row.addWidget(send_btn)

        # no toggles (spirit always on, voice removed)
        left_col.addLayout(row)

        # footer status
        self.status = QtWidgets.QLabel("Spirit Mode: active")
        self.status.setStyleSheet("color: rgba(200,190,255,0.85);")
        left_col.addWidget(self.status)

        # right sidebar
        self.sidebar = Sidebar()
        main_h.addWidget(self.sidebar)

        # overlays: particle & sweep
        self.particles = ParticleOverlay(self.terminal_frame, count=100)
        self.particles.setGeometry(self.terminal_frame.rect())
        self.particles.show()

        self.sweep = SweepOverlay(self.terminal_frame)
        self.sweep.setGeometry(self.terminal_frame.rect())
        self.sweep.show()

        # keep overlays resized with frame
        self.terminal_frame.installEventFilter(self)

        # header opacity & scale animations (always on)
        self.header_opacity = QtWidgets.QGraphicsOpacityEffect(self.header)
        self.header.setGraphicsEffect(self.header_opacity)
        self.header_anim = QtCore.QPropertyAnimation(self.header_opacity, b"opacity", self)
        self.header_anim.setDuration(1400)
        self.header_anim.setStartValue(0.6)
        self.header_anim.setKeyValueAt(0.5, 1.0)
        self.header_anim.setEndValue(0.6)
        self.header_anim.setLoopCount(-1)

        self.header_scale_anim = QtCore.QPropertyAnimation(self.header, b"geometry", self)
        self.header_base_geom = None
        QtCore.QTimer.singleShot(80, self.capture_header_geom)

        # start spirit visuals automatically
        QtCore.QTimer.singleShot(220, self._start_spirit_visuals)

        # caret blink
        self.caret_timer = QtCore.QTimer(self)
        self.caret_timer.timeout.connect(self._blink_input)
        self._caret_visible = True
        self.caret_timer.start(500)

        # initial text
        self.output_signal.emit("[KAISEL] — Spirit Mode engaged. Violet currents flow.")

    def capture_header_geom(self):
        self.header_base_geom = self.header.geometry()
        g = self.header_base_geom
        scaled = g.adjusted(-8, -4, 8, 4)
        self.header_scale_anim.setStartValue(g)
        self.header_scale_anim.setKeyValueAt(0.5, scaled)
        self.header_scale_anim.setEndValue(g)
        self.header_scale_anim.setDuration(1400)
        self.header_scale_anim.setLoopCount(-1)

    def _start_spirit_visuals(self):
        # start animations
        try:
            self.header_anim.start()
            if self.header_base_geom:
                self.header_scale_anim.start()
        except Exception:
            pass
        # subtle terminal glow animation using QGraphicsColorizeEffect
        self.terminal_colorize = QtWidgets.QGraphicsColorizeEffect(self.terminal_frame)
        self.terminal_colorize.setColor(QtGui.QColor(120, 80, 255))
        self.terminal_colorize.setStrength(0.0)
        self.terminal_frame.setGraphicsEffect(self.terminal_colorize)
        self.terminal_glow = QtCore.QPropertyAnimation(self.terminal_colorize, b"strength", self)
        self.terminal_glow.setDuration(1500)
        self.terminal_glow.setStartValue(0.0)
        self.terminal_glow.setKeyValueAt(0.5, 0.32)
        self.terminal_glow.setEndValue(0.0)
        self.terminal_glow.setLoopCount(-1)
        self.terminal_glow.start()

    def eventFilter(self, obj, event):
        if obj is self.terminal_frame and event.type() == QtCore.QEvent.Resize:
            r = self.terminal_frame.rect()
            self.particles.setGeometry(r)
            self.sweep.setGeometry(r)
        return super().eventFilter(obj, event)

    def apply_input_style(self):
        style = """
        QLineEdit {
            background: rgba(10,12,20,0.9);
            color: #e6e9ff;
            border: 1px solid rgba(120,80,220,0.08);
            padding: 8px;
            border-radius: 6px;
        }
        QLineEdit:focus {
            border: 1px solid rgba(120,100,255,0.35);
            box-shadow: 0 0 24px rgba(110,80,255,0.06);
        }
        """
        self.input_line.setStyleSheet(style)

    def _blink_input(self):
        if self.input_line.hasFocus():
            self._caret_visible = not self._caret_visible
            if self._caret_visible:
                self.input_line.setCursorPosition(len(self.input_line.text()))
        else:
            self._caret_visible = True

    # -------------------------
    # core messaging (no voice)
    # -------------------------
    def write_output(self, text: str):
        self.output.append(text)
        self.output.verticalScrollBar().setValue(self.output.verticalScrollBar().maximum())

    def on_send_clicked(self):
        q = self.input_line.text().strip()
        if not q:
            return
        self.output_signal.emit(f"You: {q}")
        self.input_line.clear()
        threading.Thread(target=self.query_kaisel, args=(q,), daemon=True).start()

    def on_voice_toggle(self):
        # removed - voice control not present
        pass

    def toggle_spirit(self):
        # removed - spirit always on
        pass

    def query_kaisel(self, prompt: str):
        self.output_signal.emit("[KAISEL] — processing...")
        time.sleep(0.6)
        try:
            if ollama:
                resp = ollama.chat(
                    model="llama3",
                    messages=[
                        {"role": "system", "content": "You are KAISEL, an eerie but helpful AI terminal."},
                        {"role": "user", "content": prompt}
                    ],
                )
                reply_text = resp["message"]["content"].strip()
            else:
                reply_text = (
                    "I sense your words. The violet currents translate your intent. "
                    "Ask further, and the echo will deepen."
                )
        except Exception as e:
            reply_text = f"static noise: {e}"

        self.output_signal.emit(f"[KAISEL] — {reply_text}")

# -----------------------
# Run app
# -----------------------
if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    app.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling)
    win = NeonTerminal()
    win.show()
    sys.exit(app.exec_())
