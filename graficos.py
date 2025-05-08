def calcular_fft(y, sr):
    fft_dom = np.fft.rfft(y)
    freqs_vect = np.fft.rfftfreq(len(y), d=1/sr)
    amplitudes = np.abs(fft_dom)
    return fft_dom, freqs_vect, amplitudes


def calcular_stft(y):
    D = np.abs(librosa.stft(y))
    D_db = librosa.amplitude_to_db(D, ref=np.max)
    return D_db



''' GRAFICOS'''

# fft_dom = np.fft.rfft(y)  # FFT en y
# freqs_vect = np.fft.rfftfreq(len(y), d=1/sr)  #-> vector con las frecs correspondientes

# amplitudes = np.abs(fft_dom)

# D = np.abs(librosa.stft(y))
# D_db = librosa.amplitude_to_db(D, ref=np.max)#pasar amplitud a dB

# duracion_nota = 0.7
# tasa_muestreo = 44100
# paso = int(0.01 * tasa_muestreo)  #desplazar entre frames