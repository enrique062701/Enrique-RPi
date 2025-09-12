import can
import time
import os


os.system('sudo ip link set can0 down')
os.system('sudo ip link set can0 type can bitrate 1000000')
os.system('sudo ip link set can0 up')
print('Port has been configured')


try:
    bus = can.interface.Bus(channel = 'can0', interface = 'socketcan')
except OSError:
    print('Can not create bus connection')
    exit()

print('Bus connection has been created')


bus = can.interface.Bus(channel="can0", interface="socketcan")

messages = [
    "00202000",
    "0020312000",
    "00302500",
    "00f84300",
    "0200007a20",
    "02010c3b09",
    "0201163b09",
    "020a016f09",
    "023e0c3b09",
    "070101",
    "070202",
    "0a0000000901",
    "0a00003b0001",
    "0d00",
    "0d01",
    "101e00",
    "102045204f464620",
    "1020506b20202020",
    "10506d702020302e",
    "1074202020302e30",
    "12",
]

for raw in messages:
    try:
        # convert safely
        data = bytes.fromhex(raw)
        dlc = len(data)
        if dlc > 8:
            print(f"Skipping {raw} (too long: {dlc} bytes)")
            continue

        msg = can.Message(
            arbitration_id=0x18820810,
            data=data,
            is_extended_id=True,
        )

        bus.send(msg)
        print(f"Sent: {hex(msg.arbitration_id)} #{data.hex()} (dlc={dlc})")
        time.sleep(0.01)

    except ValueError as e:
        print(f"Bad hex string {raw}: {e}")
    except can.CanError as e:
        print(f"Send failed: {e}")
