#!/usr/bin/env python3
import os
os.system("clear")
import numpy as np
#import IPython.display as ipd
from scipy.signal import find_peaks
from utils_midi import exportar_melodia_a_midi
from utils_coder import generar_clave_compas, crear_melodia, imprimir_melodia
from utils_audio import convertir_midi_a_wav
from utils_decoder import cargar_audio, calcular_energia, detectar_frecs, obtener_melodia, buscar_compases, decode


def banner():
    print('''     
___  ___     _           _       _____ _             
|  \/  |    | |         | |     /  ___| |            
| .  . | ___| | ___   __| |_   _\ `--.| |_ ___  __ _ 
| |\/| |/ _ \ |/ _ \ / _` | | | |`--. \ __/ _ \/ _` |
| |  | |  __/ | (_) | (_| | |_| /\__/ / ||  __/ (_| |
\_|  |_/\___|_|\___/ \__,_|\__, \____/ \__\___|\__, |
                            __/ |               __/ |
                           |___/               |___/                                                                          
Hide messages using audio                                                     
    ''')

def main():
    banner()
    #example msg--> mensaje = "hey you!"
    msj = input("Escribe el mensaje: ")


    clave, compases = generar_clave_compas(msj)
    a, b = clave
    print(f"\nClave generada: a = {a}, b = {b}, compases = {compases}\n")

    melodia_codificada = crear_melodia(msj, clave, compases)
    #imprimir_melodia(melodia_codificada)


    exportar_melodia_a_midi(melodia_codificada, bpm=60, instrumento=0)

    convertir_midi_a_wav("mensaje.mid", "mensaje.wav", "/usr/share/sounds/sf2/FluidR3_GM.sf2")




# ==== RECEPTOR funcionalidad
    print("- RECEPTOR -")
    a = int(input("Introduce clave 'a': "))
    b = int(input("Introduce clave 'b': "))
    compases = int(input("Introduce el total de compases: "))
    clave_receptor = (a, b)

    
    # cargar el wav
    #ruta = "mensaje.wav"
    ruta = input("Introduce la ruta del archivo .wav recibido: ").strip()

    y, sr, audio = cargar_audio(ruta)

    energia, tiempos = calcular_energia(audio, sr)

    
    # buscar frecuencias
    picos, _ = find_peaks(energia, height=np.max(energia)*0.3, distance=int(0.4 / 0.01))
    frecs_encontradas = detectar_frecs(audio, picos, duracion_nota=0.7, tasa_muestreo=sr)

    # obtener la melodia
    melodia_detectada = obtener_melodia(frecs_encontradas)

    compases_detectados = buscar_compases(picos, paso=int(0.01 * sr), tasa_muestreo=sr, duracion_nota=0.7)

    # decodificar
    msj_decodificado = decode(clave_receptor, compases, compases_detectados, melodia_detectada)
    print(f"Mensaje decodificado: {msj_decodificado}")

if __name__ == "__main__":
    main()