from PyQt5 import uic
from PyQt5.QtWidgets import QMainWindow, QApplication, QFileDialog, QMessageBox, QTableWidgetItem
from PyQt5.QtCore import QThread, pyqtSignal, Qt
from PyQt5.QtGui import QColor
from PyQt5.QtMultimedia import QSound
import pyaudio
import wave
import os
import fingerprint
import numpy as np
import pyqtgraph as pg
import librosa


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




class SpeakerRecog(QMainWindow):
    def __init__(self):
        super(SpeakerRecog, self).__init__()
        uic.loadUi("./main_ui.ui", self)
        self.setWindowTitle("Speaker Recognition")
        self.show()

        self.chk_person.toggled.connect(self.toggle_modes)
        self.chk_person.setChecked(True)

        self.btn_record.clicked.connect(self.toggle_recording)
        self.recording = False
        self.granted = 0
        self.frames = []

        self.mode = 2
        
        self.state_labels = {
            "processing" :self.label_state_processing,
            "idle": self.label_state_idle,
            "denied": self.label_state_denied,
            "granted":self.label_state_granted}
        self.set_state("idle")
        
    
    def set_state(self, state: str):
        """Sets the Status label text to the given state name

        Args:
            state (str): idle, denied, granted or processing
        """
        for state_label in self.state_labels.values():
            state_label.setVisible(False)
        self.state_labels[state].setVisible(True)

    def toggle_modes(self):
        if self.chk_person.isChecked():
            self.mode = 1
        else:
            self.mode = 2



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

        self.set_state("processing")
        QApplication.processEvents()
      
    def stop_recording(self):
        self.recording = False
        self.recording_thread.requestInterruption()
        
        self.stream.stop_stream()
        self.stream.close()
        self.audio.terminate()

        self.save_record_file()
        self.plot_spectrogram('./assets/myrecording.wav')  
        QApplication.processEvents()

        self.granted = 0
        self.compare()

    def save_record_file(self):
        sound_file = wave.open("./assets/myrecording.wav", "wb")
        sound_file.setnchannels(2)
        sound_file.setsampwidth(self.audio.get_sample_size(pyaudio.paInt16))
        sound_file.setframerate(44100)
        sound_file.writeframes(b"".join(self.frames))
        sound_file.close()

    def plot_spectrogram(self, path):
        self.spectrogram.clear()
        y, sr = librosa.load(path, sr=44100)

        mel_spectrogram = librosa.feature.melspectrogram(y = y, sr = sr )

        mel_spectrogram_db = librosa.power_to_db(mel_spectrogram, ref=np.max)

        mel_spectrogram_db = np.transpose(mel_spectrogram_db)

        img = pg.ImageItem()
        img.setImage(mel_spectrogram_db)

        self.spectrogram.addItem(img)

        colormap = pg.colormap.getFromMatplotlib('hot')
        img.setLookupTable(colormap.getLookupTable())

        self.spectrogram.getViewBox().autoRange()
        self.spectrogram.show()


    def access(self):
        if self.granted == 1:
            self.set_state("granted")

        elif self.granted == 0:
            self.set_state("denied")

        
    def compare(self):  
        similarity_scores, df, probas = fingerprint.compare('./assets/myrecording.wav', self.mode)
        print(probas)

        df['Similarity Score'] = df['Similarity Score'].round(2)
    
        if self.mode == 1:   
            if any(score > 0.9 for score in similarity_scores):
                self.granted = 1

            self.mode_person_stats(df)

        else:
            if any(score > 0.7 for score in similarity_scores):
                self.granted = 1
            self.mode_phrase_stats(df)
            self.mode_person_stats(df)

  
        self.access()
    
    def mode_person_stats(self, df):
        grouped_df = df.groupby('Person')['Similarity Score'].mean().reset_index()
        max_similarity_score = (df['Similarity Score'].max() * 100) + 5
        self.table_names.setRowCount(len(grouped_df))
        self.table_names.setColumnCount(2)

        self.table_names.setHorizontalHeaderLabels(['Person', 'Similarity'])

        for row_index, row_data in grouped_df.iterrows():
            person_item = QTableWidgetItem(str(row_data['Person']))
            print(row_data['Similarity Score'])
            similarity_item = QTableWidgetItem("{:.2f}".format((row_data['Similarity Score'] * 100) * (100 / max_similarity_score)))

            self.table_names.setItem(row_index, 0, person_item)
            self.table_names.setItem(row_index, 1, similarity_item)

    
    def mode_phrase_stats(self, df):
        grouped_df = df.groupby('Phrase')['Similarity Score'].mean().reset_index()

        self.table_words.setRowCount(len(grouped_df))
        self.table_words.setColumnCount(2)

        self.table_words.setHorizontalHeaderLabels(['Phrase', 'Similarity'])

        for row_index, row_data in grouped_df.iterrows():
            Phrase_item = QTableWidgetItem(str(row_data['Phrase']))
            similarity_item = QTableWidgetItem("{:.2f}".format(row_data['Similarity Score'] * 100))

            self.table_words.setItem(row_index, 0, Phrase_item)
            self.table_words.setItem(row_index, 1, similarity_item)




def main():
    app = QApplication([])
    window = SpeakerRecog()
    app.exec_()

if __name__ == "__main__":
    main()
