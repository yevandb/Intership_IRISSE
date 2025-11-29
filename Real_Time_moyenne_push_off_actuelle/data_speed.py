from PyQt5.QtCore import QThread
import asyncio
import queue
import numpy as np
from qualisys_data_receiver import connecter_qualisys, get_emg_frame


class Data_Speed(QThread):

    def __init__(
        self,
        data_vitesse=queue.Queue(),
        index_v=12,
        index_emg=0,
        ip="127.0.0.1",
    ):
        super().__init__()
        self.data_vitesse = data_vitesse
        self.index_v = index_v
        self.index_emg= index_emg
        self.ip = ip
        self.running = True
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
                frame_brute_emg,frame_brute_speed = loop.run_until_complete(
                    get_emg_frame(connection, self.index_emg, self.index_v)
                )
                if frame_brute_speed is None and frame_brute_emg:
                    continue

                # Vitesse
                data_speed= forward_fill(frame_brute_speed)
                self.data_vitesse.put(data_speed)

            except Exception as e:
                print(f" Erreur dans DataWorker : {e}")

        try:
            loop.run_until_complete(connection.disconnect())
            print("Déconnecté de QTM.")
        except:
            pass

        loop.close()


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
