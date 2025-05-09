import numpy as np  
from math import gcd
from typing import Tuple


# ==== FRECUENCIAS 
FREQS = np.array([261.63, 293.66, 329.63, 349.23, 392.00, 440.00, 493.88, 523.25])  # C4 a C5


# ==== GENERADOR DE CLAVE Y N COMPASES
def generar_clave_compas(texto: str) -> Tuple[Tuple[int, int], int]:
    notas_necesarias = len(texto) * 3
    compases = notas_necesarias
    posibles_a = [a for a in range(2, compases) if gcd(a, compases) == 1]

    if not posibles_a:
        raise ValueError(f"No se encontro ningun valor 'a' coprimo con {compases}.")

    a = posibles_a[0]
    b = ord(texto[0])  #valor ASCII del primer char del txto
    clave = (a, b)

    # print(f"\nClave generada: a = {a}, b = {b}")
    # print(f" Número de compases: {compases} (3 por char)")

    return clave, compases


# ==== FUNCIONES DE CODIFICACION 

def char_a_indices(c):
    byte = ord(c)
    indices = [(byte >> 6) & 0b111, (byte >> 3) & 0b111, byte & 0b111]
    #print(f"[char_a_indices] '{c}' -> byte: {byte:08b} -> indices: {indices}")
    return indices

def codificar_texto_a_indices(texto):
    #print(f"[codificar_texto_a_indices] codificando texto...: '{texto}'")
    indices = []
    for c in texto:
        indices.extend(char_a_indices(c))
    #print(f"[codificar_texto_a_indices] indices: {indices}")
    return indices

def nota_en_compas(idx, clave, compases):
    a, b = clave
    compas = (idx * a + b) % compases
    #print(f"[nota_en_compas] Nota idx {idx} -> Compás: {compas}")
    return compas

def crear_melodia(texto, clave, compases):
    #print(f"[generar_melodia_con_mensaje] generando melodía para: '{texto}' con clave {clave}")
    indices = codificar_texto_a_indices(texto)
    melodia = []

    for i, idx in enumerate(indices):
        freq = FREQS[idx]
        compas = nota_en_compas(i, clave, compases)
        melodia.append((i, freq, compas))
        #print(f"[generar_melodia_con_mensaje] i={i}, index={idx} -> freq={freq} Hz, compás={compas}")

    #print(f"[generar_melodia_con_mensaje] melodia creada con {len(melodia)} notas.")
    return melodia

# === VISUALIZAR 'PARTITURA'

def imprimir_melodia(melodia):
    print("\n melodia generada:")
    print(f"{'nota en Hz':>10} | {'compas':>6}")
    print("-" * 22)
    for i, freq, compas in melodia:
        print(f"{freq:>10.2f} | {compas:>6}")

