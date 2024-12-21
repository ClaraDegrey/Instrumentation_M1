import customtkinter
from tkinter import messagebox

# Définir le thème de couleur par défaut
customtkinter.set_default_color_theme("dark-blue")

# Fonction pour envoyer les commandes au générateur de fonction (simulateur ici)
def send_command():
    signal_type = signal_var.get()
    frequency = frequency_entry.get()
    frequency_unit = frequency_unit_var.get()
    amplitude = amplitude_value_entry.get()
    amplitude_unit = amplitude_unit_var.get()
    offset = offset_value_entry.get()
    offset_unit = offset_unit_var.get()

    # Convertir la fréquence et l'amplitude en valeurs numériques pour vérification
    try:
        frequency = float(frequency)
        amplitude = float(amplitude)
    except ValueError:
        messagebox.showerror("Erreur", "La fréquence et l'amplitude doivent être des nombres valides.")
        return

    # Vérification des valeurs de fréquence
    if frequency_unit == "Hz" and not (0.1 <= frequency <= 100000000):  # 100 MHz en Hz
        messagebox.showerror("Erreur", "Veuillez sélectionner une fréquence entre 0.1Hz et 100MHz.")
        return
    elif frequency_unit == "kHz" and not (0.1 <= frequency * 1000 <= 100000000):  # 100 MHz en kHz
        messagebox.showerror("Erreur", "Veuillez sélectionner une fréquence entre 0.1Hz et 100MHz.")
        return
    elif frequency_unit == "MHz" and not (0.1 <= frequency * 1000000 <= 100000000):  # 100 MHz en MHz
        messagebox.showerror("Erreur", "Veuillez sélectionner une fréquence entre 0.1Hz et 100MHz.")
        return

    # Vérification des valeurs d'amplitude
    if amplitude_unit == "V" and not (0.01 <= amplitude <= 15):  # Amplitude en V
        messagebox.showerror("Erreur", "Veuillez sélectionner une amplitude entre 0.01V et 15V.")
        return
    elif amplitude_unit == "mV" and not (0.01 <= amplitude / 1000 <= 15):  # Amplitude en mV
        messagebox.showerror("Erreur", "Veuillez sélectionner une amplitude entre 0.01V et 15V.")
        return

    # Si les vérifications passent, envoyer la commande
    command = f"Signal: {signal_type}, Frequency: {frequency} {frequency_unit}, Amplitude: {amplitude} {amplitude_unit}, Offset: {offset} {offset_unit}"
    
    messagebox.showinfo("Command Sent", command)
    print(command)

# Fonction pour enregistrer et afficher la configuration dans le terminal
def configure():
    signal_type = signal_var.get()
    frequency = frequency_entry.get()
    frequency_unit = frequency_unit_var.get()
    amplitude = amplitude_value_entry.get()
    amplitude_unit = amplitude_unit_var.get()
    offset = offset_value_entry.get()
    offset_unit = offset_unit_var.get()

    # Enregistrer la configuration
    config = {
        "Signal Type": signal_type,
        "Frequency": f"{frequency} {frequency_unit}",
        "Amplitude": f"{amplitude} {amplitude_unit}",
        "Offset": f"{offset} {offset_unit}"
    }

    # Afficher la configuration dans le terminal
    print("\nConfiguration Saved:")
    for key, value in config.items():
        print(f"{key}: {value}")

    messagebox.showinfo("Configuration Saved", "Your configuration has been saved successfully.")

# Création de l'application principale
app = customtkinter.CTk()
app.title("GBF Rigol Control Panel")

# Titre
label_title = customtkinter.CTkLabel(app, text="GBF Rigol Control", font=("Helvetica", 24, "bold"))

label_title.pack(pady=20)

# Création du cadre principal pour organiser les éléments
main_frame = customtkinter.CTkFrame(app)
main_frame.pack(fill="both", expand=True, padx=20, pady=10)

# Créer un cadre pour le sélecteur de signal (gauche)
signal_frame = customtkinter.CTkFrame(main_frame)
signal_frame.grid(row=0, column=0, padx=10, pady=5, sticky="n")

# Menu déroulant pour choisir le type de signal
signal_var = customtkinter.StringVar(value="Sinus")  # Valeur par défaut
signal_menu = customtkinter.CTkOptionMenu(signal_frame, variable=signal_var, values=["Sinus", "Square", "Ramp", "Pulse", "Noise", "Arb"])
signal_menu.pack(padx=20, pady=10)

# Créer un cadre pour la fréquence, l'amplitude et l'offset (droite)
right_frame = customtkinter.CTkFrame(main_frame)
right_frame.grid(row=0, column=1, padx=20, pady=10, sticky="n")

# Fréquence
label_frequency = customtkinter.CTkLabel(right_frame, text="Frequency:")
label_frequency.grid(row=0, column=0, padx=10, pady=5)

frequency_entry = customtkinter.CTkEntry(right_frame)
frequency_entry.insert(0, "100")  # Valeur par défaut : 100
frequency_entry.grid(row=0, column=1, padx=10, pady=5)

# Menu déroulant pour sélectionner les unités de fréquence (Hz, kHz, MHz)
frequency_unit_var = customtkinter.StringVar(value="Hz")
frequency_unit_menu = customtkinter.CTkOptionMenu(right_frame, variable=frequency_unit_var, values=["Hz", "kHz", "MHz"])
frequency_unit_menu.grid(row=0, column=2, padx=10, pady=5)

# Amplitude
label_amplitude = customtkinter.CTkLabel(right_frame, text="Amplitude:")
label_amplitude.grid(row=1, column=0, padx=10, pady=5)

amplitude_value_entry = customtkinter.CTkEntry(right_frame)
amplitude_value_entry.insert(0, "5")  # Valeur par défaut : 5
amplitude_value_entry.grid(row=1, column=1, padx=10, pady=5)

# Menu déroulant pour l'unité d'amplitude (V, mV)
amplitude_unit_var = customtkinter.StringVar(value="V")
amplitude_unit_menu = customtkinter.CTkOptionMenu(right_frame, variable=amplitude_unit_var, values=["V", "mV"])
amplitude_unit_menu.grid(row=1, column=2, padx=10, pady=5)

# Offset
label_offset = customtkinter.CTkLabel(right_frame, text="Offset:")
label_offset.grid(row=2, column=0, padx=10, pady=5)

offset_value_entry = customtkinter.CTkEntry(right_frame)
offset_value_entry.insert(0, "0")  # Valeur par défaut : 0
offset_value_entry.grid(row=2, column=1, padx=10, pady=5)

# Menu déroulant pour l'unité d'offset (V, mV)
offset_unit_var = customtkinter.StringVar(value="V")
offset_unit_menu = customtkinter.CTkOptionMenu(right_frame, variable=offset_unit_var, values=["V", "mV"])
offset_unit_menu.grid(row=2, column=2, padx=10, pady=5)

# Créer un cadre pour le bouton d'envoi
button_frame = customtkinter.CTkFrame(app)
button_frame.pack(pady=20)

# Bouton pour envoyer la commande
send_button = customtkinter.CTkButton(button_frame, text="Send Command", command=send_command)
send_button.pack()

# Lancer l'application
app.mainloop()
