import threading

import numpy as np
import sounddevice as sd

class _Voice:
    def __init__(self, audio: np.ndarray):
        self.audio = audio
        self.position = 0

    def finished(self):
        return self.position >= len(self.audio)


class Mixer:

    def __init__(
        self,
        samplerate=44100,
        blocksize=64,
    ):
        self.samplerate = samplerate
        self.blocksize = blocksize

        self.voices = []
        self.lock = threading.Lock()

        self.stream = sd.OutputStream(
            samplerate=samplerate,
            channels=2,
            callback=self.callback,
            blocksize=blocksize,
        )

    def start(self):
        self.stream.start()

    def stop(self):
        self.stream.stop()

    def play(self, audio: np.ndarray):

        if audio.ndim == 1:
            audio = np.column_stack([audio, audio])

        with self.lock:
            self.voices.append(_Voice(audio))

    def callback(
        self,
        outdata,
        frames,
        time,
        status,
    ):
        if status:
            print(status)
            
        mix = np.zeros(
            (frames, 2),
            dtype=np.float32,
        )

        with self.lock:

            dead = []

            for voice in self.voices:

                remaining = (
                    len(voice.audio)
                    - voice.position
                )

                count = min(
                    frames,
                    remaining,
                )

                mix[:count] += voice.audio[
                    voice.position:
                    voice.position + count
                ]

                voice.position += count

                if voice.finished():
                    dead.append(voice)

            for voice in dead:
                self.voices.remove(voice)

        np.clip(
            mix,
            -1.0,
            1.0,
            out=mix,
        )

        outdata[:] = mix