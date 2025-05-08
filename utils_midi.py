from mido import MidiFile, MidiTrack, Message, MetaMessage, bpm2tempo
from math import log2

def frecuencia_a_nota_midi(freq):
    """pasa una frecuencia en Hz al numero de nota MIDI mas cercana """
    return int(round(69 + 12 * log2(freq / 440.0)))  # 440 Hz = A4 = nota 69

def exportar_melodia_a_midi(melodia, nombre_archivo="mensaje.mid", bpm=60, instrumento=0):
    mid = MidiFile(ticks_per_beat=480)
    track = MidiTrack()
    mid.tracks.append(track)

    # Establecer instrumento e inicializar tempo
    track.append(Message('program_change', program=instrumento, time=0))
    track.append(MetaMessage('set_tempo', tempo=bpm2tempo(bpm), time=0))

    duracion_ticks = 480  # negra = 1 segundo si BPM = 60

    for i, freq, compas in melodia:
        nota_midi = frecuencia_a_nota_midi(freq)
        track.append(Message('note_on', note=nota_midi, velocity=64, time=0))
        track.append(Message('note_off', note=nota_midi, velocity=64, time=duracion_ticks))
        #print(f"[MIDI] nota {nota_midi} ({freq:.2f} Hz) añadida con duración {duracion_ticks} ticks")

    mid.save(nombre_archivo)
    #print(f"Archivo MIDI guardado como: {nombre_archivo}")

