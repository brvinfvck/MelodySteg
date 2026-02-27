from mido import MidiFile, MidiTrack, Message, MetaMessage, bpm2tempo
from math import log2

PROGRESION = [
    "C", "G", "Am", "F", "C"
    # "G", # I–V–vi–IV
    # "Am","F","C","G","Am","F","C","G","Am","F","C","G" #vi-IV-I-V (x3)
]

# ACORDES = {"C":  [261.63, 329.63, 392.00],   # C4, E4, G4
#            "G":  [196.00, 246.94, 293.66],   # G3, B3, D4
#            "Am": [220.00, 261.63, 329.63],   # A3, C4/(523.25 Hz), E4
#            "F":  [174.61, 220.00, 130.81],   # F3, A3 (349.23 Hz), C3
#            }

# ACORDES = {
#     "C":  [130.81, 164.81, 196.00],
#     "G":  [98.00, 123.47, 146.83],
#     "Am": [110.00, 130.81, 164.81],
#     "F":  [87.31, 110.00, 65.41],
# }


def frec_a_midi(frec):
    # convertir una frecuencia a la nota midi mas cercana
    return int(round(69 + 12 * log2(frec / 440.0)))  # 440 Hz = A4 = nota 69


def _events_to_track(track: MidiTrack, events):
    # (t_abs, kind, note, vel) ; kind: "on"/"off"
    def key(e):
        t, kind, note, vel = e
        pri = 0 if kind == "off" else 1
        return (t, pri, note)

    events.sort(key=key)
    last_t = 0
    for (t, kind, note, vel) in events:
        delta = t - last_t
        if kind == "on":
            track.append(Message("note_on", note=note,
                         velocity=vel, time=delta))
        else:
            track.append(Message("note_off", note=note,
                         velocity=vel, time=delta))
        last_t = t


'''
def exportar_melodia_a_midi(  # EXPERIMENTO hasta 3 char
    melodia,
    nombre_archivo="mensaje.mid",
    bpm=60,
    instrumento=0,
    numerador=4,
    segunda_voz=True,
    instrumento_bajo=0,  # 32
    vel_bajo=45,
    step_div=2,          # 2=corchea (más rápido), 1=negra, 4=semi
    # stretch=2
):
    tpb = 480
    # step = (tpb * stretch) // step_div

    step = tpb // step_div  # tamaño de “celda”

    mid = MidiFile(ticks_per_beat=tpb)

    # TRACK 0: conductor
    conductor = MidiTrack()
    mid.tracks.append(conductor)
    conductor.append(MetaMessage("set_tempo", tempo=bpm2tempo(bpm), time=0))
    conductor.append(MetaMessage("time_signature",
                     numerator=numerador, denominator=4, time=0))

    mel_orden = sorted(melodia, key=lambda x: (x[0], x[1]))
    compases_tot = (max(c for (c, _, _, _) in mel_orden) +
                    1) if mel_orden else 0

    # TRACK 1: melodía
    track1 = MidiTrack()
    mid.tracks.append(track1)
    track1.append(Message("program_change", program=instrumento, time=0))

    events1 = []
    for (compas, beat, frec, es_msj) in mel_orden:
        nota = frec_a_midi(float(frec))
        t_abs = (compas * numerador + beat) * step

        if es_msj:
            dur = int(0.7 * step)
            vel = 60
        else:
            dur = int(0.55 * step)
            vel = 70

        events1.append((t_abs, "on", nota, vel))
        events1.append((t_abs + dur, "off", nota, vel))

    _events_to_track(track1, events1)

    # TRACK 2: bajo largo por compás
    if segunda_voz:
        track2 = MidiTrack()
        mid.tracks.append(track2)
        track2.append(Message("program_change",
                      program=instrumento_bajo, time=0))

        events2 = []
        for c in range(compases_tot):
            n_acorde = PROGRESION[c % len(PROGRESION)]
            acorde = ACORDES[n_acorde]

            frec_bajo = float(acorde[0]) / 2.0
            nota_bajo = frec_a_midi(frec_bajo)

            t_abs = (c * numerador) * step
            dur = numerador * step

            events2.append((t_abs, "on", nota_bajo, vel_bajo))
            events2.append((t_abs + dur, "off", nota_bajo, vel_bajo))

        _events_to_track(track2, events2)

    mid.save(nombre_archivo)
'''

'''
def exportar_melodia_a_midi(
    melodia,
    nombre_archivo="mensaje.mid",
    bpm=60,
    instrumento=0,
    numerador=4,
    segunda_voz=True,
    instrumento_bajo=0,
    dur_msg_beats=0.6,     # NUEVO: duración nota mensaje (en beats)
    dur_fill_beats=0.5,    # NUEVO: duración nota relleno (en beats)
    dur_bajo_beats=None    # NUEVO: duración bajo (None = compás entero)
):
    ticks_per_beat = 240
    mid = MidiFile(ticks_per_beat=ticks_per_beat)

    # --- Pista 1: melodía (mensaje + relleno) ---
    track1 = MidiTrack()
    mid.tracks.append(track1)
    track1.append(Message('program_change', program=instrumento, time=0))
    track1.append(MetaMessage('set_tempo', tempo=bpm2tempo(bpm), time=0))

    # ordenar por compás y beat
    mel_orden = sorted(melodia, key=lambda x: (x[0], x[1]))

    # Convertimos cada evento a (t_abs_ticks, nota_midi, dur_ticks, vel)
    eventos1 = []
    for (compas, beat, frec, es_msj) in mel_orden:
        nota_midi = frec_a_midi(float(frec))
        t_abs = (compas * numerador + beat) * ticks_per_beat

        if es_msj:
            # dur = 1 * ticks_per_beat      # 1 beat (negra)
            dur = int(dur_msg_beats * ticks_per_beat)
            # dur = ticks_per_beat
            vel = 60
        else:
            # 1 beat también (para cuadrar con beat)
           # dur = 1 * ticks_per_beat
            dur = int(dur_fill_beats * ticks_per_beat)
            vel = 70

        eventos1.append((t_abs, nota_midi, dur, vel))

    # escribir eventos1 en track1 usando deltas
    eventos1.sort(key=lambda e: e[0])
    last_t = 0
    for (t_abs, nota, dur, vel) in eventos1:
        delta = t_abs - last_t
        track1.append(Message('note_on', note=nota, velocity=vel, time=delta))
        track1.append(Message('note_off', note=nota, velocity=vel, time=dur))
        last_t = t_abs + dur

    # --- Pista 2: segunda voz (bajo largo por compás) ---
    if segunda_voz:
        track2 = MidiTrack()
        mid.tracks.append(track2)
        track2.append(Message('program_change',
                      program=instrumento_bajo, time=0))
        # no hace falta repetir tempo, pero no molesta si lo haces

        # número de compases: máximo compás + 1
        if mel_orden:
            compases_tot = max(c for (c, _, _, _) in mel_orden) + 1
        else:
            compases_tot = 0

        eventos2 = []
        for c in range(compases_tot):
            # acorde del compás
            n_acorde = PROGRESION[c % len(PROGRESION)]
            acorde = ACORDES[n_acorde]

            # fundamental del acorde, bajada una octava (más grave)
            frec_bajo = float(acorde[0]) / 2.0
            nota_bajo = frec_a_midi(frec_bajo)

            t_abs = (c * numerador + 0) * ticks_per_beat
            dur = numerador * ticks_per_beat  # dura todo el compás
            vel = 45  # más suave para que no tape

            eventos2.append((t_abs, nota_bajo, dur, vel))

        eventos2.sort(key=lambda e: e[0])
        last_t2 = 0
        for (t_abs, nota, dur, vel) in eventos2:
            delta = t_abs - last_t2
            track2.append(Message('note_on', note=nota,
                          velocity=vel, time=delta))
            track2.append(
                Message('note_off', note=nota, velocity=vel, time=dur))
            last_t2 = t_abs + dur

    # acorde cierre (opcional): lo dejo en track1 al final
    # (si lo quieres cuadrado en el tiempo, habría que posicionarlo también con ticks absolutos)
    mid.save(nombre_archivo)
'''


def exportar_melodia_a_midi(melodia, nombre_archivo="mensaje.mid", bpm=60, instrumento=0):
    # OLD but works...
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
