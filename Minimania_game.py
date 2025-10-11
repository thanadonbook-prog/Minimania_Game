from maya import cmds
from maya import OpenMayaUI as omui
from PySide6 import QtWidgets, QtCore
from shiboken6 import wrapInstance
import random

def maya_main_window():
    main_window_ptr = omui.MQtUtil.mainWindow()
    return wrapInstance(int(main_window_ptr), QtWidgets.QWidget)

class RhythmGameMultiNotes(QtWidgets.QDialog):
    def __init__(self, parent=maya_main_window()):
        super(RhythmGameMultiNotes, self).__init__(parent)

        self.setWindowTitle("Rhythm Game Multi Notes")
        self.setFixedSize(400, 450)

        # Settings
        self.columns = 4
        self.column_width = 80
        self.hit_zone_y = 300
        self.notes = []

        self.score = 0
        self.notes_per_spawn = 1
        self.note_speed = 10
        self.note_interval = 400

        # Hit windows
        self.PERFECT_WINDOW = 10
        self.GOOD_WINDOW = 25

        # Timers
        self.timer_move = QtCore.QTimer(self)
        self.timer_move.timeout.connect(self.update_notes)
        self.timer_note = QtCore.QTimer(self)
        self.timer_note.timeout.connect(self.spawn_note)

        # Key mapping
        self.key_map = {
            QtCore.Qt.Key_D: 0,
            QtCore.Qt.Key_F: 1,
            QtCore.Qt.Key_K: 2,
            QtCore.Qt.Key_L: 3
        }

        self.create_widgets()
        self.create_layout()
        self.create_connections()

    def create_widgets(self):
        self.label_info = QtWidgets.QLabel("Press D F K L on hit zone!")
        self.label_info.setAlignment(QtCore.Qt.AlignCenter)
        self.label_score = QtWidgets.QLabel("Score: 0")
        self.label_score.setAlignment(QtCore.Qt.AlignCenter)

        # Difficulty selection
        self.combo_difficulty = QtWidgets.QComboBox()
        self.combo_difficulty.addItems(["Easy", "Normal", "Hard"])
        self.combo_difficulty.currentIndexChanged.connect(self.change_difficulty)

        # Play area
        self.play_area = QtWidgets.QFrame()
        self.play_area.setFixedSize(self.columns*self.column_width, 320)
        self.play_area.setStyleSheet("background-color: #222;")
        self.play_area.setLayout(None)

        # Hit zone
        self.hit_zone = QtWidgets.QFrame(self.play_area)
        self.hit_zone.setGeometry(0, self.hit_zone_y, self.columns*self.column_width, 20)
        self.hit_zone.setStyleSheet("background-color: yellow;")

        # Buttons
        self.btn_start = QtWidgets.QPushButton("Start")
        self.btn_stop = QtWidgets.QPushButton("Stop")

    def create_layout(self):
        layout = QtWidgets.QVBoxLayout(self)
        layout.addWidget(self.label_info)
        layout.addWidget(self.label_score)
        layout.addWidget(QtWidgets.QLabel("Select Difficulty:"))
        layout.addWidget(self.combo_difficulty)
        layout.addWidget(self.play_area)
        layout.addWidget(self.btn_start)
        layout.addWidget(self.btn_stop)

    def create_connections(self):
        self.btn_start.clicked.connect(self.start_game)
        self.btn_stop.clicked.connect(self.stop_game)

    def change_difficulty(self):
        diff = self.combo_difficulty.currentText()
        if diff == "Easy":
            self.note_speed = 10
            self.notes_per_spawn = 1
            self.note_interval = 500
        elif diff == "Normal":
            self.note_speed = 20
            self.notes_per_spawn = 2
            self.note_interval = 400
        else:  # Hard
            self.note_speed = 30
            self.notes_per_spawn = 3
            self.note_interval = 300

    def start_game(self):
        self.score = 0
        self.label_score.setText("Score: 0")
        self.notes.clear()
        # ลบโน้ตเก่า
        for child in self.play_area.findChildren(QtWidgets.QWidget):
            if child != self.hit_zone:
                child.deleteLater()
        # Start timers
        self.timer_move.start(30)
        self.timer_note.start(self.note_interval)
        self.label_info.setText(f"Game Started! Difficulty: {self.combo_difficulty.currentText()}")

    def stop_game(self):
        self.timer_move.stop()
        self.timer_note.stop()
        for note in self.notes:
            note['widget'].deleteLater()
        self.notes.clear()
        self.label_info.setText(f"Game Stopped! Final Score: {self.score}")

    def spawn_note(self):
        num_notes = random.randint(1, self.notes_per_spawn)
        available_cols = list(range(self.columns))
        random.shuffle(available_cols)
        for i in range(num_notes):
            col = available_cols[i]
            note = QtWidgets.QFrame(self.play_area)
            note.setFixedSize(self.column_width, 20)
            note.setStyleSheet("background-color: red;")
            note.setGeometry(col*self.column_width, 0, self.column_width, 20)
            note.show()
            self.notes.append({'widget': note, 'column': col, 'y':0})

    def update_notes(self):
        remove_notes = []
        for note in self.notes:
            note['y'] += self.note_speed
            note['widget'].move(note['column']*self.column_width, note['y'])
            if note['y'] > self.play_area.height():
                remove_notes.append(note)
                note['widget'].deleteLater()
                # Reset score on miss
                self.score = 0
                self.label_score.setText(f"Score: {self.score}")
                self.label_info.setText("Miss!")
        for note in remove_notes:
            self.notes.remove(note)

    def keyPressEvent(self, event):
        key = event.key()
        if key in self.key_map:
            col = self.key_map[key]
            hit_note = None
            grade = None
            for note in self.notes:
                if note['column'] == col:
                    note_center_y = note['y'] + note['widget'].height()/2
                    hit_zone_center = self.hit_zone_y + self.hit_zone.height()/2
                    diff = abs(note_center_y - hit_zone_center)
                    if diff <= self.PERFECT_WINDOW:
                        hit_note = note
                        grade = "Perfect"
                        break
                    elif diff <= self.GOOD_WINDOW:
                        hit_note = note
                        grade = "Good"
                        break
            if hit_note:
                self.score += 1
                self.label_score.setText(f"Score: {self.score}")
                self.label_info.setText(grade + "!")
                cmds.polyCube(name=f"cube_{self.score}")
                hit_note['widget'].deleteLater()
                self.notes.remove(hit_note)
            else:
                self.score = 0
                self.label_score.setText(f"Score: {self.score}")
                self.label_info.setText("Miss!")
        else:
            super(RhythmGameMultiNotes, self).keyPressEvent(event)

# -----------------------------------------------------
def show_ui():
    global rhythm_game_multi_dialog
    try:
        rhythm_game_multi_dialog.close()
        rhythm_game_multi_dialog.deleteLater()
    except:
        pass

    rhythm_game_multi_dialog = RhythmGameMultiNotes()
    rhythm_game_multi_dialog.show()

show_ui()
