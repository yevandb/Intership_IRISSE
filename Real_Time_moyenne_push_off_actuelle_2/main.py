import sys
from PyQt5.QtWidgets import QApplication
from interface import FenetreEMG
from control_window import ControlWindow

if __name__ == "__main__":
    app = QApplication(sys.argv)

    fenetre = FenetreEMG()
    fenetre.show()

    ctrl=ControlWindow(fenetre)
    ctrl.show()

    sys.exit(app.exec_())
