import numpy as np
from scipy.signal import butter, iirnotch, lfilter, lfilter_zi


class Filter:
    def __init__(
        self,
        fs,
        f_notch=50,
        q_notch=30,
        low_bp=20,
        high_bp=400,
        order_bp=2,
        cutoff_env=5,
        order_env=4,
        cut_off_pb=20,
        order_pb=4,
    ):
        # Notch 50 Hz
        self.b_notch, self.a_notch = iirnotch(f_notch, q_notch, fs)
        self.zi_notch = lfilter_zi(self.b_notch, self.a_notch) * 0.0

        # Band-pass 20–400 Hz
        nyq = fs / 2
        bp_norm = [low_bp / nyq, high_bp / nyq]
        self.b_bp, self.a_bp = butter(order_bp, bp_norm, btype="band")
        self.zi_bp = lfilter_zi(self.b_bp, self.a_bp) * 0.0

        # Passe-bas pour enveloppe (5 Hz)
        env_norm = cutoff_env / nyq
        self.b_env, self.a_env = butter(order_env, env_norm, btype="low")
        self.zi_env = lfilter_zi(self.b_env, self.a_env) * 0.0

        # passe bas butter worth 4th order 20 Hz
        pb_norm = cut_off_pb / nyq
        self.b_pb, self.a_pb = butter(order_pb, pb_norm, btype="low")
        self.zi_pb_grf = lfilter_zi(self.b_pb, self.a_pb) * 0.0

    def process_block_emg(self, signal):

        s_notch, self.zi_notch = lfilter(
            self.b_notch, self.a_notch, signal, zi=self.zi_notch
        )

        s_bp, self.zi_bp = lfilter(self.b_bp, self.a_bp, s_notch, zi=self.zi_bp)

        s_rect = np.abs(s_bp)

        # s_env, self.zi_env = lfilter(self.b_env, self.a_env, s_rect, zi=self.zi_env)

        return s_rect

    def process_block_ap_grf(self, signal):

        s_pb, self.zi_pb_grf = lfilter(self.b_pb, self.a_pb, signal, zi=self.zi_pb_grf)

        return s_pb
