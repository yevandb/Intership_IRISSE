import queue

import numpy as np
from PyQt5 import QtWidgets
from PyQt5.QtCore import QTimer
import pyqtgraph as pg
from data_speed import Data_Speed
pg.setConfigOption('background', 'w')
pg.setConfigOption('foreground', 'k')

class fenetre_vitesse(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Vitesse")
        self.resize(1200, 400)
        self.buffer_size = 600000
        layout = QtWidgets.QVBoxLayout(self)
        self.setLayout(layout)
        self.buffer_vitesse=np.full(self.buffer_size,np.nan)
        x = np.arange(self.buffer_size)

        self.plot_vitesse = pg.PlotWidget(title="Vitesse")
        layout.addWidget(self.plot_vitesse)

        layout_c1=QtWidgets.QVBoxLayout(self)
        layout_c2=QtWidgets.QVBoxLayout(self)
        layout_boutons = QtWidgets.QHBoxLayout()
        layout.addLayout(layout_boutons)
        layout_boutons.addLayout(layout_c1, 1)
        layout_boutons.addLayout(layout_c2, 1)

        self.window_size=15000
        self.x_2=np.arange(0, self.buffer_size)

        self.courbe_vitesse = self.plot_vitesse.plot(x,self.buffer_vitesse,pen=pg.mkPen(color='b', width=2.5))
        self.plot_vitesse.setYRange(0,2,padding=0)
        self.plot_vitesse.setXRange(0,self.window_size,padding=0)

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.refresh_plot_vitesse)
        self.timer.setInterval(30)

        self.start_button = QtWidgets.QPushButton("Start", self)
        self.start_button.clicked.connect(self.start_acquisition)
        layout_c1.addWidget(self.start_button)

        self.label_vitesse_instant = QtWidgets.QLabel("Vitesse instantanée : --")
        layout_c2.addWidget(self.label_vitesse_instant)

        self.moyenne_button = QtWidgets.QPushButton("Afficher la moyenne de la vitesse")
        self.moyenne_button.clicked.connect(self.afficher_moyenne_vitesse)
        layout_c1.addWidget(self.moyenne_button)

        self.label_moyenne = QtWidgets.QLabel("Moyenne de la vitesse : --")
        layout_c2.addWidget(self.label_moyenne)

        self.compteur=0
        self.data_queue_vitesse=queue.Queue()
        self.worker_vitesse=Data_Speed(data_vitesse=self.data_queue_vitesse,index_v=12,index_emg=0,ip="127.0.0.1")
        self.ptr_vitesse=0
        self.window_index=0
    def update_vitesse(self, data_queue, buffer,curve):
        ptr=self.ptr_vitesse
        updated=False
        last_value = None

        while not data_queue.empty():
            new_data = data_queue.get()
            length = new_data.shape[0]
            end = ptr + length
            if ptr + length > buffer.size:
                break
            buffer[ptr:end] = new_data
            ptr = end
            updated = True
            last_value = new_data[-1]

        self.ptr_vitesse=ptr

        if updated:
            start = max(0, ptr - self.window_size)
            x = np.arange(start, ptr)
            y = buffer[start:ptr]
            x = np.array(x, dtype=np.float64)
            y = np.array(y, dtype=np.float64)
            mask = ~np.isnan(y)
            x = x[mask]
            y = y[mask]

            if len(x) >= 2:
                curve.setData(self.x_2, buffer, _callSync='off')
            if last_value is not None:
                self.label_vitesse_instant.setText(f"Vitesse instantanée : {last_value:.2f} m/s")

        return ptr

    def refresh_plot_vitesse(self):

        ptr=self.update_vitesse(self.data_queue_vitesse,self.buffer_vitesse,self.courbe_vitesse)

        if ptr>self.window_size*self.window_index:
            self.plot_vitesse.setXRange(self.window_size*self.window_index,self.window_size*(self.window_index+1),padding=0)
            self.window_index+=1


    def start_acquisition(self):
        if not self.timer.isActive(): self.timer.start()
        if not self.worker_vitesse.isRunning() : self.worker_vitesse.start()
        self.start_button.setEnabled(False)

    def afficher_moyenne_vitesse(self):
        valid_values = self.buffer_vitesse[~np.isnan(self.buffer_vitesse)]
        if valid_values.size > 0:
            moyenne = np.mean(valid_values)
            self.label_moyenne.setText(f"Moyenne de la vitesse : {moyenne:.2f} m/s")
        else:
            self.label_moyenne.setText("Moyenne de la vitesse : --")








