from scipy.fft import rfft, rfftfreq
from scipy.signal import find_peaks
from scipy.io import wavfile
from utils_coder import FREQS
import numpy as np
import librosa
import wave # for .wav format
import os
os.system("clear")


#file = wave.open("mensaje.wav", "r") # rb = read binary
def cargar_audio(ruta_archivo):
    tasa_muestreo, datos = wavfile.read(ruta_archivo)
    y, sr = librosa.load(ruta_archivo, sr=None)
    print(f"archivo subido con sr: {sr} Hz,\nduracion: {len(y)/sr:.2f} s")

    if len(datos.shape) == 2:
        datos = datos[:, 0]
    audio = datos / np.max(np.abs(datos)) # normalizar los datos
    
    return y, sr, audio

def calcular_energia(audio, tasa_muestreo): 
    ventana = int(0.05 * tasa_muestreo)
    paso = int(0.01 * tasa_muestreo)

    energia = [np.sum(audio[i:i+ventana]**2) for i in range(0, len(audio)-ventana, paso)] # energia en cada 'ventana'
    tiempos = np.arange(len(energia)) * paso / tasa_muestreo
    return energia, tiempos # tiempos correspondientes a cada punto de energía


def frec_a_indx(f, tolerancia=5.0):
    dif = np.abs(FREQS - f)
    indice = np.argmin(dif)

    if dif[indice] <= tolerancia:#si encuentra freq
        return indice
    else:
        return None

def inverso(a, m):
#buscar el 'i' con el q se codifico la nota original
    for x in range(1, m):
        if (a * x) % m == 1:
            return x
    raise ValueError(f"no encontró el inverso mod")

def recuperar_msg_con_indx(indices_ordenados):
  #reordenar los idx
    def indices_a_char(i1, i2, i3):
        byte = (i1 << 6) | (i2 << 3) | i3
        return chr(byte)

    chars = []
    #print(f"\nidx recibidos: {indices_ordenados}")

    for i in range(0, len(indices_ordenados), 3):
        grupo = indices_ordenados[i:i+3] #agrupo en 3
        if len(grupo) == 3:
            c = indices_a_char(*grupo)
            print(f"grupo {grupo} → '{c}'")
            chars.append(c)

    return "".join(chars)


def detectar_frecs(audio, picos, duracion_nota, tasa_muestreo):
    # busca las frec dominantes en los picos de energía
    samples_nota = int(duracion_nota * tasa_muestreo)
    frecuencias_encontradas = []

    for pico in picos:
        inicio = pico * int(0.01 * tasa_muestreo)
        fin = inicio + samples_nota
        if fin > len(audio):
            continue
        segmento = audio[inicio:fin]
        señal = segmento * np.hanning(len(segmento))  # Hann ventana
        espectro = np.abs(rfft(señal))
        freqs = rfftfreq(len(señal), 1 / tasa_muestreo)
        freq_dominante = freqs[np.argmax(espectro)]
        frecuencias_encontradas.append(freq_dominante)

    return frecuencias_encontradas

def obtener_melodia(frecuencias_encontradas):
    frecuencias_filtradas = [] 
    for f in frecuencias_encontradas:
        if abs(f) > 30 and abs(f ) > 30:
            frecuencias_filtradas.append(f)

    melodia_detectada = []

    for f in frecuencias_filtradas:
        idx = frec_a_indx(f) # mapeo los indices con las freqs encontradas

        if idx is not None:
            melodia_detectada.append(idx)

    return melodia_detectada



# Este bloque detecta el compás estimado por cada nota detectada
# Basado en su tiempo de aparición en el audio

# duracion_nota debe ser la misma que usaste al codificar (ej: 0.7 s)
def buscar_compases(picos, paso, tasa_muestreo, duracion_nota):
    compases_detectados = [
        int((pico * paso / tasa_muestreo) // duracion_nota)
        for pico in picos
    ]
    return compases_detectados


# print("compases detectados desde los picos : ", compases_detectados)

def decode(clave, compases, compases_detectados, melodia_detectada):
    a, b = clave
    a_inv = inverso(a, compases)

    melodia_con_i = []
    for compas_detectado, idx in zip(compases_detectados, melodia_detectada):
        i_real = (a_inv * (compas_detectado - b)) % compases
        melodia_con_i.append((i_real, idx))
    # Ordenar por índice original
    #melodia_con_i.sort()
    indices_ordenados = [idx for _, idx in melodia_con_i]

    mensaje = recuperar_msg_con_indx(indices_ordenados) # recuperar msg
    return mensaje






# clave = (5, 104)  # 21 abril
# compases = 27
# a, b = clave
# a_inv = inverso(a, compases)


# print("frame rate:", file.getframerate())  # 44100
# print("sample width:", file.getsampwidth()) # 2
# print("number of frames:", file.getnframes())
# print("parametros:", file.getparams())
# print("numero de canales:", file.getnchannels()) # 2

# duracion = file.getnframes()/ file.getframerate() # duracion audio en seg
# print("Duracion:", duracion)

# frames = file.readframes(-1)
# print("muestras:",len(frames))
