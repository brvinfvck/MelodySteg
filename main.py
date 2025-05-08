import os
os.system("clear")

import IPython.display as ipd
from utils_midi import exportar_melodia_a_midi
from utils_coder import generar_clave_y_compases, generar_melodia_con_mensaje, mostrar_melodia_en_texto
from utils_audio import convertir_midi_a_wav

def main():
    mensaje = "hola"
    clave, compases = generar_clave_y_compases(mensaje)
    melodia_codificada = generar_melodia_con_mensaje(mensaje, clave, compases)
    mostrar_melodia_en_texto(melodia_codificada)

    exportar_melodia_a_midi(melodia_codificada, bpm=60, instrumento=0)

    convertir_midi_a_wav("mensaje.mid", "mensaje.wav", "/usr/share/sounds/sf2/FluidR3_GM.sf2")
    ipd.Audio("mensaje.wav")
    #files.download("mensaje.wav")

if __name__ == "__main__":
    main()