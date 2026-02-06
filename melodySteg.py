#!p/usr/bin/env python3


import argparse
import os
import re
import sys

from utils.utils_coder import kdf_from_compases


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
    python melodySteg.py --modo emisor/receptor

Modo emisor:
    - Introduce un mensaje desde la terminal.
    - El programa codificará el mensaje y generará 'mensaje.wav'.
    - También generará 'claves.txt' con los parámetros: a,b y compás para decodificar.

Modo receptor:
    - Recibe el archivo .wav.
    - (a,b) se obtiene en background de dos formas:
        1) Derivándolo desde una contraseña (recomendado): usa --pw o escribe la contraseña cuando se pida.
        2) Leyéndolo desde un archivo (por defecto: claves.txt) si existe y NO se indicó --pw.
    - El numerador (tiempos por compás) se intenta inferir automáticamente desde el audio (o se toma de claves.txt si está).

Argumentos(modo receptor):
    --wav RUTA_WAV
    --pw CONTRASEÑA
    --claves RUTA_CLAVES   (por defecto: claves.txt)

Requisitos:
    - pip install -r requirements.txt y una soundfont

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
python melodySteg.py --help muestra guía de uso
                --modo emisor/receptor
    ''')


def cargar_claves_desde_archivo(ruta: str):
    try:
        with open(ruta, "r", encoding="utf-8") as f:
            contenido = f.read()
    except FileNotFoundError:
        return None

    patron = r"a\\s*->\\s*(\\d+).*?b\\s*->\\s*(\\d+).*?comp[aá]s\\s*->\\s*(\\d+)"
    match = re.search(patron, contenido, flags=re.IGNORECASE | re.DOTALL)
    if not match:
        return None

    a, b, numerador = (int(x) for x in match.groups())
    return (a, b), numerador


def emisor():
    from utils.utils_midi import exportar_melodia_a_midi
    from utils.utils_coder import (
        kdf,
        crear_melodia,
        imprimir_melodia,
        mel_con_padding,
        log_dispersion,
    )
    from utils.utils_audio import midi_a_wav

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

    # clave, compases = generar_clave_compas(entrada)
    clave, compases = kdf(pw, entrada)
    a, b = clave
    print(f"\n Clave generada: a->{a}, b->{b} y compases->{compases}\n")

    melodia = crear_melodia(entrada, clave, compases)
    mel_final = mel_con_padding(melodia, compases, clave, numerador)
    exportar_melodia_a_midi(mel_final, bpm=60, instrumento=instr)
    imprimir_melodia(melodia)

    midi_a_wav("mensaje.mid", "mensaje.wav",
               "/usr/share/sounds/sf2/FluidR3_GM.sf2")

    with open("claves.txt", "w") as f:
        f.write(f"\n Clave generada: a->{a}, b->{b}, compás->{numerador}\n")

    print("Archivos creados: mensaje.wav y claves.txt")
    log_dispersion(entrada, melodia, mel_final)


def receptor(wav_path=None, claves_path="claves.txt", pw=None, numerador=None):
    from utils.utils_decoder import (
        cargar_audio,
        onsets_y_frecs,
        inferir_numerador_y_compases,
        decode,
    )

    print("- Parámetros para decodificar el mensaje -")

    clave = None

    if not wav_path:
        if os.path.exists("mensaje.wav"):
            wav_path = "mensaje.wav"
            print("Usando archivo por defecto: mensaje.wav")
        else:
            wav_path = input("Ruta del archivo .wav: ").strip()

    # Se intenta cargar el numerador desde claves.txt (si existe).
    # (a,b) solo se toma del archivo cuando NO se indicó contraseña.
    if claves_path and os.path.exists(claves_path):
        cargado = cargar_claves_desde_archivo(claves_path)
        if cargado:
            clave_archivo, numerador_archivo = cargado
            if numerador is None:
                numerador = numerador_archivo
            if pw is None:
                clave = clave_archivo
                a, b = clave
                print(
                    f"Usando claves desde '{claves_path}': a={a}, b={b}, compás={numerador}")
            else:
                print(
                    f"Usando compás desde '{claves_path}': compás={numerador}")

    y, sr, audio = cargar_audio(wav_path)

    onsets, frecs = onsets_y_frecs(audio, sr)

    compases = None
    if numerador is None:
        numerador_inf, compases_inf = inferir_numerador_y_compases(onsets, sr)
        if numerador_inf is not None:
            numerador = numerador_inf
            compases = compases_inf
            print(f"Numerador inferido automáticamente: {numerador}")

    if numerador is None:
        numerador = 4
        print("No se pudo obtener el numerador; usando 4 por defecto.")

    # limitar compases a lo realmente disponible en el wav (por robustez)
    compases_max = len(onsets) // numerador
    if compases is None or compases > compases_max:
        compases = compases_max

    #     # buscar las frecuencias
    # energia, _ = calcular_energia(audio, sr)
    # picos, _  = find_peaks(energia, height=np.max(energia)*0.3, distance=int(0.4/0.01))
    # frecs = detectar_frecs(audio, picos, duracion_nota=0.7, tasa_muestreo=sr)
    # melodia=obtener_melodia(frecs)

    # compases_encontrados= buscar_compases(picos, paso=int(0.01*sr), tasa_muestreo=sr, duracion_nota=0.7)
    # compases = len(compases_encontrados)

    if clave is None:
        if pw is None:
            pw = input("Escribe la contraseña: ").strip()
        clave = kdf_from_compases(pw, compases)

    msj_final = decode(clave, compases, onsets, frecs, numerador)
    print(f"Mensaje decodificado: {msj_final}")


def main():
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument('--modo', choices=['emisor', 'receptor'])
    parser.add_argument('--help', action='store_true')
    parser.add_argument(
        '--wav', help="Ruta del archivo .wav  (modo receptor).")
    parser.add_argument('--claves', default="claves.txt",
                        help="Ruta del archivo con a,b y compás (por defecto: claves.txt).")
    parser.add_argument(
        '--pw', help="Contraseña para derivar (a,b) automáticamente (modo receptor).")
    args = parser.parse_args()

    banner()

    if args.help:
        help()
        return

    # si se elige el modo directamente:
    if args.modo:
        if args.modo == 'emisor':
            emisor()
        elif args.modo == 'receptor':
            receptor(wav_path=args.wav, claves_path=args.claves,
                     pw=args.pw)
        return

    while True:
        modo = input(
            "\nSelecciona un modo para continuar (emisor/receptor) o 'salir': ").strip().lower()

        if modo == 'emisor':
            emisor()
            break
        elif modo == 'receptor':
            receptor(wav_path=args.wav, claves_path=args.claves,
                     pw=args.pw)
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
