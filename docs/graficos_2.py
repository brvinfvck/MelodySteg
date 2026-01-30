import numpy as np  
import librosa
import librosa.display
import matplotlib.pyplot as plt

def fft(y, sr, archivo="fft.png"):

    fft_dom = np.fft.rfft(y)
    frecs_vect = np.fft.rfftfreq(len(y), d=1/sr)
    amplitudes = np.abs(fft_dom)

    plt.figure(figsize=(10, 6))
    plt.plot(frecs_vect, amplitudes)
    plt.title("FFT")
    plt.xlabel("Frec (Hz)")
    plt.ylabel("amplitud")
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(archivo)

    plt.close()
    return fft_dom, frecs_vect, amplitudes


def stft(y, sr, archivo="stft.png"):

    D = np.abs(librosa.stft(y))
    D_db = librosa.amplitude_to_db(D, ref=np.max)

    plt.figure(figsize=(10, 6))
    librosa.display.specshow(D_db, x_axis='time', y_axis='log', sr=sr)
    plt.colorbar(format="%+2.0f dB")
    plt.title("STFT")
    plt.tight_layout()
    plt.savefig(archivo)
    plt.close()

    return D_db

y, sr = librosa.load('mensaje.wav', sr=None)
fft(y, sr)
stft(y, sr)
