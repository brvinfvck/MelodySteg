#!/usr/bin/env python3
import os
os.system("clear")
import numpy as np
#import IPython.display as ipd
from scipy.signal import find_peaks
from utils_midi import exportar_melodia_a_midi
from utils_coder import generar_clave_y_compases, generar_melodia_con_mensaje, mostrar_melodia_en_texto
from utils_audio import convertir_midi_a_wav
from utils_decoder import cargar_audio, calcular_energia,  detectar_frecuencias, obtener_melodia, calcular_compases, decodificar_mensaje

def titulo():
    print("=" * 60)
    print("🎵 MelodySteg - Oculta y revela mensajes en melodías 🎵".center(60))
    print("=" * 60)


def main():
    titulo()
    #mensaje = "hey you!"
    mensaje = input("Escribe el mensaje: ")


    clave, compases = generar_clave_y_compases(mensaje)
    a, b = clave
    print(f"\nClave generada para el receptor: a = {a}, b = {b}, compases = {compases}\n")

    melodia_codificada = generar_melodia_con_mensaje(mensaje, clave, compases)
    #mostrar_melodia_en_texto(melodia_codificada)


    exportar_melodia_a_midi(melodia_codificada, bpm=60, instrumento=0)

    convertir_midi_a_wav("mensaje.mid", "mensaje.wav", "/usr/share/sounds/sf2/FluidR3_GM.sf2")
    #ipd.Audio("mensaje.wav")



#---------------------------------------------------- receptor

    print("=== RECEPTOR ===")
    a = int(input("Introduce la clave 'a': "))
    b = int(input("Introduce la clave 'b': "))
    compases = int(input("Introduce el número total de compases: "))
    clave_receptor = (a, b)

    
    # Cargar el archivo de audio
    #ruta = "mensaje.wav"
    ruta = input("Introduce la ruta del archivo .wav recibido: ").strip()

    y, sr, audio = cargar_audio(ruta)

    # Calcular la energía de la señal
    energia, tiempos = calcular_energia(audio, sr)

    
    # Detectar las frecuencias dominantes
    picos, _ = find_peaks(energia, height=np.max(energia)*0.3, distance=int(0.4 / 0.01))
    frecuencias_encontradas = detectar_frecuencias(audio, picos, duracion_nota=0.7, tasa_muestreo=sr)

    # Obtener la melodía detectada
    melodia_detectada = obtener_melodia(frecuencias_encontradas)

    compases_detectados = calcular_compases(picos, paso=int(0.01 * sr), tasa_muestreo=sr, duracion_nota=0.7)

    # Decodificar el mensaje
    mensaje_decodificado = decodificar_mensaje(clave_receptor, compases, compases_detectados, melodia_detectada)
    print(f"Mensaje decodificado: {mensaje_decodificado}")

if __name__ == "__main__":
    main()