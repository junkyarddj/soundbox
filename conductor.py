import asyncio
import time

BPM = 125
BEATS_PER_BAR = 4

bar_counters = {}

async def conductor(mixer, channels):
    
    beat_duration = 60 / BPM
    next_beat = time.monotonic()
    beat = 0
    
    while True:

        for channel in channels.values() if channel.beat == True else []:
            if not channel.enabled:
                continue

            mixer.play(channel.sample)
        
                
        if beat % BEATS_PER_BAR == 0:
            print(f"Bar {beat // BEATS_PER_BAR + 1}")
                        
            for channel in channels.values() if channel.beat == False else []:
                if not channel.enabled:
                    continue
                
                counter = bar_counters.get(channel.name, 0)
                if counter == 0:
                    mixer.play(channel.sample)
                    counter = channel.num_bars
                    
                counter -= 1
                bar_counters[channel.name] = counter
        
        next_beat += beat_duration
        await asyncio.sleep(max(0,next_beat - time.monotonic()))
                
        beat += 1

