from scipy.fft import rfft, rfftfreq
from scipy.io import wavfile
from util.coder import FREQS
import numpy as np
import librosa
from util.coder import beat_random, ACORDES

# file = wave.open("mensaje.wav", "r") # rb = read binary

min_freq = 20e3
max_freq = -1

for a in ACORDES:
    for f in ACORDES[a]:
        min_freq = min(min_freq, f)
        max_freq = max(max_freq, f)

def cargar_audio(ruta_archivo):
    sr, datos = wavfile.read(ruta_archivo)
    # y, sr = librosa.load(ruta_archivo, sr=None)
    print(f"archivo subido con sr: {sr} Hz,\nduracion: {len(datos)/sr:.2f} s")

    if len(datos.shape) == 2:
        datos = datos[:, 0]

    raw = datos.astype(np.float32) / np.max(np.abs(datos))  # normalizar los datos

    # TODO Band pass filter
    fft = np.fft.fft(raw)

    # Freq 
    smin = int(min_freq * 0 * fft.size / sr) 
    smax = int(max_freq * 16 * fft.size / sr) 
    filtered = fft.copy()
    filtered[:smin] = 0
    filtered[smax:] = 0

    # import matplotlib.pyplot as plt
    # plt.plot(fft)
    # plt.plot(filtered)
    # plt.show()
    audio = np.fft.ifft(filtered).real.astype(np.float32)

    wavfile.write('test.wav', sr, audio)

    return sr, audio.astype(np.float32)


# FUNCIONES DECODIFICACION
'''def calcular_energia(audio, tasa_muestreo): 
    ventana = int(0.05 * tasa_muestreo)
    paso = int(0.01 * tasa_muestreo)

    energia = [np.sum(audio[i:i+ventana]**2) for i in range(0, len(audio)-ventana, paso)] # energia en cada 'ventana'
    tiempos = np.arange(len(energia)) * paso / tasa_muestreo
    return energia, tiempos # tiempos correspondientes a cada punto de energía
'''


def frec_a_indx(f, tolerancia=5.0):
    dif = np.abs(FREQS - f)
    indice = np.argmin(dif)

    if dif[indice] <= tolerancia:  # si encuentra frec...
        return indice
    else:
        return None


def inverso(a, m):
    # buscar el 'i' con el q se codificó la nota original
    for x in range(1, m):
        if (a * x) % m == 1:
            return x
    raise ValueError(f"no se encontró el inverso mod")


# TODO Nueva estrategia de depósito y comparación?
def recuperar_msg_con_indx(indx_ordenados):
  # reordenar los idx
    def indices_a_char(i1, i2, i3):
        byte = (i1 << 6) | (i2 << 3) | i3
        return chr(byte)

    chars = []
    # print(f"\nidx recibidos: {indx_ordenados}")

    for i in range(0, len(indx_ordenados), 3):
        grupo = indx_ordenados[i:i+3]  # agrupo en 3
        if len(grupo) == 3:
            c = indices_a_char(*grupo)
            print(f"grupo {grupo} → '{c}'")
            chars.append(c)

    return "".join(chars)


# funcion para encontrar onsets y extraer frec dominante

def onsets_y_frecs(audio, sr, muestra=0.25):

    y_librosa = librosa.util.normalize(audio)
    onsets = librosa.onset.onset_detect(
        y=y_librosa, sr=sr, units='samples', backtrack=False)

    frecs_encontradas = []
    for onset in onsets:  # por cada nota, extrae la frec
        inicio = int(onset)
        fin = int(onset + muestra * sr)
        segmento = audio[inicio:fin]
        fft = np.abs(np.fft.rfft(segmento))
        freqs = np.fft.rfftfreq(segmento.size, 1 / sr)
        fdom = freqs[np.argmax(fft)]
        # fft.sample to freq
        fdom = np.argmax(fft) * sr / segmento.size
        
        frecs_encontradas.append(fdom)

    return onsets, frecs_encontradas


def decode(clave, compases, onsets, frecs_encontradas, numerador):
    
    a, b = clave
    a_inv = inverso(a, compases)

    orden = np.argsort(onsets)
    # onsets_ord = np.array(onsets)[orden][:compases * numerador]
    # se guardan las frec necesarias
    frecs_ord = np.array(frecs_encontradas)[orden][:compases*numerador]

    idx_msj = []

    for c in range(compases):

        segmento = frecs_ord[c*numerador: (c+1)*numerador]

        i_original = (a_inv * (c-b)) % compases
        beat_msj = beat_random(
            i_original, clave, numerador)  # posicion nota_msj
        f_msj = segmento[beat_msj]
        idx = frec_a_indx(f_msj)
        if idx is not None:
            idx_msj.append((i_original, idx))

    idx_msj.sort(key=lambda x: x[0])
    indx_ordenados = [idx for (_, idx) in idx_msj]  # solo indx de la frec_msj

    return recuperar_msg_con_indx(indx_ordenados)


'''
def buscar_frecs(audio, picos, duracion_nota, tasa_muestreo):
    # busca las frec dominantes 
    samples_nota = int(duracion_nota * tasa_muestreo)
    frecs_encontradas = []

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
        frecs_encontradas.append(freq_dominante)

    return frecs_encontradas

def obtener_melodia(frecs_encontradas):
    frecs_filtradas = [] 
    for f in frecs_encontradas:
        if abs(f ) > 30:
            frecs_filtradas.append(f)

    melodia_detectada = []

    for f in frecs_filtradas:
        idx = frec_a_indx(f) # mapeo los indices con las freqs encontradas

        if idx is not None:
            melodia_detectada.append(idx)

    return melodia_detectada

# Este bloque detecta el compás estimado por cada nota detectada
# Basado en su tiempo de aparición en el audio

# duración_nota debe ser la misma que se usó al codificar (0.7 s)
def buscar_compases(picos, paso, tasa_muestreo, duracion_nota):
    compases_detectados = []
    for pico in picos:
        pico_a_seg = (pico *paso)/tasa_muestreo
        compas = int(pico_a_seg // duracion_nota)
        compases_detectados.append(compas)
    
    return compases_detectados


# print("compases detectados desde los picos : ", compases_detectados)
'''
# print("frame rate:", file.getframerate())  # 44100
# print("sample width:", file.getsampwidth()) # 2
# print("number of frames:", file.getnframes())
# print("parametros:", file.getparams())
# print("numero de canales:", file.getnchannels()) # 2

# duracion = file.getnframes()/ file.getframerate() # duracion audio en seg
# print("Duracion:", duracion)

# frames = file.readframes(-1)
# print("muestras:",len(frames))
