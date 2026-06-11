import asyncio

from mixer import Mixer
from conductor import conductor
from channel import get_channels

BPM = 125
channels = get_channels("configs/channels_slaphouse.py", BPM)

async def testing_loop(channels):

    while True:

        command = await asyncio.to_thread(input, "> ")

        try:
            parts = command.split()
            if parts[0] == "all" and parts[1] == "off":
                for channelName in channels:
                    channels[channelName].enabled = False
                continue
                
            if parts[1] == "on":
                channels[parts[0]].enabled = True

            elif parts[1] == "off":
                channels[parts[0]].enabled = False
        except Exception as e:
            print("Invalid command")

async def main():
    
    mixer = Mixer()
    mixer.start()
    
    channels["1"].enabled = True
    #channels["3"].enabled = True

    await asyncio.gather(
        conductor(mixer, channels),
        testing_loop(channels)
    )

if __name__ == "__main__":
    asyncio.run(main())