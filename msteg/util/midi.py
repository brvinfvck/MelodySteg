from mido import MidiFile, MidiTrack, Message, MetaMessage, bpm2tempo
from math import log2


def frec_a_midi(frec):
    # convertir una frecuencia a la nota midi mas cercana
    return int(round(69 + 12 * log2(frec / 440.0)))  # 440 Hz = A4 = nota 69

# https://en.wikipedia.org/wiki/General_MIDI
def exportar_melodia_a_midi(melodia, nombre_archivo="mensaje.mid", bpm=60, instrumento=1, signature=(4,4)):

    numerador = signature[0]

    TPB = 480
    NEGRA = int(TPB / signature[1])
    CORCHEA = int(NEGRA/2)


    mid = MidiFile(ticks_per_beat=TPB)  # cuenta interna en negras

    track = MidiTrack()
    cover = MidiTrack()
    
    mid.tracks.append(track)
    mid.tracks.append(cover)

    track.append(Message('program_change', program=instrumento, channel=0))
    cover.append(Message('program_change', program=instrumento, channel=1))

    track.append(MetaMessage('set_tempo', tempo=bpm2tempo(bpm), time=0))    # TODO Set tempo using time_signature
    cover.append(MetaMessage('set_tempo', tempo=bpm2tempo(bpm), time=0))

    # ordenar por num_compas y beat_compas ordenados
    mel_orden = sorted(melodia, key=lambda x: (x[0], x[1]))

    for (compas, beat, frec, es_msj) in mel_orden:
        nota_midi = frec_a_midi(frec)
        # FIXME No debería ir la duración en función del compás, bpm y/0 ticks_per_beat?
        if es_msj:
            duration_ticks = NEGRA  # nota de msj negra corta (~0.5s a 60 bpm)
            velocity = 60
        else:
            duration_ticks = NEGRA  # corchea corta (~0.25s a 60 bpm)
            velocity = 70

        # Primera nota de cada compás
        if (beat == 0):
            # Las cover graves meten armónicos (en frecuencias más altas)
            # por lo tanto, para separar, debemos meter el mensaje en
            # las frecuencias más bajas
            nota_cover = frec_a_midi(frec*16)
            cover.append(Message('note_on', note=nota_cover,
                        velocity=70, time=0))
            print(compas)
            cover.append(Message('note_off', note=nota_cover,
                        velocity=30, time=numerador*NEGRA))  
            # # TODO No sé meter silencios (:
            # cover.append(Message('note_on', note=0,
            #             velocity=0, time=0))
            # cover.append(Message('note_off', note=0,
            #             velocity=0, time=CORCHEA))

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
