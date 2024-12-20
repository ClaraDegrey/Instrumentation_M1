import pyvisa
import time

def test_and_measure_signal():
    # Initialisation du gestionnaire de ressources PyVISA
    rm = pyvisa.ResourceManager()

    # Lister les instruments disponibles
    print("Instruments disponibles :", rm.list_resources())

    # Adresse USB de l'oscilloscope (à ajuster si nécessaire)
    oscilloscope_address = 'USB0::6833::1230::DS1ZA192712222::0::INSTR'

    try:
        # Connexion à l'oscilloscope
        instrument = rm.open_resource(oscilloscope_address)
        instrument.timeout = 20000  # Timeout en millisecondes
        time.sleep(1)

        # Identification de l'appareil
        instrument.write("*IDN?")
        print("Instrument identifié :", instrument.read().strip())

        # Activer la courbe des canaux 1 et 2
        for channel in [1, 2]:
            instrument.write(f":CHANnel{channel}:DISPlay ON")
            print(f"Canal {channel} activé.")

        # Définir l'échelle verticale du canal 1 à 2V/div
        instrument.write(":CHAN1:SCALe 2")
        print("Échelle verticale du canal 2 définie à 2V/div.")

        # Définir l'échelle verticale du canal 2 à 2V/div
        instrument.write(":CHAN2:SCALe 2")
        print("Échelle verticale du canal 2 définie à 2V/div.")

        # Définir l'échelle horizontale à 500 µs/div (500 microsecondes par division)
        instrument.write(":TIMebase:SCALe 10E-6")
        print("Échelle horizontale définie à 500 µs/div.")


        # Mesurer les échelles verticales des canaux
        for channel in [1, 2]:
            instrument.write(f":CHANnel{channel}:SCALe?")
            scale = instrument.read()
            print(f"Échelle verticale du canal {channel} : {scale.strip()} V/div")

        # Mesurer l'échelle horizontale (temps par division)
        instrument.write(":TIMebase:SCALe?")
        time_scale = instrument.read()
        print(f"Échelle horizontale : {time_scale.strip()} s/div")

        # Mesurer la fréquence et l'amplitude crête à crête sur CH1 et CH2
        for channel in [1, 2]:
            instrument.write(f":MEASure:FREQuency? CHAN{channel}")
            frequency = instrument.read()
            print(f"Fréquence mesurée sur CH{channel} : {frequency.strip()} Hz")

            instrument.write(f":MEASure:VPP? CHAN{channel}")
            amplitude = instrument.read()
            print(f"Amplitude crête à crête mesurée sur CH{channel} : {amplitude.strip()} V")

        # Mesurer le déphasage entre CH1 et CH2
        try:
            instrument.write(":MEASure:ITEM RPHase,CHANnel1,CHANnel2")
            time.sleep(1)  # Pause pour la mesure
            instrument.write(":MEASure:ITEM? RPHase,CHANnel1,CHANnel2")
            phase_diff = instrument.read()
            print(f"Déphasage mesuré entre CH1 et CH2 : {float(phase_diff):.2f} degrés")
        except Exception as e:
            print("Erreur lors de la mesure du déphasage :", e)

    except pyvisa.errors.VisaIOError as e:
        print("Erreur de communication VISA :", e)
    except Exception as e:
        print("Erreur inattendue :", e)
    finally:
        # Fermer la connexion
        if 'instrument' in locals():
            instrument.close()
            print("Connexion fermée.")

# Appeler la fonction pour tester et mesurer
test_and_measure_signal()
