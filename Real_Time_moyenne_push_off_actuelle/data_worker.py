from PyQt5.QtCore import QThread
import asyncio
import queue
import numpy as np
from scipy.interpolate import interp1d

from qualisys_data_receiver import connecter_qualisys, get_emg_frame
from traitement_emg import Filter


class DataWorker(QThread):

    def __init__(
        self,
        index_emg,
        index_ap,
        get_emg,
        data_emg=queue.Queue(),
        data_ap=queue.Queue(),
        ip="127.0.0.1",
    ):
        super().__init__()
        self.data_emg = data_emg
        self.data_ap = data_ap
        self.get_emg = get_emg
        self.ip = ip
        self.index_emg = index_emg
        self.index_ap = index_ap
        self.running = True
        self.emg_filter = None
        self.target_period = 0.1

    def stop(self):
        self.running = False

    def run(self):

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        try:
            connection = loop.run_until_complete(connecter_qualisys(self.ip))
        except Exception as e:
            print(f"Impossible de se connecter à QTM : {e}")
            return

        while self.running:

            try:
                frame_brute_emg, frame_brute_grf = loop.run_until_complete(
                    get_emg_frame(connection, self.index_emg, self.index_ap)
                )
                if frame_brute_emg is None and frame_brute_grf:
                    continue
                fs_analog = 1000
                if self.emg_filter is None:
                    self.emg_filter = Filter(fs=fs_analog)
                    # print(f"[DEBUG] EMGFilter, fs={fs_analog} Hz")

                # GRF
                n_input = len(frame_brute_grf)
                n_target = 100

                if n_input < 2:
                    continue

                x_old = np.linspace(0, 1, n_input)
                x_new = np.linspace(0, 1, n_target)

                interpolator = interp1d(x_old, frame_brute_grf, kind="linear")
                frame_interp = interpolator(x_new)
                data_grf = self.forward_fill(frame_interp)
                data_grf = self.emg_filter.process_block_ap_grf(data_grf)
                data_grf = self.forcer_taille(data_grf)
                self.data_ap.put(data_grf)

                # EMG
                if self.get_emg is True:
                    data_emg = self.forward_fill(frame_brute_emg)
                    data_emg = self.emg_filter.process_block_emg(data_emg)
                    data_emg = self.forcer_taille(data_emg)
                    self.data_emg.put(data_emg)

            except Exception as e:
                print(f" Erreur dans DataWorker : {e}")



        try:
            loop.run_until_complete(connection.disconnect())
            print("Déconnecté de QTM.")
        except:
            pass

        loop.close()

    @staticmethod
    def forcer_taille(data, taille_voulue=100):

        data = np.asarray(data)

        if len(data) > taille_voulue:
            return data[:taille_voulue]
        elif len(data) < taille_voulue:
            pad_len = taille_voulue - len(data)
            last = data[-1] if len(data) > 0 else 0
            return np.concatenate([data, np.full(pad_len, last)])  # complète
        else:
            return data

    @staticmethod
    def forward_fill(a):

        a = a.copy()
        mask = np.isnan(a)
        if mask.all():
            return a

        # 1) back-fill des NaN initiaux
        first_valid = np.flatnonzero(~mask)[0]
        a[:first_valid] = a[first_valid]

        # 2) forward-fill classique
        mask = np.isnan(a)
        idx = np.where(~mask, np.arange(a.size), 0)
        np.maximum.accumulate(idx, out=idx)
        return a[idx]
