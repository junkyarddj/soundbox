import numpy as np
import importlib.util
import soundfile as sf

from dataclasses import dataclass

@dataclass
class Channel:
    sample: np.ndarray = None
    samplerate: int = None
    
    enabled: bool = False
    num_bars: int = 1

    beat: bool = False
    double: bool = False

def get_channels(genreName, bpm):

    path = "samples/" + genreName + "/config.py"

    spec = importlib.util.spec_from_file_location("channel_config",path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    channels = {}

    for cfg in module.CHANNELS:
        channel = Channel()
        channel.num_bars = cfg.get("num_bars", 1)
        channel.double = cfg.get("double", False)
        channel.beat = cfg.get("beat", False)
        channels[cfg["name"]] = channel
        
        amp = cfg.get("amp", 1)
        
        sample, samplerate = _load_sample(cfg["path"])
        channel.sample = _stretch_to_bars(
            sample * amp,
            samplerate,
            bpm,
            channel.num_bars
        )

    return channels

def _load_sample(path):

    audio, sr = sf.read(
        path,
        dtype="float32",
        always_2d=True,
    )

    return audio, sr

def _stretch_to_bars(audio,samplerate,bpm,bars):
    target_seconds = (bars * 4 * 60 / bpm)

    return _stretch_to_duration(audio,samplerate,target_seconds)

def _stretch_to_duration(audio,samplerate,target_seconds):

    current_seconds = (len(audio)/samplerate)
    factor = (target_seconds / current_seconds)
    new_length = int(len(audio) * factor)
    positions = np.linspace(0,len(audio) - 1,new_length)
    
    channels = []

    for ch in range(audio.shape[1]):
        stretched = np.interp(positions,np.arange(len(audio)),audio[:, ch])
        channels.append(stretched)

    return np.column_stack(channels).astype(np.float32)