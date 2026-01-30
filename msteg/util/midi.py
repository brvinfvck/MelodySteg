from mido import MidiFile, MidiTrack, Message, MetaMessage, bpm2tempo
from math import log2


def frec_a_midi(frec):
    # convertir una frecuencia a la nota midi mas cercana
    return int(round(69 + 12 * log2(frec / 440.0)))  # 440 Hz = A4 = nota 69


def exportar_melodia_a_midi(melodia, nombre_archivo="mensaje.mid", bpm=60, instrumento=0):

    mid = MidiFile(ticks_per_beat=480)  # cuenta interna en negras
    track = MidiTrack()
    mid.tracks.append(track)

    track.append(Message('program_change', program=instrumento, time=0))
    track.append(MetaMessage('set_tempo', tempo=bpm2tempo(bpm), time=0))

    # ordenar por num_compas y beat_compas ordenados
    mel_orden = sorted(melodia, key=lambda x: (x[0], x[1]))

    for (compas, beat, frec, es_msj) in mel_orden:
        nota_midi = frec_a_midi(frec)
        if es_msj:
            duration_ticks = 210  # nota de msj negra corta (~0.5s a 60 bpm)
            velocity = 60
        else:
            duration_ticks = 100  # corchea corta (~0.25s a 60 bpm)
            velocity = 70

        track.append(Message('note_on', note=nota_midi,
                     velocity=velocity, time=0))
        track.append(Message('note_off', note=nota_midi,
                     velocity=velocity, time=duration_ticks))

    # se añade un acorde d cierre en tónica
    cierre = [60, 64, 48]   # acorde cierre --> C4 E4 C3
    for nota in cierre:
        track.append(Message('note_on', note=nota, velocity=80, time=0))
    track.append(Message('note_off', note=cierre[0], velocity=70, time=240))
    track.append(Message('note_off', note=cierre[1], velocity=80, time=240))
    track.append(Message('note_off', note=cierre[2], velocity=80, time=240))

    mid.save(nombre_archivo)
    # print(f" midi guardado: {nombre_archivo}")
