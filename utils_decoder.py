from scipy.fft import rfft, rfftfreq
from scipy.signal import find_peaks
from scipy.io import wavfile
from utils_coder import FREQS
import numpy as np
import librosa
import wave # for .wav format
import os
os.system("clear")

#ignorar las firmas 

#load the file
#file = wave.open("mensaje.wav", "r") # rb = read binary

#def cargar_audio(ruta_archivo):
# Leer archivo WAV usando scipy
tasa_muestreo, datos = wavfile.read('mensaje.wav')

# Cargar el archivo con librosa para obtener la señal y la tasa de muestreo
y, sr = librosa.load('mensaje.wav', sr=None)

# Imprimir información sobre la canción
print(f"Canción cargada con sr: {sr} Hz, Duración: {len(y)/sr:.2f} s")

# Convertir a mono en caso de que sea estéreo
if len(datos.shape) == 2:  # caso de estéreo -> 1 canal
    datos = datos[:, 0]

# Normalizar los datos de audio
audio = datos / np.max(np.abs(datos))



#deteccion de audio
ventana = int(0.05 * tasa_muestreo)
paso = int(0.01 * tasa_muestreo)

# Calcular la energía en cada ventana
energia = [np.sum(audio[i:i+ventana]**2) for i in range(0, len(audio)-ventana, paso)]

# Calcular los tiempos correspondientes a cada punto de energía
tiempos = np.arange(len(energia)) * paso / tasa_muestreo




''' GRAFICOS'''

fft_dom = np.fft.rfft(y)  # FFT en y
freqs_vect = np.fft.rfftfreq(len(y), d=1/sr)  #-> vector con las frecs correspondientes

amplitudes = np.abs(fft_dom)

D = np.abs(librosa.stft(y))
D_db = librosa.amplitude_to_db(D, ref=np.max)#pasar amplitud a dB

duracion_nota = 0.7
tasa_muestreo = 44100
paso = int(0.01 * tasa_muestreo)  #desplazar entre frames


def frecuencia_a_indice(f, tolerancia=5.0):
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

def reconstruir_mensaje_desde_indices(indices_ordenados):
  #reordenar los idx
    def indices_a_char(i1, i2, i3):
        byte = (i1 << 6) | (i2 << 3) | i3
        return chr(byte)

    chars = []
    print(f"\nidx recibidos: {indices_ordenados}")

    for i in range(0, len(indices_ordenados), 3):
        grupo = indices_ordenados[i:i+3] #agrupo en 3
        if len(grupo) == 3:
            c = indices_a_char(*grupo)
            print(f"grupo {grupo} → '{c}'")
            chars.append(c)

    return "".join(chars)

picos, _ = find_peaks(energia, height=np.max(energia)*0.3, distance=int(0.4 / 0.01))
samples_nota = int(duracion_nota * tasa_muestreo)
frecuencias_encontradas = []

for pico in picos:
    inicio = pico * paso
    fin = inicio + samples_nota
    if fin > len(audio):
        continue
    segmento = audio[inicio:fin]
    señal = segmento * np.hanning(len(segmento)) # hann
    espectro = np.abs(rfft(señal))
    freqs = rfftfreq(len(señal), 1 / tasa_muestreo)
    freq_dominante = freqs[np.argmax(espectro)]
    frecuencias_encontradas.append(freq_dominante)



frecuencias_filtradas = [] #quitar las firmas
for f in frecuencias_encontradas:
    if abs(f) > 30 and abs(f ) > 30:
        frecuencias_filtradas.append(f)

''' mapeo los indices con las freqs encontradas'''
melodia_detectada = []
for f in frecuencias_filtradas:
    idx = frecuencia_a_indice(f)
    if idx is not None:
        melodia_detectada.append(idx)

print(melodia_detectada)


# Este bloque detecta el compás estimado por cada nota detectada
# Basado en su tiempo de aparición en el audio

# duracion_nota debe ser la misma que usaste al codificar (ej: 0.7 s)
compases_detectados = [
    int((pico * paso / tasa_muestreo) // duracion_nota)
    for pico in picos
]

# Verificación visual
print("Compases detectados desde los picos (por tiempo):", compases_detectados)

clave = (5, 104)  # 21 abril
compases = 27
a, b = clave
a_inv = inverso(a, compases)

melodia_con_i = []
for compas_detectado, idx in zip(compases_detectados, melodia_detectada):
    i_real = (a_inv * (compas_detectado - b)) % compases
    melodia_con_i.append((i_real, idx))
print(melodia_con_i)
# Ordenar por índice original
#melodia_con_i.sort()
indices_ordenados = [idx for _, idx in melodia_con_i]

# Reconstrucción
mensaje = reconstruir_mensaje_desde_indices(indices_ordenados)
print("mensaje decodificado:", mensaje)


# print("frame rate:", file.getframerate())  # 44100
# print("sample width:", file.getsampwidth()) # 2
# print("number of frames:", file.getnframes())
# print("parametros:", file.getparams())
# print("numero de canales:", file.getnchannels()) # 2

# duracion = file.getnframes()/ file.getframerate() # duracion audio en seg
# print("Duracion:", duracion)

# frames = file.readframes(-1)
# print("muestras:",len(frames))
