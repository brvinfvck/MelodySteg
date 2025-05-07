import subprocess

def convertir_midi_a_wav(nombre_midi="mensaje.mid", nombre_wav="mensaje.wav", soundfont="/usr/share/sounds/sf2/FluidR3_GM.sf2"):
    comando = [
        "fluidsynth",
        "-ni",
        soundfont,
        nombre_midi,
        "-F",
        nombre_wav,
        "-r",
        "44100"
    ]
    print(f" Ejecutando: {' '.join(comando)}")
    subprocess.run(comando)
    print(f"Archivo WAV generado: {nombre_wav}")