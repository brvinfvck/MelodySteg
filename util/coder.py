import numpy as np
import random
from math import gcd
from typing import Tuple
from hashlib import pbkdf2_hmac

# Am pentatónica ampliada a 8 notas
FREQS = np.array([220.00, 261.63, 293.66, 329.63,
                 392.00, 440.00, 523.25, 587.33])
# FREQS = np.array([
#     220.00,  # A3
#     246.94,  # B3
#     261.63,  # C4
#     293.66,  # D4
#     329.63,  # E4
#     349.23,  # F4
#     392.00,  # G4
#     440.00,  # A4
# ])

# acordes en relativa Cmaj
ACORDES = {"C":  [261.63, 329.63, 392.00],   # C4, E4, G4
           "G":  [196.00, 246.94, 293.66],   # G3, B3, D4
           "Am": [220.00, 261.63, 329.63],   # A3, C4/(523.25 Hz), E4
           "F":  [174.61, 220.00, 130.81],   # F3, A3 (349.23 Hz), C3

           }
PROGRESION = [
    "C", "G", "Am", "F", "C"
    # "G", # I–V–vi–IV
    # "Am","F","C","G","Am","F","C","G","Am","F","C","G" #vi-IV-I-V (x3)
]


def kdf(pw, txt):
    compases = len(txt)*3
    v_aleatorio = b"melodia"
    key = pbkdf2_hmac('sha256', pw.encode(), v_aleatorio, 100_000, dklen=2)

    a = key[0] % compases  # genero 'a'
    while gcd(a, compases) != 1:
        a = (a+1) % compases or 1

    b = key[1]  # genero 'b'
    clave = (a, b)
    return clave, compases

# FUNCIONES DE CODIFICACION


def char_a_idx(c):
    byte = ord(c)
    indices = [(byte >> 6) & 0b111, (byte >> 3) & 0b111, byte & 0b111]
    # print(f"'{c}' -> byte: {byte} -> indices: {indices}")
    return indices


def txt_a_idx(texto):
    # print(f"codificando texto...: '{texto}'")
    indices = []
    for c in texto:
        indices.extend(char_a_idx(c))
    # print(f"indices: {indices}")
    return indices


def nota_en_compas(idx, clave, compases):
    a, b = clave
    compas = (idx * a + b) % compases
    # print(f"Nota idx {idx} -> compas: {compas}")
    return compas


def beat_random(i, clave, numerador):

    a, b = clave
    seed = (a * 1000 + b) * (i + 1)
    random.seed(seed)  # reinicia random
    return random.randint(0, numerador-1)


def crear_melodia(texto, clave, compases):
    indices = txt_a_idx(texto)
    melodia = []

    for i, idx in enumerate(indices):
        freq = float(FREQS[idx])
        compas = nota_en_compas(i, clave, compases)
        melodia.append((i, freq, compas))

    return melodia

# se unen melodia y notas de relleno


def mel_con_padding(melodia, compases, clave, numerador):

    nota_por_compas = {}
    for i, frec, compas in melodia:
        nota_por_compas[compas] = (i, frec)

    rdo = []

    for c in range(compases):
        i, frec_msj = nota_por_compas[c]
        n_acorde = PROGRESION[c % len(PROGRESION)]
        acorde = ACORDES[n_acorde]
        pos_msj = beat_random(i, clave, numerador)

        relleno_idx = 0

        for beat in range(numerador):
            if beat == pos_msj:
                # LOG:
                print(
                    f"compas {c}, beat {beat} → nota msj i={i}, frec={frec_msj:.2f} Hz")

                rdo.append((c, beat, frec_msj, True))
            else:
                frec_relleno = acorde[relleno_idx %
                                      len(acorde)]  # notas acorde en orden
                print(
                    f"compás {c}, beat {beat} → nota relleno i={i}, frec={frec_relleno:.2f} Hz")

                rdo.append((c, beat, float(frec_relleno), False))
                relleno_idx += 1
    return rdo


def imprimir_melodia(melodia):
    print("\n melodia generada:")
    print(f"{'nota en Hz':>10} | {'compas':>6}")
    print("-" * 22)
    for i, freq, compas in melodia:
        print(f"{freq:>10.2f} | {compas:>6}")

# LOG pruebas


def log_dispersion(texto, melodia, m_final):

    compas_a_beat = {
        comp: beat
        for (comp, beat, freq, es_msg) in m_final
        if es_msg
    }

    print("LOG DE DISPERSIÓN DE NOTAS:\n")
    for char_idx, c in enumerate(texto):
        i1, i2, i3 = 3*char_idx, 3*char_idx+1, 3*char_idx+2
        detalles = []
        for i, freq, compas in melodia:
            if i in (i1, i2, i3):
                beat = compas_a_beat.get(compas)
                detalles.append((i, compas, beat))
        print(f"'{c}':")
        for (i, comp, beat) in sorted(detalles, key=lambda x: x[0]):
            print(f" i={i} -- compas {comp}, beat {beat}")
        print()
