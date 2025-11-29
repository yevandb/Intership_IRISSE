from PyQt5 import QtWidgets, QtCore


class ControlWindow(QtWidgets.QWidget):
    def __init__(self, fenetre_emg):
        super().__init__()
        self.fenetre_emg = fenetre_emg
        self.setWindowTitle("Control Window")
        self.resize(1000, 150)

        layout = QtWidgets.QVBoxLayout(self)

        layout.setAlignment(QtCore.Qt.AlignTop)

        layout_boutons = QtWidgets.QHBoxLayout()
        layout.addLayout(layout_boutons)
        layout_c1 = QtWidgets.QVBoxLayout()
        layout_c2 = QtWidgets.QVBoxLayout()
        layout_boutons.addLayout(layout_c1, 1)
        layout_boutons.addLayout(layout_c2, 1)

        # Start
        self.start_button = QtWidgets.QPushButton("Start", self)
        self.start_button.clicked.connect(self.start)
        layout_c1.addWidget(self.start_button)

        # Slider Consigne
        self.slider_label = QtWidgets.QLabel(
            f"Consigne ±{int(self.fenetre_emg.consigne * 100)}%", self
        )
        self.slider_label.setAlignment(QtCore.Qt.AlignCenter)
        self.slider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.slider.setRange(5, 50)
        self.slider.setValue(int(self.fenetre_emg.consigne * 100))
        self.slider.setTickInterval(5)
        self.slider.setTickPosition(QtWidgets.QSlider.TicksBelow)
        self.slider.setSizePolicy(
            QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed
        )
        self.slider.valueChanged.connect(self.consigne)
        slider_layout = QtWidgets.QVBoxLayout()
        slider_layout.addWidget(self.slider_label)
        slider_layout.addWidget(self.slider)
        layout_c1.addLayout(slider_layout)

        self.tolerance = 0.1
        # slider tolerance
        self.slider_label_tole = QtWidgets.QLabel(
            f"Tolérance ±{int(self.tolerance * 100)}%", self
        )
        self.slider_label_tole.setAlignment(QtCore.Qt.AlignCenter)
        self.slider_tole = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.slider_tole.setRange(1, 30)
        self.slider_tole.setValue(int(self.tolerance * 100))
        self.slider_tole.setTickInterval(1)
        self.slider_tole.setTickPosition(QtWidgets.QSlider.TicksBelow)
        self.slider_tole.setSizePolicy(
            QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed
        )
        self.slider_tole.valueChanged.connect(self.tolerance_f)
        slider_layout_tole = QtWidgets.QVBoxLayout()
        slider_layout_tole.addWidget(self.slider_label_tole)
        slider_layout_tole.addWidget(self.slider_tole)
        layout_c1.addLayout(slider_layout_tole)

        # Enregistrer
        self.save_button = QtWidgets.QPushButton("Enregistrer", self)
        self.save_button.clicked.connect(self.save_buffers)
        layout_c2.addWidget(self.save_button)

        # Moyenne EMG
        layout_moyenne = QtWidgets.QHBoxLayout()
        self.mean_button = QtWidgets.QPushButton("Moyenne EMG", self)
        self.mean_button.clicked.connect(self.compute_mean_emg)
        layout_moyenne.addWidget(self.mean_button)
        self.mean_label_g = QtWidgets.QLabel("Gauche : --", self)
        layout_moyenne.addWidget(self.mean_label_g)
        self.mean_label_d = QtWidgets.QLabel("Droite  : --", self)
        layout_moyenne.addWidget(self.mean_label_d)
        layout_c2.addLayout(layout_moyenne)

        # Masse du sujet
        mass_layout = QtWidgets.QHBoxLayout()
        self.mass_input = QtWidgets.QLineEdit(self)
        self.mass_input.setPlaceholderText("Entrez la masse")
        self.set_mass_button = QtWidgets.QPushButton("Valider", self)
        self.set_mass_button.clicked.connect(self.mass)
        mass_layout.addWidget(QtWidgets.QLabel("Masse du sujet (kg) :", self))
        mass_layout.addWidget(self.mass_input)
        mass_layout.addWidget(self.set_mass_button)
        layout_c2.addLayout(mass_layout)

        # Seuil gauche
        seuil_g_layout = QtWidgets.QHBoxLayout()
        self.seuil_g_input = QtWidgets.QLineEdit(self)
        self.seuil_g_input.setPlaceholderText("Entrez le seuil")
        self.set_seuil_gauche_button = QtWidgets.QPushButton("Valider", self)
        self.set_seuil_gauche_button.clicked.connect(
            lambda: self.seuil("gauche", self.seuil_g_input)
        )
        seuil_g_layout.addWidget(QtWidgets.QLabel("Seuil jambe gauche", self))
        seuil_g_layout.addWidget(self.seuil_g_input)
        seuil_g_layout.addWidget(self.set_seuil_gauche_button)
        layout_c1.addLayout(seuil_g_layout)

        # Seuil droite
        seuil_d_layout = QtWidgets.QHBoxLayout()
        self.seuil_d_input = QtWidgets.QLineEdit(self)
        self.seuil_d_input.setPlaceholderText("Entrez le seuil")
        self.set_seuil_droite_button = QtWidgets.QPushButton("Valider", self)
        self.set_seuil_droite_button.clicked.connect(
            lambda: self.seuil("droite", self.seuil_d_input)
        )
        seuil_d_layout.addWidget(QtWidgets.QLabel("Seuil jambe droite", self))
        seuil_d_layout.addWidget(self.seuil_d_input)
        seuil_d_layout.addWidget(self.set_seuil_droite_button)
        layout_c2.addLayout(seuil_d_layout)

        #  Boutons conditions
        layout_conditions = QtWidgets.QHBoxLayout()

        self.button_condition_0 = QtWidgets.QPushButton("Condition 0%", self)
        self.button_condition_minus = QtWidgets.QPushButton(f"Condition -{self.fenetre_emg.consigne*100}%", self)
        self.button_condition_plus = QtWidgets.QPushButton(f"Condition +{self.fenetre_emg.consigne*100}%", self)

        self.button_condition_0.clicked.connect(lambda: self.set_condition("0"))
        self.button_condition_minus.clicked.connect(lambda: self.set_condition("-"))
        self.button_condition_plus.clicked.connect(lambda: self.set_condition("+"))

        layout_conditions.addWidget(self.button_condition_0)
        layout_conditions.addWidget(self.button_condition_minus)
        layout_conditions.addWidget(self.button_condition_plus)
        layout.addLayout(layout_conditions)

        self.threshold_prev_gauche=0
        self.threshold_prev_droite=0

    def set_condition(self, condition):
        seuil_g_base=self.fenetre_emg.threshold_gauche
        seuil_d_base=self.fenetre_emg.threshold_droite
        x= self.tolerance

        if condition == "0":
            self.fenetre_emg.hline_gauche_max.setValue(self.fenetre_emg.threshold_gauche * (1 + x))
            self.fenetre_emg.hline_gauche_min.setValue(self.fenetre_emg.threshold_gauche*(1-x))
            self.fenetre_emg.hline_droite_max.setValue(self.fenetre_emg.threshold_droite*(1+x))
            self.fenetre_emg.hline_droite_min.setValue(self.fenetre_emg.threshold_droite*(1-x))
            self.threshold_prev_gauche=self.fenetre_emg.threshold_gauche
            self.threshold_prev_droite=self.fenetre_emg.threshold_droite

        elif condition == "-":
            seuil_g_base = (1-self.fenetre_emg.consigne) * self.fenetre_emg.threshold_gauche
            seuil_d_base = (1-self.fenetre_emg.consigne) * self.fenetre_emg.threshold_droite

        elif condition == "+":
            seuil_g_base = (1+self.fenetre_emg.consigne) * self.fenetre_emg.threshold_gauche
            seuil_d_base = (1+self.fenetre_emg.consigne) * self.fenetre_emg.threshold_droite

        self.fenetre_emg.hline_gauche_max.setValue(seuil_g_base * (1 + x))
        self.fenetre_emg.hline_gauche_min.setValue(seuil_g_base * (1 - x))
        self.fenetre_emg.hline_droite_max.setValue(seuil_d_base * (1 + x))
        self.fenetre_emg.hline_droite_min.setValue(seuil_d_base * (1 - x))

        self.threshold_prev_gauche = seuil_g_base
        self.threshold_prev_droite = seuil_d_base

    def start(self):
        self.fenetre_emg.start_acquisition()
        self.start_button.setEnabled(False)

    def consigne(self, value):
        self.fenetre_emg.consigne = value / 100.0
        self.slider_label.setText(f"Consigne ±{value}%")
        self.button_condition_minus.setText(f"Condition –{value}%")
        self.button_condition_plus.setText(f"Condition +{value}%")

    def tolerance_f(self,value):
        self.tolerance=value/100.0
        self.slider_label_tole.setText(f"Tolérance ±{value}%")
        self.fenetre_emg.hline_gauche_max.setValue(self.threshold_prev_gauche * (1 + self.tolerance))
        self.fenetre_emg.hline_gauche_min.setValue(self.threshold_prev_gauche* (1 - self.tolerance))
        self.fenetre_emg.hline_droite_max.setValue(self.threshold_prev_droite* (1 + self.tolerance))
        self.fenetre_emg.hline_droite_min.setValue(self.threshold_prev_droite* (1 - self.tolerance))

    def save_buffers(self):
        self.fenetre_emg.save_buffers()

    def compute_mean_emg(self):
        left, right = self.fenetre_emg.compute_mean_emg()
        self.mean_label_g.setText(f"Gauche : {left:.2f}")
        self.mean_label_d.setText(f"Droite  : {right:.2f}")

    def mass(self):
        try:
            m = float(self.mass_input.text())
            if m <= 0:
                raise ValueError
            self.fenetre_emg.update_mass(m)
        except ValueError:
            QtWidgets.QMessageBox.warning(self, "Erreur", "Masse invalide")

    def seuil(self, side, widget):
        try:
            s = float(widget.text())
            if s <= 0:
                raise ValueError
            if side == "gauche":
                self.fenetre_emg.threshold_gauche = s
            else:
                self.fenetre_emg.threshold_droite = s
        except ValueError:
            QtWidgets.QMessageBox.warning(self, "Erreur", "Seuil invalide")
