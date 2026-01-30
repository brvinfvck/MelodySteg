#!p/usr/bin/env python3


import argparse
import sys
import numpy as np
# import IPython.display as ipd

from scipy.signal import find_peaks
from util.midi import exportar_melodia_a_midi
from util.coder import kdf, crear_melodia, imprimir_melodia, mel_con_padding, log_dispersion, gen_compases_from_m, gen_compases_from_c
from util.audio import midi_a_wav
from util.decoder import cargar_audio, onsets_y_frecs, decode


# funcion para validar clave del receptor
def validar_entrada(entrada):
    while True:
        respuesta = input(entrada).strip()
        if respuesta.lower() == "salir":
            print("Saliendo de la aplicación...")
            sys.exit(0)
        if respuesta.isdigit():
            return int(respuesta)
        print("Entrada no válida, debe ser un entero.")


def help():
    print("""

Uso:
    python3 main.py --modo emisor/receptor

Modo emisor:
    - Introduce un mensaje desde la terminal.
    - El programa codificará el mensaje y generará 'mensaje.wav'.
    - También generará 'clave_para_receptor.txt' con los parámetros: clave(a,b) para decodificar.

Modo receptor:
    - Recibe el archivo 'mensaje.wav' y 'clave_para_receptor.txt'.
    - El programa pedirá que ingreses los valores de clave y selecciones el .WAV para decodificar el mensaje.

Requisitos:
    - Python 3
    - Instalar dependencias: pip install -r requirements.txt y una soundfont

""")


def banner():
    print(r'''     
___  ___     _           _       _____ _             
|  \/  |    | |         | |     /  ___| |            
| .  . | ___| | ___   __| |_   _\ `--.| |_ ___  __ _ 
| |\/| |/ _ \ |/ _ \ / _` | | | |`--. \ __/ _ \/ _` |
| |  | |  __/ | (_) | (_| | |_| /\__/ / ||  __/ (_| |
\_|  |_/\___|_|\___/ \__,_|\__, \____/ \__\___|\__, |
                            __/ |               __/ |
                           |___/               |___/                                                                          
Hide messages using audio   
python3 main.py --help muestra guía de uso
                --modo emisor/receptor
    ''')


def emisor_main(output="mensaje.wav"):
    entrada = input("Escribe el mensaje a codificar: ")
    pw = input("Escribe una contraseña: ")

    print("\nElige un instrumento (0-127)")
    print("0  - Piano")
    print("46 - Guitarra acústica")  # no si >3 char

    instr = int(input("escribe el número del instrumento: "))
    if not 0 <= instr <= 127:
        print("entrada no válida, se usará Piano (0) por defecto")
        instr = 0

    compas = input("Escribe el compás (p.ej. 4/4): ").strip()
    try:
        numerador = int(compas.split('/')[0])
    except:
        print("Formato de compás no válido. Usando 4/4 por defecto.")
        numerador = 4

    emisor(entrada, pw, instr, numerador, output=output)

def emisor(entrada, pw, instr, numerador, output="mensaje.wav"):

    # clave, compases = generar_clave_compas(entrada)
    compases = gen_compases_from_m(entrada, numerador)
    a,b = kdf(pw, compases)
    
    print(f"\n Clave generada: a->{a}, b->{b} y compases->{compases}\n")

    melodia = crear_melodia(entrada, (a,b), compases)
    mel_final = mel_con_padding(melodia, compases, (a,b), numerador)
    exportar_melodia_a_midi(mel_final, bpm=60, instrumento=instr)
    imprimir_melodia(melodia)

    midi_a_wav("mensaje.mid", output,
               "/usr/share/sounds/sf2/FluidR3_GM.sf2")

    # with open("claves.txt", "w") as f:
    #     f.write(f"\n Clave generada: a->{a}, b->{b}, compás->{numerador}\n")

    print(f"Archivos creados: {output}")
    log_dispersion(entrada, melodia, mel_final)


def receptor_main(ruta="mensaje.wav"):
    print("- Clave para decodificar el mensaje -")
    pw = input("Escribe una contraseña: ")
    numerador = validar_entrada("Tiempos por compás: ")
    receptor(pw, numerador, ruta)

def receptor(pw, numerador, ruta="mensaje.wav"):
    y, sr, audio = cargar_audio(ruta)
    onsets, frecs = onsets_y_frecs(audio, sr)

    compases = gen_compases_from_c(onsets, numerador)
    clave = kdf(pw, compases)
    #     # buscar las frecuencias
    # energia, _ = calcular_energia(audio, sr)
    # picos, _  = find_peaks(energia, height=np.max(energia)*0.3, distance=int(0.4/0.01))
    # frecs = detectar_frecs(audio, picos, duracion_nota=0.7, tasa_muestreo=sr)
    # melodia=obtener_melodia(frecs)

    # compases_encontrados= buscar_compases(picos, paso=int(0.01*sr), tasa_muestreo=sr, duracion_nota=0.7)
    # compases = len(compases_encontrados)

    msj_final = decode(clave, compases, onsets, frecs, numerador)
    print(f"Mensaje decodificado: {msj_final}")

def main():
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument('--modo', choices=['emisor', 'receptor'])
    parser.add_argument('--f', type=str, help='Archivo de salida para el emisor o de entrada para el receptor', default='mensaje.wav')
    parser.add_argument('--help', action='store_true')
    args = parser.parse_args()

    banner()

    if args.help:
        help()

    if args.f is None:
        f = input("Ruta del archivo .wav: ").strip()
    else:
        f = args.f

    # si se elige el modo directamente:
    if args.modo:
        if args.modo == 'emisor':
            emisor_main(output=f)
        elif args.modo == 'receptor':
            receptor_main(ruta=f)
        return


    while True:

        modo = input(
            "\nSelecciona un modo para continuar (emisor/receptor) o 'salir': ").strip().lower()

        if modo == 'emisor':
            emisor_main(output=f)
            break
        elif modo == 'receptor':
            receptor_main(ruta=f)
            break
        elif modo == "salir":
            print("Saliendo de la aplicación...")
            sys.exit(0)
        else:
            print("Entrada no válida. Escribe si eres 'emisor/receptor' o 'salir'. ")


if __name__ == "__main__":
    main()


#   print("3  - Piano eléctrico")
#   print("35 - Tuba")
#   print("42 - Viola")
