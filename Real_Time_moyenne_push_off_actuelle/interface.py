import queue
import numpy as np
from PyQt5 import QtWidgets, QtCore
from PyQt5.QtCore import QTimer
import pyqtgraph as pg
from collections import deque
import pandas as pd

from data_worker import DataWorker

pg.setConfigOption("background", "w")
pg.setConfigOption("foreground", "k")


class FenetreEMG(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Biofeedback EMG Temps Réel")
        self.resize(1200, 400)

        self.subject_mass = 0

        self.points_gauche_brute = []
        self.points_droite_brute = []

        self.list_idx_debut_droite = []
        self.list_idx_fin_droite = []
        self.list_idx_debut_gauche = []
        self.list_idx_fin_gauche = []

        self.buf2_g = deque(maxlen=2)
        self.buf2_d = deque(maxlen=2)
        self.idx2_g = 0
        self.idx2_d = 0

        self.window_pas = 3
        self.buf_moy_g = deque(maxlen=self.window_pas)
        self.buf_moy_d = deque(maxlen=self.window_pas)

        self.buffer_size = 600000
        self.window_size = 30
        self.window_index_g = 0
        self.window_index_d = 0

        self.nombre_pas = 1000
        self.pas_gauche = np.arange(1, self.nombre_pas + 1)
        self.index_pas_gauche = 0

        self.pas_droite = np.arange(1, self.nombre_pas + 1)
        self.index_pas_droite = 0

        self.y_max_gauche = 300
        self.y_max_droite = 300


        # Buffers EMG
        self.buffer_1 = np.full(self.buffer_size, np.nan)
        self.buffer_2 = np.full(self.buffer_size, np.nan)
        self.ptr_left = 0
        self.ptr_right = 0

        self.debut_gauche = 0
        self.debut_droite = 0
        self.fin_droite = 0
        self.fin_gauche = 0
        self.points_gauche = []
        self.points_droite = []

        # Buffers AP GRF
        self.buffer_GRF_gauche = np.full(self.buffer_size, np.nan)
        self.buffer_GRF_droite = np.full(self.buffer_size, np.nan)
        self.ptr_grfg = 0
        self.ptr_grfd = 0

        # Buffers Fz GRF

        self.buffer_vert_gauche = np.full(self.buffer_size, np.nan)
        self.buffer_vert_droite = np.full(self.buffer_size, np.nan)
        self.ptr_vertgauche = 0
        self.ptr_vertdroite = 0

        layout = QtWidgets.QVBoxLayout(self)
        self.setLayout(layout)

        layout_graphs = QtWidgets.QHBoxLayout()
        layout.addLayout(layout_graphs)
        layout_boutons = QtWidgets.QHBoxLayout()
        layout.addLayout(layout_boutons)
        layout_c1 = QtWidgets.QVBoxLayout()
        layout_c2 = QtWidgets.QVBoxLayout()
        layout_boutons.addLayout(layout_c1, 1)
        layout_boutons.addLayout(layout_c2, 1)

        self.plot_moy_gauche = pg.PlotWidget(title="Moyenne EMG gauche")
        self.plot_moy_droite = pg.PlotWidget(title="Moyenne EMG droite")

        self.scatter_moy_gauche = pg.ScatterPlotItem(size=10, brush="b")
        self.plot_moy_gauche.addItem(self.scatter_moy_gauche)

        self.scatter_moy_droite = pg.ScatterPlotItem(size=10, brush="r")
        self.plot_moy_droite.addItem(self.scatter_moy_droite)

        vb_g = self.plot_moy_gauche.getViewBox()
        vb_d = self.plot_moy_droite.getViewBox()
        vb_g.setXRange(0, self.window_size, padding=0)
        vb_d.setXRange(0, self.window_size, padding=0)
        vb_g.setYRange(0, 250, padding=0)
        vb_d.setYRange(0, 250, padding=0)
        self.plot_moy_gauche.enableAutoRange(axis=pg.ViewBox.XAxis, enable=False)
        self.plot_moy_droite.enableAutoRange(axis=pg.ViewBox.XAxis, enable=False)
        self.plot_moy_gauche.enableAutoRange(axis=pg.ViewBox.YAxis, enable=False)
        self.plot_moy_droite.enableAutoRange(axis=pg.ViewBox.YAxis, enable=False)
        self.plot_moy_gauche.getPlotItem().hideAxis("left")
        self.plot_moy_droite.getPlotItem().hideAxis("left")

        layout_graphs.addWidget(self.plot_moy_gauche)
        layout_graphs.addWidget(self.plot_moy_droite)

        self.plot_moy_gauche.getAxis("bottom").setTickSpacing(major=1, minor=1)
        self.plot_moy_droite.getAxis("bottom").setTickSpacing(major=1, minor=1)

        self.threshold_gauche = 0
        self.threshold_droite = 0
        self.consigne = 0.2



        self.hline_gauche_max = pg.InfiniteLine(
            pos=(1 + self.consigne) * self.threshold_gauche,
            angle=0,
            pen=pg.mkPen(color="m", style=QtCore.Qt.DashLine, width=1.2),
            name="seuil max",
        )

        self.hline_gauche_min = pg.InfiniteLine(
            pos=(1 - self.consigne) * self.threshold_gauche,
            angle=0,
            pen=pg.mkPen(color="m", style=QtCore.Qt.DashLine, width=1.2),
            name="seuil min",
        )

        # Idem pour la droite


        self.hline_droite_max = pg.InfiniteLine(
            pos=(1 + self.consigne) * self.threshold_droite,
            angle=0,
            pen=pg.mkPen(color="m", style=QtCore.Qt.DashLine, width=1.2),
            name="seuil max",
        )

        self.hline_droite_min = pg.InfiniteLine(
            pos=(1 - self.consigne) * self.threshold_droite,
            angle=0,
            pen=pg.mkPen(color="m", style=QtCore.Qt.DashLine, width=1.2),
            name="seuil min",
        )

        self.plot_moy_gauche.addItem(self.hline_gauche_max)
        self.plot_moy_gauche.addItem(self.hline_gauche_min)

        self.plot_moy_droite.addItem(self.hline_droite_max)
        self.plot_moy_droite.addItem(self.hline_droite_min)

        # Threads
        self.data_queue_1 = queue.Queue()
        self.data_queue_2 = queue.Queue()
        self.data_GRF_gauche = queue.Queue()
        self.data_GRF_droite = queue.Queue()
        self.data_vert_gauche = queue.Queue()
        self.data_vert_droite = queue.Queue()

        self.worker1 = DataWorker(
            index_emg=0,
            index_ap=7,
            get_emg=True,
            data_emg=self.data_queue_1,
            data_ap=self.data_GRF_gauche,
            ip="127.0.0.1",
        )
        self.worker2 = DataWorker(
            index_emg=1,
            index_ap=1,
            get_emg=True,
            data_emg=self.data_queue_2,
            data_ap=self.data_GRF_droite,
            ip="127.0.0.1",
        )
        self.worker_vert_gauche = DataWorker(
            index_emg=1,
            index_ap=8,
            get_emg=False,
            data_emg=self.data_queue_2,
            data_ap=self.data_vert_gauche,
            ip="127.0.0.1",
        )
        self.worker_vert_droite = DataWorker(
            index_emg=1,
            index_ap=2,
            get_emg=False,
            data_emg=self.data_queue_2,
            data_ap=self.data_vert_droite,
            ip="127.0.0.1",
        )

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.refresh_plots)
        self.timer.setInterval(50)

    def mean_emg_push_off(self, index_debut_prop, index_fin_prop, emg, grf, vert, side):
        if np.all(np.isnan(grf)) or np.nanmax(np.abs(grf)) == 0:
            print("erreur 1")
            return np.nan, index_debut_prop, index_fin_prop

        ptr_grf = self.ptr_grfg if side == "gauche" else self.ptr_grfd
        list_idx_debut = (
            self.list_idx_debut_gauche
            if side == "gauche"
            else self.list_idx_debut_droite
        )
        list_idx_fin = (
            self.list_idx_fin_gauche if side == "gauche" else self.list_idx_fin_droite
        )

        # print(f"[DEBUG] ptr_grf ({side}) = {ptr_grf}")

        seuil = -0.03 * np.nanmax(grf[index_fin_prop:ptr_grf])
        found_debut = False

        for i in range(index_fin_prop, ptr_grf):
            if vert[i] > 0.005 * self.subject_mass:
                if i >= 101:
                    data_previous = np.nanmean(grf[i - 100 : i])
                else:
                    data_previous = np.nanmean(grf[:i])

                if not np.isnan(grf[i]) and grf[i] < seuil and grf[i] < data_previous:
                    index_debut_prop = i
                    found_debut = True
                    break

        if not found_debut:
            # print("erreur 3")
            return np.nan, index_debut_prop, index_fin_prop

        found_fin = False
        for j in range(index_debut_prop, ptr_grf):
            if j >= 100:
                data_previous = np.nanmean(grf[j - 100 : j])
            else:
                data_previous = np.nanmean(grf[:j])
            if data_previous < grf[j] and grf[j] > seuil:
                index_fin_prop = j
                found_fin = True
                break
        if not found_fin:
            # print("erreur 4")
            return np.nan, index_debut_prop, index_fin_prop

        if self.index_pas_gauche > self.window_size * self.window_index_g:
            self.plot_moy_gauche.setXRange(
                self.window_index_g * self.window_size,
                (self.window_index_g + 1) * self.window_size,
            )
            self.window_index_g += 1
        if self.index_pas_droite > self.window_size * self.window_index_d:
            self.plot_moy_droite.setXRange(
                self.window_index_d * self.window_size,
                (self.window_index_d + 1) * self.window_size,
            )
            self.window_index_d += 1

        if index_fin_prop - index_debut_prop > 90:
            list_idx_debut.append(index_debut_prop)
            list_idx_fin.append(index_fin_prop)
            emg_segment = emg[index_debut_prop:index_fin_prop]
            if emg_segment.size == 0 or np.all(np.isnan(emg_segment)):
                print("erreur 5")
                return np.nan, index_debut_prop, index_fin_prop
            mean_val = np.nanmean(emg_segment)
            return mean_val, index_debut_prop, index_fin_prop
        else:
            return np.nan, index_debut_prop, index_fin_prop

    def update_mean_point(self, grf, emg, vert, side):
        debut = getattr(self, f"debut_{side}")
        fin = getattr(self, f"fin_{side}")

        mean, idx_debut, idx_fin = self.mean_emg_push_off(
            debut, fin, emg, grf, vert, side
        )

        setattr(self, f"debut_{side}", idx_debut)
        setattr(self, f"fin_{side}", idx_fin)

        if not np.isnan(mean):
            x_point = (idx_debut + idx_fin) // 2
            y_point_brute = mean

            # moyenne sur ces 2 pas
            """
            buf2 = self.buf2_g if side == 'gauche' else self.buf2_d
            buf2.append(mean)            
            if len(buf2) < 2:
                return
            avg2 = (buf2[0] + buf2[1]) / 2.0
            buf2.clear()
            y_point = avg2
            """
            # moyenne glissante

            buf = self.buf_moy_g if side == "gauche" else self.buf_moy_d
            buf.append(mean)
            smooth_mean = sum(buf) / len(buf)
            y_point = smooth_mean

            if side == "gauche":
                x_graph = self.pas_gauche[self.index_pas_gauche]
                if y_point > self.y_max_gauche:
                    self.y_max_gauche = y_point
                    self.plot_moy_gauche.setYRange(0, self.y_max_gauche)
                if self.points_gauche:
                    x_prev, y_prev = self.points_gauche[-1]
                    x_graph_av = self.pas_gauche[self.index_pas_gauche - 1]
                    self.plot_moy_gauche.plot(
                        [x_graph_av, x_graph],
                        [y_prev, y_point],
                        pen=pg.mkPen(color="b", width=2),
                    )
                self.points_gauche.append((x_point, y_point))
                self.points_gauche_brute.append((x_point, y_point_brute))
                self.scatter_moy_gauche.addPoints(x=[x_graph], y=[y_point])
                self.index_pas_gauche += 1

            elif side == "droite":
                x_graph = self.pas_droite[self.index_pas_droite]
                if y_point > self.y_max_droite:
                    self.y_max_droite = y_point
                    self.plot_moy_droite.setYRange(0, self.y_max_droite)

                if self.points_droite:
                    y_prev = self.points_droite[-1][1]
                    x_graph_av = self.pas_droite[self.index_pas_droite - 1]
                    self.plot_moy_droite.plot(
                        [x_graph_av, x_graph],
                        [y_prev, y_point],
                        pen=pg.mkPen(color="r", width=2),
                    )
                self.points_droite.append((x_point, y_point))
                self.points_droite_brute.append((x_point, y_point_brute))
                self.scatter_moy_droite.addPoints(x=[x_graph], y=[y_point])
                self.index_pas_droite += 1

    def refresh_plots(self):

        self._update_buffer_and_curve(self.data_queue_1, self.buffer_1, "left")
        self._update_buffer_and_curve(self.data_queue_2, self.buffer_2, "right")
        self._update_buffer_and_curve(
            self.data_GRF_gauche, self.buffer_GRF_gauche, "grfg"
        )
        self._update_buffer_and_curve(
            self.data_GRF_droite, self.buffer_GRF_droite, "grfd"
        )
        self._update_buffer_and_curve(
            self.data_vert_gauche, self.buffer_vert_gauche, "vertgauche"
        )
        self._update_buffer_and_curve(
            self.data_vert_droite, self.buffer_vert_droite, "vertdroite"
        )

        self.update_mean_point(
            self.buffer_GRF_gauche,
            self.buffer_1,
            self.buffer_vert_gauche,
            side="gauche",
        )
        self.update_mean_point(
            self.buffer_GRF_droite,
            self.buffer_2,
            self.buffer_vert_droite,
            side="droite",
        )

    def _update_buffer_and_curve(self, data_queue, buffer, side):
        ptr = getattr(self, f"ptr_{side}")

        while not data_queue.empty():
            new_data = data_queue.get()
            length = new_data.shape[0]
            end = ptr + length
            if ptr + length > buffer.size:
                break

            buffer[ptr:end] = new_data
            ptr = end

        setattr(self, f"ptr_{side}", ptr)

    def start_acquisition(self):
        if not self.worker1.isRunning():
            self.worker1.start()
        if not self.worker2.isRunning():
            self.worker2.start()
        if not self.worker_vert_droite.isRunning():
            self.worker_vert_droite.start()
        if not self.worker_vert_gauche.isRunning():
            self.worker_vert_gauche.start()
        if not self.timer.isActive():
            self.timer.start()

    def save_buffers(self):

        ptr_left = self.ptr_left
        ptr_right = self.ptr_right
        ptr_grf_left = self.ptr_grfg
        ptr_grf_right = self.ptr_grfd
        ptr_vert_left = self.ptr_vertgauche
        ptr_vert_right = self.ptr_vertdroite

        b1 = self.buffer_1[:ptr_left]
        b2 = self.buffer_2[:ptr_right]
        g1 = self.buffer_GRF_gauche[:ptr_grf_left]
        g2 = self.buffer_GRF_droite[:ptr_grf_right]
        v1 = self.buffer_vert_gauche[:ptr_vert_left]
        v2 = self.buffer_vert_droite[:ptr_vert_right]

        # Points de moyenne (scatter)
        xg, yg = zip(*self.points_gauche) if self.points_gauche else ([], [])
        xd, yd = zip(*self.points_droite) if self.points_droite else ([], [])
        xg_brute, yg_brute = (
            zip(*self.points_gauche_brute) if self.points_gauche_brute else ([], [])
        )
        xd_brute, yd_brute = (
            zip(*self.points_droite_brute) if self.points_droite_brute else ([], [])
        )

        # Index
        idx_debut_droite = (
            np.array(self.list_idx_debut_droite)
            if self.list_idx_debut_droite
            else np.array([])
        )
        idx_fin_droite = (
            np.array(self.list_idx_fin_droite)
            if self.list_idx_fin_droite
            else np.array([])
        )

        idx_debut_gauche = (
            np.array(self.list_idx_debut_gauche)
            if self.list_idx_debut_gauche
            else np.array([])
        )
        idx_fin_gauche = (
            np.array(self.list_idx_fin_gauche)
            if self.list_idx_fin_gauche
            else np.array([])
        )

        # Padding à la même longueur
        max_len = max(
            len(b1),
            len(b2),
            len(g1),
            len(g2),
            len(v1),
            len(v2),
            len(xg),
            len(xd),
            len(xg_brute),
            len(xd_brute),
            len(idx_debut_droite),
            len(idx_fin_droite),
            len(idx_fin_gauche),
            len(idx_debut_gauche),
        )

        def pad(arr):
            arr = arr.astype(float)  # Convertir en float pour permettre les NaN
            return np.pad(arr, (0, max_len - len(arr)), constant_values=np.nan)

        df = {
            "EMG_Gauche": pad(b1),
            "EMG_Droite": pad(b2),
            "GRF_Gauche": pad(g1),
            "GRF_Droite": pad(g2),
            "VERT_Gauche": pad(v1),
            "VERT_Droite": pad(v2),
            "X_Mean_G": pad(np.array(xg)),
            "Y_Mean_G": pad(np.array(yg)),
            "X_Mean_D": pad(np.array(xd)),
            "Y_Mean_D": pad(np.array(yd)),
            "X_Mean_G_brute": pad(np.array(xg_brute)),
            "Y_Mean_G_brute": pad(np.array(yg_brute)),
            "X_Mean_D_brute": pad(np.array(xd_brute)),
            "Y_Mean_D_brute": pad(np.array(yd_brute)),
            "Index_debut_droite": pad(np.array(idx_debut_droite)),
            "Index_fin_droite": pad(np.array(idx_fin_droite)),
            "Index_debut_gauche": pad(np.array(idx_debut_gauche)),
            "Index_fin_gauche": pad(np.array(idx_fin_gauche)),
        }

        df = pd.DataFrame(df)

        options = QtWidgets.QFileDialog.Options()
        file_name, _ = QtWidgets.QFileDialog.getSaveFileName(
            self,
            "Enregistrer les données complètes",
            "",
            "CSV Files (*.csv)",
            options=options,
        )

        if file_name:
            try:
                df.to_csv(file_name, index=False)
                QtWidgets.QMessageBox.information(
                    self, "Succès", "Données enregistrées avec succès."
                )
            except Exception as e:
                QtWidgets.QMessageBox.critical(
                    self, "Erreur", f"Erreur lors de l'enregistrement : {e}"
                )

    def update_mass(self, mass):
        self.subject_mass = mass
        QtWidgets.QMessageBox.information(self, "Masse enregistrée", f"{mass} kg")


    def compute_mean_emg(self):
        vg = [y for (_, y) in self.points_gauche_brute]
        vd = [y for (_, y) in self.points_droite_brute]
        if not vg or not vd:
            QtWidgets.QMessageBox.warning(
                self,
                "Pas de points",
                "Il n'y a pas encore de points bruts calculés pour la moyenne.",
            )
            return None, None

        if len(vg)>10 and len(vd)>10:
            vg = vg[-10:]
            vd = vd[-10:]

        mean_left = float(np.mean(vg))
        mean_right = float(np.mean(vd))

        return mean_left, mean_right

    def closeEvent(self, event):
        for w in [
            self.worker1,
            self.worker2,
            self.worker_vert_gauche,
            self.worker_vert_droite,
        ]:
            w.stop()
            w.wait(1000)
        super().closeEvent(event)
