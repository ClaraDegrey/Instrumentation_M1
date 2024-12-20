import pyvisa
import time

# Initialiser PyVISA Resource Manager
rm = pyvisa.ResourceManager("@py")
# Lister les instruments connectés
print("Instruments disponibles :", rm.list_resources())

# Déclaration des variables globales
instrument = None  # Pour la connexion à l'instrument

# Fonction pour configurer la forme d'onde (sinusoïdal ou carré)
def configure_waveform(instrument, function_form, frequency, amplitude, offset):
    try:
        # Choisir la forme d'onde
        if function_form == "Sinus":
            instrument.write("FUNCtion SIN")  # Commande pour signal sinusoïdal
        elif function_form == "Square":
            instrument.write("FUNCtion SQU")  # Commande pour signal carré
        elif function_form == "Ramp":
            instrument.write("FUNCtion RAMP")  # Commande pour signal en rampe
        elif function_form == "Pulse":
            instrument.write("FUNCtion PULS")  # Commande pour signal pulsé
        elif function_form == "Noise":
            instrument.write("FUNCtion NOIS")  # Commande pour signal bruité
        elif function_form == "Arb":
            instrument.write("FUNCtion ARB")  # Commande pour signal arbitraire
        else:
            print("Forme d'onde non reconnue")
            return
        time.sleep(1)  # Attendre que la commande soit exécutée

        # Appliquer la fréquence explicitement (en cas de changement de fréquence)
        instrument.write(f"FREQ {frequency}")
        time.sleep(1)  # Attendre que la fréquence soit mise à jour

        # Appliquer l'amplitude et l'offset
        instrument.write(f"APPLy {function_form},{frequency},{amplitude},{offset}")
        time.sleep(1)

        # Activer la sortie
        instrument.write("OUTPut ON")
        time.sleep(1)

        print(f"Signal {function_form} configuré : {frequency} Hz, {amplitude} Vpp, offset {offset} V")
    except Exception as e:
        print("Erreur lors de la configuration du signal :", e)

# Fonction pour envoyer la commande avec des valeurs définies dans le code
def send_command():
    # Paramètres définis dans le code
    function_form = "Sinus"  # Type de signal (ex. Sinus, Square, etc.)
    frequency = 50000  # Fréquence en Hz
    amplitude = 5  # Amplitude en V
    offset = 0  # Offset en V

    # Vérifier si l'instrument est déjà connecté
    global instrument
    if instrument is None:
        try:
            instrument = rm.open_resource('USB0::1024::2500::DG1D184250521\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00::0::INSTR')
            print("Connecté à l'instrument")
        except Exception as e:
            print(f"Erreur lors de la connexion à l'instrument : {e}")
            return

    # Configurer le signal sur l'instrument
    configure_waveform(instrument, function_form, frequency, amplitude, offset)

    # Afficher un message avec la commande envoyée
    command = f"Signal: {function_form}, Frequency: {frequency} Hz, Amplitude: {amplitude} Vpp, Offset: {offset} V"
    print("Commande envoyée : ", command)

# Lancer la commande directement
send_command()
