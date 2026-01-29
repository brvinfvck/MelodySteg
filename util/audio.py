import subprocess
import os

def midi_a_wav(nombre_midi="mensaje.mid", nombre_wav="mensaje.wav", soundfont="/usr/share/sounds/sf2/FluidR3_GM.sf2", gain=10.0):
    comando = [
        "fluidsynth",
        "-ni",
        soundfont,
        nombre_midi,
        "-F",
        nombre_wav,
        "-r",
        "44100",
        "-g", str(gain)
    ]
    with open(os.devnull, 'w') as devnull:
        subprocess.run(comando, stdout=devnull, stderr=devnull)

    print(f"Archivo WAV generado: {nombre_wav}")