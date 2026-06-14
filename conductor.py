import asyncio
import time

BEATS_PER_BAR = 4

bar_counters = {}

async def conductor(mixer, channels, bpm):
    
    beat_duration = 60 / bpm
    next_beat = time.monotonic()
    beat = 0
    
    while True:
        for channelName in (c for c in channels if channels[c].beat):
            print(f"Playing")
            channel = channels[channelName]
            if not channel.enabled:
                bar_counters[channelName] = 0
                continue
            mixer.play(channel.sample)
        
                
        if beat % BEATS_PER_BAR == 0:
            print(f"Bar {beat // BEATS_PER_BAR + 1}")
                        
            for channelName in (c for c in channels if not channels[c].beat):
                channel = channels[channelName]
                if not channel.enabled:
                    bar_counters[channelName] = 0
                    continue
                
                counter = bar_counters.get(channelName, 0)
                if counter == 0:
                    print("Play:", channelName)
                    mixer.play(channel.sample)
                    counter = channel.num_bars
                    
                counter -= 1
                bar_counters[channelName] = counter
        
        next_beat += beat_duration
        await asyncio.sleep(max(0,next_beat - time.monotonic()))
                
        beat += 1

