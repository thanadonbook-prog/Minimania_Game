from maya import cmds
from maya import OpenMayaUI as omui
from PySide6 import QtWidgets, QtCore, QtGui
from shiboken6 import wrapInstance
import random
import os

def maya_main_window():
    ptr = omui.MQtUtil.mainWindow()
    return wrapInstance(int(ptr), QtWidgets.QWidget)

class RhythmGame(QtWidgets.QDialog):
    def __init__(self, parent=maya_main_window()):
        super(RhythmGame, self).__init__(parent)
        self.setWindowTitle("MiniMania")
        self.setFixedSize(420, 600)
        self.setStyleSheet("""
            QDialog { background-color: #1b1b1b; color: #ddd; font-size: 14px; }
            QPushButton { background-color: #444; color: white; padding: 6px; border-radius: 4px; }
            QPushButton:hover { background-color: #666; }
            QLabel { font-weight: bold; }
        """)
        self.setFocusPolicy(QtCore.Qt.StrongFocus)

        # --- Game settings ---
        self.columns = 4
        self.column_width = 90
        self.hit_zone_y = 460
        self.notes = []
        self.score = 0
        self.high_score = 0
        self.combo = 0
        self.highest_combo = 0
        self.speed = 12
        self.spawn_interval = 800
        self.difficulty = "Normal"

        # Judgement windows
        self.PERFECT_WINDOW = 20
        self.GOOD_WINDOW = 40
        self.BAD_WINDOW = 60

        # Key mapping
        self.key_map = {
            QtCore.Qt.Key_D.value: 0,
            QtCore.Qt.Key_F.value: 1,
            QtCore.Qt.Key_J.value: 2,
            QtCore.Qt.Key_K.value: 3
        }

        # --- Timers ---
        self.timer_move = QtCore.QTimer(self)
        self.timer_move.timeout.connect(self.update_notes)
        self.timer_spawn = QtCore.QTimer(self)
        self.timer_spawn.timeout.connect(self.spawn_notes)

        # assets on Desktop
        self.assets_dir = r"---"
        # file names (PUT THE ASSETS PATH HERE )
        #EX  self.assets_dir = r"C:\Users\ACER\project_Minimania\Assets"
        self.effect_files = {
            "Perfect": "perfect.png",
            "Good":    "good.png",
            "Bad":     "bad.png",
            "Miss":    "miss.png"
        }
        # effect sprite size
        self.effect_size = (80, 80)  # width, height

        # keep references to running animations so they don't get GC'd
        self._running_animations = []

        self.create_widgets()
        self.create_layout()
        self.create_connections()

    # -----------------------------
    def create_widgets(self):
        self.label_info = QtWidgets.QLabel("Select Difficulty and Press Start")
        self.label_info.setAlignment(QtCore.Qt.AlignCenter)

        self.label_score = QtWidgets.QLabel("Score: 0")
        self.label_score.setAlignment(QtCore.Qt.AlignCenter)

        self.label_combo = QtWidgets.QLabel("Combo: 0 | Highest Combo: 0")
        self.label_combo.setAlignment(QtCore.Qt.AlignCenter)

        self.combo_diff = QtWidgets.QComboBox()
        self.combo_diff.addItems(["Easy", "Normal", "Hard", "Insane", "Extreme"])

        # --- Play area ---
        self.play_area = QtWidgets.QFrame()
        self.play_area.setFixedSize(self.columns*self.column_width, 500)
        self.play_area.setStyleSheet("background-color: #111; border: 2px solid #333; border-radius: 6px;")
        self.play_area.setLayout(None)
        self.play_area.setFocusPolicy(QtCore.Qt.NoFocus)

        # Column visual lines
        for i in range(1, self.columns):
            line = QtWidgets.QFrame(self.play_area)
            line.setGeometry(i*self.column_width, 0, 2, self.play_area.height())
            line.setStyleSheet("background-color: #333;")

        # Judgement line
        self.hit_zone = QtWidgets.QFrame(self.play_area)
        self.hit_zone.setGeometry(0, self.hit_zone_y, self.columns*self.column_width, 6)
        self.hit_zone.setStyleSheet("background-color: cyan; border-radius: 3px;")

        # --- Buttons ---
        self.btn_start = QtWidgets.QPushButton("▶ Start Game")
        self.btn_stop = QtWidgets.QPushButton("■ Stop")
        self.btn_start.setFixedWidth(120)
        self.btn_stop.setFixedWidth(80)

    # -----------------------------
    def create_layout(self):
        layout = QtWidgets.QVBoxLayout(self)
        layout.addWidget(self.label_info)
        layout.addWidget(self.label_score)
        layout.addWidget(self.label_combo)
        layout.addWidget(self.combo_diff)
        layout.addWidget(self.play_area, alignment=QtCore.Qt.AlignCenter)

        btn_layout = QtWidgets.QHBoxLayout()
        btn_layout.addStretch()
        btn_layout.addWidget(self.btn_start)
        btn_layout.addWidget(self.btn_stop)
        btn_layout.addStretch()

        layout.addLayout(btn_layout)

    # -----------------------------
    def create_connections(self):
        self.btn_start.clicked.connect(self.start_game)
        self.btn_stop.clicked.connect(self.stop_game)

    # -----------------------------
    def start_game(self):
        self.stop_game()
        self.score = 0
        self.combo = 0
        self.label_score.setText("Score: 0")
        self.label_combo.setText(f"Combo: 0 | Highest Combo: {self.highest_combo}")
        self.label_info.setText("Game Started!")
        self.notes.clear()

        diff = self.combo_diff.currentText()
        self.difficulty = diff

        if diff == "Easy":
            self.speed = 8
            self.spawn_interval = 900
        elif diff == "Normal":
            self.speed = 12
            self.spawn_interval = 700
        elif diff == "Hard":
            self.speed = 16
            self.spawn_interval = 400
        elif diff == "Insane":
            self.speed = 22
            self.spawn_interval = 220
        elif diff == "Extreme":
            self.speed = 30           # ความเร็วสูง
            self.spawn_interval = 120  # โน้ต spawn เยอะ

        self.timer_move.start(30)
        self.timer_spawn.start(self.spawn_interval)
        self.activateWindow()
        self.setFocus()

    # -----------------------------
    def stop_game(self):
        self.timer_move.stop()
        self.timer_spawn.stop()
        for note in self.notes:
            note["widget"].deleteLater()
        self.notes.clear()
        if self.score > self.high_score:
            self.high_score = self.score
        self.label_info.setText(
            f"Game Stopped! Score: {self.score} | High Score: {self.high_score} | Highest Combo: {self.highest_combo}"
        )

    # -----------------------------
    def spawn_notes(self):
        # --- Extreme ไม่มี random speed ---
        speed_variation = 0

        # จำนวนโน้ตต่อ spawn
        if self.difficulty == "Extreme":
            weights = [1, 1, 1, 0.2]  # ลดโอกาส spawn 4 โน้ตพร้อมกัน
            num_notes = random.choices([1, 2, 3, 4], weights=weights)[0]
        elif self.difficulty == "Insane":
            num_notes = random.randint(2,3)
        elif self.difficulty == "Hard":
            num_notes = random.randint(1,3)
        else:
            num_notes = random.randint(1,2)

        # สุ่มบันไดสำหรับ Insane / Extreme
        if self.difficulty in ["Insane", "Extreme"] and random.random() < 0.4:
            # Stair pattern: 0->1->2->3->2->1...
            start_col = random.randint(0, self.columns-1)
            stair_cols = [(start_col + i) % self.columns for i in range(num_notes)]
            cols = stair_cols
        else:
            cols = random.sample(range(self.columns), num_notes)

        for col in cols:
            note = QtWidgets.QFrame(self.play_area)
            note.setFixedSize(self.column_width-10, 20)
            note.setStyleSheet("background-color: #e74c3c; border-radius: 6px;")
            note.setGeometry(col*self.column_width + 5, 0, self.column_width-10, 20)
            note.show()
            self.notes.append({"widget": note, "column": col, "y": 0, "hit": False, "speed": self.speed + speed_variation})

        # Random interval สำหรับ Extreme / Insane
        if self.difficulty == "Extreme":
            next_interval = self.spawn_interval
        elif self.difficulty == "Insane":
            next_interval = random.randint(180, 250)
        else:
            next_interval = self.spawn_interval
        self.timer_spawn.start(next_interval)

    # -----------------------------
    def update_notes(self):
        remove_list = []
        for note in self.notes:
            note["y"] += note.get("speed", self.speed)
            note["widget"].move(note["column"]*self.column_width + 5, note["y"])

            if note["y"] > self.play_area.height():
                remove_list.append(note)
                note["widget"].deleteLater()
                if not note["hit"]:
                    # show Miss effect on this column
                    try:
                        self.show_hit_effect(note["column"], "Miss")
                    except Exception:
                        pass
                    if self.combo > self.highest_combo:
                        self.highest_combo = self.combo
                    self.combo = 0
                    self.score = 0
                    self.label_score.setText(f"Score: {self.score}")
                    self.label_combo.setText(f"Combo: {self.combo} | Highest Combo: {self.highest_combo}")
                    self.label_info.setText("Miss!")
                    self.label_info.setStyleSheet("color: #e74c3c; font-weight: bold;")

        for note in remove_list:
            if note in self.notes:
                self.notes.remove(note)

    # -----------------------------
    def show_hit_effect(self, col, result):
        """
        แสดง sprite effect (Perfect/Good/Bad/Miss) ที่คอลัมน์ col แล้วจางหาย
        - col: index ของคอลัมน์ (0..columns-1)
        - result: "Perfect" / "Good" / "Bad" / "Miss"
        """
        fname = self.effect_files.get(result, None)
        pix = None
        if fname:
            path = os.path.join(self.assets_dir, fname)
            if os.path.exists(path):
                pix = QtGui.QPixmap(path).scaled(self.effect_size[0], self.effect_size[1],
                                                 QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation)

        effect = QtWidgets.QLabel(self.play_area)
        effect.setAttribute(QtCore.Qt.WA_TranslucentBackground)
        w, h = self.effect_size
        # center effect in the column
        x = col * self.column_width + (self.column_width - w) // 2
        y = self.hit_zone_y - h - 8
        effect.setGeometry(x, y, w, h)

        if pix:
            effect.setPixmap(pix)
        else:
            # fallback: white circle
            effect.setStyleSheet("background-color: white; border-radius: {}px;".format(min(w, h)//2))

        effect.show()

        # opacity effect + animation
        opacity = QtWidgets.QGraphicsOpacityEffect(effect)
        effect.setGraphicsEffect(opacity)
        anim = QtCore.QPropertyAnimation(opacity, b"opacity", self)
        anim.setDuration(450)
        anim.setStartValue(1.0)
        anim.setEndValue(0.0)
        anim.finished.connect(effect.deleteLater)

        # keep a reference so it doesn't get GC'd while running
        self._running_animations.append(anim)

        def on_anim_finished():
            try:
                self._running_animations.remove(anim)
            except ValueError:
                pass

        anim.finished.connect(on_anim_finished)
        anim.start()

    # -----------------------------
    def keyPressEvent(self, event):
        key = event.key()
        if key in self.key_map:
            col = self.key_map[key]

            notes_in_col = [n for n in self.notes if n["column"] == col and not n["hit"]]
            if not notes_in_col:
                return

            hit_note = None
            grade = None
            min_diff = float('inf')
            for note in notes_in_col:
                diff = abs(note["y"] - self.hit_zone_y)
                if diff < min_diff:
                    min_diff = diff
                    if diff <= self.PERFECT_WINDOW:
                        hit_note = note
                        grade = "Perfect"
                    elif diff <= self.GOOD_WINDOW:
                        hit_note = note
                        grade = "Good"
                    elif diff <= self.BAD_WINDOW:
                        hit_note = note
                        grade = "Bad"

            if hit_note:
                hit_note["hit"] = True
                self.combo += 1
                if self.combo > self.highest_combo:
                    self.highest_combo = self.combo

                if grade == "Perfect":
                    self.score += 3
                    color = "#2ecc71"
                elif grade == "Good":
                    self.score += 2
                    color = "#f1c40f"
                elif grade == "Bad":
                    self.score += 1
                    color = "#e67e22"

                # show hit effect sprite
                try:
                    self.show_hit_effect(col, grade)
                except Exception:
                    pass

                self.label_score.setText(f"Score: {self.score}")
                self.label_combo.setText(f"Combo: {self.combo} | Highest Combo: {self.highest_combo}")
                self.label_info.setText(f"{grade}!")
                self.label_info.setStyleSheet(f"color: {color}; font-weight: bold;")
                hit_note["widget"].deleteLater()
                self.notes.remove(hit_note)
        else:
            super(RhythmGame, self).keyPressEvent(event)

# -----------------------------
def show_ui():
    global rhythm_dialog
    try:
        rhythm_dialog.close()
        rhythm_dialog.deleteLater()
    except:
        pass

    rhythm_dialog = RhythmGame()
    rhythm_dialog.show()
    rhythm_dialog.activateWindow()
    rhythm_dialog.setFocus()

show_ui()
