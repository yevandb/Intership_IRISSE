import sys
from PyQt5.QtWidgets import QApplication
from interface import FenetreEMG
import treadmill_remote
from interface_vitesse import fenetre_vitesse
from control_window import ControlWindow


if __name__ == "__main__":
    app = QApplication(sys.argv)

    # Interface tapis roulant
    estimator = treadmill_remote.StateEstimator()
    controller = treadmill_remote.LQGController()
    gui_treadmill = treadmill_remote.TreadmillAIInterface(estimator, controller)
    gui_treadmill.show()

    # Interface EMG
    fenetre_emg = FenetreEMG()
    fenetre_emg.show()

    # Interface controle
    ctrl=ControlWindow(fenetre_emg)
    ctrl.show()

    # Interface vitesse
    vitesse=fenetre_vitesse()
    vitesse.show()

    sys.exit(app.exec_())


