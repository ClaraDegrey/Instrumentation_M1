import tkinter as tk
from tkinter import ttk
import pyvisa  # Assurez-vous d'avoir pyvisa installé pour la gestion des instruments
import time
import numpy as np
import matplotlib
matplotlib.use('TkAgg')  # Utiliser TkAgg pour l'intégration Tkinter
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk

# Initialiser PyVISA Resource Manager
rm = pyvisa.ResourceManager("@py")
print("Instruments disponibles :", rm.list_resources())


class Etat(tk.Frame):
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        self.status_square = tk.Canvas(self, width=20, height=20, bg="red")  # Carré rouge
        self.status_square.grid(row=0, column=0, padx=5, pady=5)

    def set_status(self, connected):
        if connected:
            self.status_square.config(bg="green")
        else:
            self.status_square.config(bg="red")


class MyApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Interface Graphique - Diagrammes de Bode")
        self.geometry("1200x700")

        # Frame principale pour la configuration et les graphiques
        main_frame = tk.Frame(self)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Frame pour les paramètres (à gauche)
        param_frame = tk.Frame(main_frame, padx=10, pady=10, relief=tk.RAISED, borderwidth=2)
        param_frame.pack(side=tk.LEFT, fill=tk.Y)

        # Frame pour les paramètres de balayage
        balayage_frame = tk.Frame(param_frame, relief=tk.RAISED, borderwidth=2)
        balayage_frame.pack(pady=10, fill='x')

        # Titre pour le cadre de balayage
        ttk.Label(balayage_frame, text="Balayage par Intervalles", font=("Arial", 12, "bold")).pack(pady=5)

        # Fréquence Min
        freq_min_frame = tk.Frame(balayage_frame)
        freq_min_frame.pack(pady=5, fill='x')

        ttk.Label(freq_min_frame, text="Fréquence Min:").pack(side='left', padx=5)
        self.freq_min_entry = tk.Entry(freq_min_frame)
        self.freq_min_entry.pack(side='left', padx=5)
        self.freq_min_unit = ttk.Combobox(freq_min_frame, values=["Hz", "kHz", "MHz"], state="readonly")
        self.freq_min_unit.pack(side='left', padx=5)
        self.freq_min_unit.current(0)

        # Fréquence Max
        freq_max_frame = tk.Frame(balayage_frame)
        freq_max_frame.pack(pady=5, fill='x')

        ttk.Label(freq_max_frame, text="Fréquence Max:").pack(side='left', padx=5)
        self.freq_max_entry = tk.Entry(freq_max_frame)
        self.freq_max_entry.pack(side='left', padx=5)
        self.freq_max_unit = ttk.Combobox(freq_max_frame, values=["Hz", "kHz", "MHz"], state="readonly")
        self.freq_max_unit.pack(side='left', padx=5)
        self.freq_max_unit.current(0)

        # Nombre de Points
        num_points_frame = tk.Frame(balayage_frame)
        num_points_frame.pack(pady=5, fill='x')

        ttk.Label(num_points_frame, text="Nombre de Points:").pack(side='left', padx=5)
        self.num_points_entry = tk.Entry(num_points_frame)
        self.num_points_entry.pack(side='left', padx=5)

        # Bouton de démarrage de l'acquisition
        ttk.Button(balayage_frame, text="Démarrer l'Acquisition", command=self.start_acquisition).pack(pady=10, fill='x')

        # Frame pour les connexions
        connexion_frame = tk.Frame(param_frame, relief=tk.RAISED, borderwidth=2)
        connexion_frame.pack(pady=10, fill='x')

        # Titre pour le cadre des connexions
        ttk.Label(connexion_frame, text="Connexion", font=("Arial", 12, "bold")).pack(pady=5)

        # GBF : Bouton et état
        gbf_frame = tk.Frame(connexion_frame)
        gbf_frame.pack(pady=5, fill='x')

        ttk.Button(gbf_frame, text="Connecter au GBF", command=self.connect_gbf).pack(side='left', padx=5)
        self.status_gbf = Etat(gbf_frame)
        self.status_gbf.pack(side='right', padx=5)

        # Oscilloscope : Bouton et état
        osc_frame = tk.Frame(connexion_frame)
        osc_frame.pack(pady=5, fill='x')

        ttk.Button(osc_frame, text="Connecter à l'oscilloscope", command=self.connect_oscilloscope).pack(side='left', padx=5)
        self.status_oscilloscope = Etat(osc_frame)
        self.status_oscilloscope.pack(side='right', padx=5)

        # Instruments : Bouton et zone de texte
        instrument_frame = tk.Frame(connexion_frame)
        instrument_frame.pack(pady=5, fill='x')

        ttk.Button(instrument_frame, text="Lister les Instruments", command=self.list_instruments).pack(side='top', padx=5, pady=5)
        self.instrument_list = tk.Text(instrument_frame, height=5, width=40)
        self.instrument_list.pack(side='top', pady=5, fill='x')

        # Frame pour la barre de progression
        progress_frame = tk.Frame(param_frame, relief=tk.RAISED, borderwidth=2)
        progress_frame.pack(pady=10, fill='x')

        # Titre pour la barre de progression
        ttk.Label(progress_frame, text="Progression", font=("Arial", 12, "bold")).pack(pady=5)

        # Barre de progression
        self.progress_bar = ttk.Progressbar(progress_frame, orient="horizontal", mode="determinate", length=200)
        self.progress_bar.pack(pady=5)

        # Frame pour les graphiques (à droite)
        graph_frame = tk.Frame(main_frame)
        graph_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        # Création des figures Matplotlib
        figure = Figure(figsize=(8, 6), dpi=100)

        # Subplot pour le gain
        self.ax_gain = figure.add_subplot(211)
        self.ax_gain.set_title("Diagramme de Bode - Gain")
        self.ax_gain.set_xlabel("Fréquence (Hz)")
        self.ax_gain.set_ylabel("Gain (dB)")
        self.ax_gain.grid(True, which="both", linestyle="--", linewidth=0.5)

        # Subplot pour la phase
        self.ax_phase = figure.add_subplot(212)
        self.ax_phase.set_title("Diagramme de Bode - Phase")
        self.ax_phase.set_xlabel("Fréquence (Hz)")
        self.ax_phase.set_ylabel("Phase (degrés)")
        self.ax_phase.grid(True, which="both", linestyle="--", linewidth=0.5)

        # Ajustement des marges entre les sous-graphiques
        figure.tight_layout(pad=4.0)

        # Intégration des graphiques dans Tkinter
        self.canvas = FigureCanvasTkAgg(figure, master=graph_frame)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        # Ajout de la barre d'outils Matplotlib
        toolbar = NavigationToolbar2Tk(self.canvas, graph_frame)
        toolbar.update()
        toolbar.pack(side=tk.BOTTOM, fill=tk.X)

        self.geometry("1400x800")  # Taille adaptée pour tout afficher

        # Initialisation des états de connexion
        self.connected_gbf = False
        self.connected_oscilloscope = False

    def update_progress(self, step=1):
        # Met à jour la barre de progression
        self.progress_bar["value"] += step  # Incrémenter la valeur actuelle
        self.update_idletasks()  # Rafraîchir l'interface pour afficher les changements

    def connect_gbf(self):
        try:
            global gbf
            gbf = rm.open_resource("USB0::1024::2500::DG1D184250521\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00::0::INSTR")
            self.connected_gbf = True
        except:
            self.connected_gbf = False
        self.status_gbf.set_status(self.connected_gbf)

    def connect_oscilloscope(self):
        try:
            global oscilloscope
            oscilloscope = rm.open_resource('USB0::6833::1230::DS1ZA192712222::0::INSTR')
            self.connected_oscilloscope = True
        except:
            self.connected_oscilloscope = False
        self.status_oscilloscope.set_status(self.connected_oscilloscope)

    def list_instruments(self):
        # Liste tous les instruments connectés via PyVISA
        self.instrument_list.delete(1.0, tk.END)
        resources = rm.list_resources()
        for resource in resources:
            self.instrument_list.insert(tk.END, resource + "\n")

    def calculate_parameters(self):
        # Récupérer les valeurs et convertir les unités
        num_points_value = int(self.num_points_entry.get())
        
        if self.freq_min_unit.get() == "kHz":
            frequence_min_choix = int(self.freq_min_entry.get()) * 1000
        else:
            frequence_min_choix = int(self.freq_min_entry.get())
        
        if self.freq_max_unit.get() == "kHz":
            frequence_max_choix = int(self.freq_max_entry.get()) * 1000
        else:
            frequence_max_choix = int(self.freq_max_entry.get())
        
        # Retourner les valeurs calculées
        return num_points_value, frequence_min_choix, frequence_max_choix
        
        
    def start_acquisition(self):
        if not self.connect_gbf or not self.connected_oscilloscope:
            print("Veuillez d'abord établir les connexions aux instruments.")
            return
        
        # Acquérir les données (vous pouvez adapter la logique de l'acquisition ici)
        data = []
        function_form = "Sinus"
        amplitude = 5
        offset = 0

        num_points_value = int(self.num_points_entry.get())

        # Conversion de la fréquence minimale
        if self.freq_min_unit.get() == "kHz":
            frequence_min_choix = int(self.freq_min_entry.get()) * 1000
        else:
            frequence_min_choix = int(self.freq_min_entry.get())

        # Conversion de la fréquence maximale
        if self.freq_max_unit.get() == "kHz":
            frequence_max_choix = int(self.freq_max_entry.get()) * 1000
        else:
            frequence_max_choix = int(self.freq_max_entry.get())
        
        # Échelles de fréquence logaritmiques
        frequencies = np.logspace(np.log10(frequence_min_choix), np.log10(frequence_max_choix), num=num_points_value)

        self.progress_bar["maximum"] = num_points_value  # Configurer le nombre total de crans
        self.progress_bar["value"] = 0  # Réinitialiser la barre au début

        for frequency in frequencies:
            # Configurer le générateur de formes d'onde
            time_per_div = 0.5 / frequency  # 10 périodes visibles
            oscilloscope.write(f":TIMebase:SCALe {time_per_div:.6f}")  # Définir l'échelle horizontale
            time.sleep(1)
            oscilloscope.write(":CHAN1:SCALe 2") # Définir l'échelle verticale du canal 1 à 2V/div
            time.sleep(1)
            oscilloscope.write(":CHAN2:SCALe 2") # Définir l'échelle verticale du canal 2 à 2V/div
            time.sleep(1)

            self.configure_waveform(gbf, function_form, frequency, amplitude, offset)
            
            # Mesurer les données sur l'oscilloscope
            oscilloscope.write(":MEASure:VPP? CHAN1")
            amplitude_ch1 = oscilloscope.read().strip()

            oscilloscope.write(":MEASure:VPP? CHAN2")
            amplitude_ch2 = oscilloscope.read().strip()

            oscilloscope.write(":MEASure:ITEM RPHase,CHANnel2,CHANnel1")
            time.sleep(3)
            oscilloscope.write(":MEASure:ITEM? RPHase,CHANnel2,CHANnel1")
            phase_diff = oscilloscope.read().strip()

            data.append([frequency, amplitude_ch1, amplitude_ch2, phase_diff])

            # Mettre à jour la barre de progression
            self.update_progress(step=1)

        # Afficher les diagrammes de Bode
        self.plot_bode(data)



    def configure_waveform(self, instrument, function_form, frequency, amplitude, offset):
        if function_form == "Sinus":
            instrument.write("FUNCtion SIN")
        else:
            print("Forme d'onde non reconnue, utiliser Sinus.")
            return

        time.sleep(1)
        instrument.write(f"FREQ {frequency}")
        time.sleep(1)
        instrument.write(f"APPLy {function_form},{frequency},{amplitude},{offset}")
        time.sleep(1)
        instrument.write("OUTPut ON")
        time.sleep(1)

    def plot_bode(self, data):
        try:
            # Conversion des données en tableaux numpy
            frequencies = np.array([d[0] for d in data])
            amplitude_ch1 = np.array([float(d[1]) for d in data])
            amplitude_ch2 = np.array([float(d[2]) for d in data])
            phase_diff = np.array([float(d[3]) for d in data])

            # Calcul du gain en dB
            gain_dB = 20 * np.log10(amplitude_ch2 / amplitude_ch1)

            # Mise à jour du graphique pour le gain
            self.ax_gain.clear()
            self.ax_gain.semilogx(frequencies, gain_dB, marker='o', color='blue', label="Gain (dB)")
            self.ax_gain.set_title('Diagramme de Bode - Gain')
            self.ax_gain.set_xlabel('Fréquence (Hz)')
            self.ax_gain.set_ylabel('Gain (dB)')
            self.ax_gain.grid(True, which='both', linestyle='--', linewidth=0.5)
            self.ax_gain.legend(loc='upper left')

            # Mise à jour du graphique pour la phase
            self.ax_phase.clear()
            self.ax_phase.semilogx(frequencies, phase_diff, marker='x', color='red', label="Phase (°)")
            self.ax_phase.set_title('Diagramme de Bode - Phase')
            self.ax_phase.set_xlabel('Fréquence (Hz)')
            self.ax_phase.set_ylabel('Phase (degrés)')
            self.ax_phase.grid(True, which='both', linestyle='--', linewidth=0.5)
            self.ax_phase.legend(loc='upper left')

                # Dessiner les graphiques mis à jour
            self.canvas.draw()

        except Exception as e:
             print("Erreur lors de l'affichage des graphiques :", e)


if __name__ == "__main__":
    app = MyApp()
    app.mainloop()
