from PyQt5 import uic
from PyQt5.QtWidgets import QMainWindow, QApplication
from PyQt5.QtCore import QThread, pyqtSignal, Qt
from PyQt5.QtGui import QColor
import pyaudio
import wave
import numpy as np
import pyqtgraph as pg
import librosa
from fingerprint import audioSpectogram, loopFolder
import os
import pandas as pd
import glob


class RecordingThread(QThread):
    done_signal = pyqtSignal()

    def __init__(self, frames, stream, duration):
        super().__init__()
        self.frames = frames
        self.stream = stream
        self.duration = duration

    def run(self):
        chunk_size = 1024
        total_frames = int(44100 / chunk_size * self.duration)

        for _ in range(total_frames):
            data = self.stream.read(chunk_size)
            self.frames.append(data)

        self.done_signal.emit()


class VoiceRecognitionApp(QMainWindow):
    def __init__(self):
        super(VoiceRecognitionApp, self).__init__()
        uic.loadUi("./Recorder.ui", self)
        self.setWindowTitle("Voice Recognition")
        self.show()

        self.RecordButton.clicked.connect(self.toggle_recording)
        self.frames = []
        self.recording = False

        self.NameEdit.setText("Kyrollos")
        self.PhraseEdit.setText("Grant me access")
        self.NumberEdit.setText("1")

        self.btn_hashing1.clicked.connect(lambda: self.HashFiles('./AudioFingerprints/', 1))
        self.btn_hashing2.clicked.connect(lambda: self.HashFiles('./AudioFingerprints/', 2))

        self.recording_thread = None

    def loopFolder(self, path:str,extension:str):
        Files = glob.glob(path + "/*" + extension)
        return Files
    
    def HashFiles(self, root_path, mode):
        person_folders = loopFolder(root_path, '')

        hash_data = {'Person': [], 'Phrase': [], 'Fingerprint': []}

        for person in person_folders:
            person_name = os.path.basename(person)
            print("Processing person:", person_name)

            phrase_folders = loopFolder(person, '')

            for phrase in phrase_folders:
                phrase_name = os.path.basename(phrase)
                print("  - Phrase:", phrase_name)

                files = loopFolder(phrase, '.wav')
                for i in range(len(files)):
                    record = os.path.basename(files[i])
                    print("    - File:", record)

                    song = audioSpectogram(files[i], mode, i)
                    fingerprint = song.getData()

                    hash_data['Person'].append(person_name)
                    hash_data['Phrase'].append(phrase_name)
                    hash_data['Fingerprint'].append(fingerprint)

                    del song

        df = pd.DataFrame(hash_data)
        df.to_csv(f'./hashing{mode}.csv', index=False)

    def toggle_recording(self):
        if not self.recording:
            self.start_recording()
        else:
            self.stop_recording()

    def start_recording(self):
        self.recording = True
        self.frames = []

        self.audio = pyaudio.PyAudio()
        self.stream = self.audio.open(format=pyaudio.paInt16, channels=2, rate=44100, input=True, frames_per_buffer=1024)

        self.recording_thread = RecordingThread(self.frames, self.stream, 3.0)
        self.recording_thread.done_signal.connect(self.stop_recording)
        self.recording_thread.start()

        self.recording_state(state="Recording", background_color=QColor(0, 0, 0))
        QApplication.processEvents()

    def stop_recording(self):
        self.recording = False
        self.recording_thread.requestInterruption()

        self.stream.stop_stream()
        self.stream.close()
        self.audio.terminate()

        self.save_record_file()
        self.plot_spectrogram(f"./AudioFingerprints/{self.name}/{self.phrase}/record{self.num}.wav")
        self.recording_state(state="Done Recording", background_color=QColor(0, 150, 0))

    def save_record_file(self):
        self.name, self.phrase, self.num = self.NameEdit.text(), self.PhraseEdit.text(), self.NumberEdit.text()
        sound_file = wave.open(f"./AudioFingerprints/{self.name}/{self.phrase}/record{self.num}.wav", "wb")
        sound_file.setnchannels(2)
        sound_file.setsampwidth(self.audio.get_sample_size(pyaudio.paInt16))
        sound_file.setframerate(44100)
        sound_file.writeframes(b"".join(self.frames))
        sound_file.close()

    def recording_state(self, state, background_color):
        self.AccessLabel.setText(state)
        self.AccessLabel.setStyleSheet(f"background-color: {background_color.name()};")
        self.AccessLabel.setAlignment(Qt.AlignCenter)

    def plot_spectrogram(self, path):
        self.SpectWidget.clear()
        y, sr = librosa.load(path, sr=44100)

        spectrogram = librosa.feature.melspectrogram(y=y, sr=sr)
        spectrogram_db = librosa.power_to_db(spectrogram, ref=np.max)
        spectrogram_db = np.transpose(spectrogram_db)

        img = pg.ImageItem()
        img.setImage(spectrogram_db)
        self.SpectWidget.addItem(img)

        colormap = pg.colormap.getFromMatplotlib('hot')
        img.setLookupTable(colormap.getLookupTable())

        self.SpectWidget.getViewBox().autoRange()
        self.SpectWidget.show()




def main():
    app = QApplication([])
    window = VoiceRecognitionApp()
    app.exec_()


if __name__ == "__main__":
    main()
