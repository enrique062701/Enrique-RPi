"""
Controller_mimick_v2.py
=======================
Mimics the manufacturer controller on the laser CAN bus.

Decoded protocol (from candump captures):
  Laser identity broadcast : 0x1803280a  dlc=4  00000000  (sent once on power-up)
  Controller reply          : 0x3080a     dlc=4  00000000  (triggers full data dump)
  Laser telemetry           : 0x18820810  (ISO-TP multi-frame + raw structs)
  Controller commands       : 0x19000410  dlc=3  [cmd, 0x1f, 0xff]

Handshake sequence (from start_with_no_control.csv):
  t+0.000  LASER  0x1803280a  00000000   <- laser announces itself
  t+0.139  CTRL   0x3080a     00000000   <- controller replies (triggers data dump)
  t+0.139  LASER  0x18820810  01         <- laser ack (0x01)
  t+0.404  LASER  0x18820810  03         <- laser ready (0x03), then full telemetry burst
  [laser sends full telemetry block ~265ms after handshake]
  t+4.968  CTRL   0x19000410  121fff     <- first controller poll command

Polling cycle (79 commands, from unplug_plug_controller.csv):
  Byte 0 cycles through: 0x12, 0x02, 0x07, 0x10, 0x0d, 0x0a
  Byte 1 always: 0x1f
  Byte 2 normal: 0xff  |  burst mode: 0xef  (bit 4 = mode flag)

Heartbeat (no controller):
  Laser sends 0x12 on 0x18820810 at 1 Hz until controller is detected.

Usage:
  python3 Controller_mimick_v2.py [--burst] [--send CMD]

  --burst         Enable burst mode flag (byte 2 = 0xef instead of 0xff)
  --send CMD      Inject a one-shot command after next poll cycle
                  CMD is hex byte0, e.g. --send 12 or --send 0a
  --interval N    Seconds between poll cycles (default: 0.2)
"""

import can
import time
import argparse
import threading
import queue
import sys


LASER_ANNOUNCE_ID  = 0x1803280A   # Laser → broadcast on power-up
CTRL_ANNOUNCE_ID   = 0x0003080A   # Controller → reply to laser announce
LASER_TELEM_ID     = 0x18820810   # Laser → telemetry / status
CTRL_CMD_ID        = 0x19000410   # Controller → command frames

# Command cycle captured whem idle - 79 frames
# Each entry is byte 0 (command). Byte 1 = 0x1f always. Byte 2 = mode flag.
POLL_CYCLE = [
    0x12,
    0x02, 0x07, 0x10, 0x10, 0x02, 0x07, 0x02, 0x10, 0x10,
    0x02, 0x07, 0x02, 0x10, 0x10, 0x02, 0x07, 0x0d, 0x02, 0x10,
    0x10, 0x0d, 0x0a, 0x0a, 0x02, 0x07, 0x10, 0x02, 0x10, 0x07,
    0x10, 0x02, 0x07, 0x02, 0x10, 0x10, 0x02, 0x07, 0x02, 0x10,
    0x10, 0x02, 0x07, 0x0d, 0x02, 0x10, 0x10, 0x0d, 0x0a, 0x0a,
    0x02, 0x07, 0x10, 0x02, 0x10, 0x07, 0x10, 0x02, 0x07, 0x02,
    0x10, 0x10, 0x02, 0x07, 0x02, 0x10, 0x10, 0x02, 0x07, 0x0d,
    0x02, 0x10, 0x10, 0x0d, 0x0a, 0x0a, 0x02, 0x07, 0x10,
]

# Mode flag byte
FLAG_NORMAL = 0xFF
FLAG_BURST  = 0xEF   # bit 4 cleared = burst mode


def build_cmd(byte0: int, mode_flag: int) -> bytes:
    return bytes([byte0, 0x1F, mode_flag])


def send_frame(bus: can.Bus, arb_id: int, data: bytes, extended: bool = True):
    msg = can.Message(arbitration_id=arb_id, data=data, is_extended_id=extended)
    bus.send(msg)


def do_handshake(bus: can.Bus, timeout: float = 5.0) -> bool:
    """
    Wait for laser identity broadcast (0x1803280a), then reply with 0x3080a.
    Returns True if handshake completed, False if timed out.

    Sequence observed:
      LASER  0x1803280a  00000000
      CTRL   0x3080a     00000000   <- we send this
      LASER  0x18820810  01         <- laser ack
      LASER  0x18820810  03         <- laser ready (~265 ms later)
    """
    print("[HANDSHAKE] Waiting for laser identity broadcast on 0x1803280a ...")
    deadline = time.time() + timeout
    while time.time() < deadline:
        msg = bus.recv(timeout=0.5)
        if msg is None:
            continue
        if msg.arbitration_id == LASER_ANNOUNCE_ID:
            print(f"[HANDSHAKE] Laser announced: {msg.data.hex()}  — sending controller reply")
            time.sleep(0.010)  # small gap observed in captures (~10 ms)
            send_frame(bus, CTRL_ANNOUNCE_ID, bytes.fromhex("00000000"))

            # Wait for laser ack (0x01) then ready (0x03)
            acks = []
            ack_deadline = time.time() + 1.0
            while time.time() < ack_deadline and len(acks) < 2:
                m = bus.recv(timeout=0.2)
                if m and m.arbitration_id == LASER_TELEM_ID:
                    acks.append(m.data[0] if m.data else 0)

            print(f"[HANDSHAKE] Laser ack bytes received: {[hex(x) for x in acks]}")

            # Wait for full telemetry burst (~265 ms after handshake in captures)
            print("[HANDSHAKE] Waiting for initial telemetry burst (~400 ms) ...")
            time.sleep(0.400)
            print("[HANDSHAKE] Done — starting poll loop")
            return True

    print("[HANDSHAKE] TIMEOUT — laser did not announce. Check wiring / termination.")
    return False


class LaserController:
    def __init__(self, channel: str = "can0", burst: bool = False,
                 poll_interval: float = 0.200):
        self.channel = channel
        self.mode_flag = FLAG_BURST if burst else FLAG_NORMAL
        self.poll_interval = poll_interval
        self.cycle_index = 0
        self.cmd_queue: queue.Queue = queue.Queue()
        self._stop = threading.Event()
        self.bus = None

    def connect(self) -> bool:
        try:
            self.bus = can.interface.Bus(channel=self.channel, interface="socketcan")
            print(f"[BUS] Connected on {self.channel}")
            return True
        except OSError as e:
            print(f"[BUS] Cannot connect: {e}")
            return False

    def disconnect(self):
        if self.bus:
            self.bus.shutdown()
            print("[BUS] Disconnected")

    def set_burst_mode(self, enabled: bool):
        self.mode_flag = FLAG_BURST if enabled else FLAG_NORMAL
        mode_name = "BURST" if enabled else "NORMAL"
        print(f"[MODE] Switched to {mode_name} mode (flag=0x{self.mode_flag:02x})")

    def inject_command(self, byte0: int):
        """Queue a one-shot command to be sent at next opportunity."""
        self.cmd_queue.put(byte0)
        print(f"[CMD] Queued manual command: 0x{byte0:02x}")

    def _send_next_poll(self):
        """Send the next frame in the poll cycle (or a queued manual command)."""
        # Drain any queued manual commands first
        if not self.cmd_queue.empty():
            byte0 = self.cmd_queue.get_nowait()
            data = build_cmd(byte0, self.mode_flag)
            send_frame(self.bus, CTRL_CMD_ID, data)
            print(f"[TX] Manual cmd: {data.hex()}")
            return

        byte0 = POLL_CYCLE[self.cycle_index]
        data = build_cmd(byte0, self.mode_flag)
        send_frame(self.bus, CTRL_CMD_ID, data)
        self.cycle_index = (self.cycle_index + 1) % len(POLL_CYCLE)

    def _rx_thread(self):
        """Background thread: receive and decode laser telemetry."""
        iso_tp_buffer = {}  # arb_id -> {'expected_len': int, 'payload': bytes}

        while not self._stop.is_set():
            msg = self.bus.recv(timeout=0.1)
            if msg is None:
                continue
            if msg.arbitration_id != LASER_TELEM_ID:
                continue

            data = msg.data
            if not data:
                continue

            first = data[0]
            frame_type = (first & 0xF0) >> 4

            if frame_type == 0:
                # Single frame
                length = first & 0x0F
                payload = bytes(data[1:1 + length])
                self._decode_payload(payload)

            elif frame_type == 1:
                # First frame of multi-frame message
                length = ((first & 0x0F) << 8) | data[1]
                payload = bytes(data[2:])
                iso_tp_buffer[msg.arbitration_id] = {
                    "expected_len": length,
                    "payload": payload,
                    "sn": 1,
                }
                # Send flow control ACK
                fc = build_cmd(0x30, 0x00)  # FC: ContinueToSend, block=0, sep=0
                fc_msg = can.Message(
                    arbitration_id=CTRL_CMD_ID,
                    data=bytes([0x30, 0x00, 0x00]),
                    is_extended_id=True,
                )
                self.bus.send(fc_msg)

            elif frame_type == 2:
                # Consecutive frame
                buf = iso_tp_buffer.get(msg.arbitration_id)
                if buf:
                    buf["payload"] += bytes(data[1:])
                    if len(buf["payload"]) >= buf["expected_len"]:
                        self._decode_payload(buf["payload"][:buf["expected_len"]])
                        del iso_tp_buffer[msg.arbitration_id]

            elif first == 0x12:
                # Heartbeat (0x12 single byte, 1 Hz when no controller)
                print("[RX] Heartbeat 0x12 (laser idle)")

    def _decode_payload(self, payload: bytes):
        """Attempt to decode a reassembled laser payload."""
        try:
            text = payload.decode("ascii", errors="replace").strip()
            if any(c.isprintable() and not c.isspace() for c in text):
                print(f"[RX] Telemetry: {repr(text)}")
                return
        except Exception:
            pass
        print(f"[RX] Raw payload ({len(payload)}B): {payload.hex()}")

    def run(self):
        """Main loop: handshake, then poll forever."""
        if not self.connect():
            return

        # Start RX thread
        rx = threading.Thread(target=self._rx_thread, daemon=True)
        rx.start()

        # Handshake
        if not do_handshake(self.bus):
            # If laser already running (e.g. hot-start), skip handshake and jump in
            print("[WARN] No handshake detected — attempting to join existing bus session")

        # Poll loop
        print(f"[POLL] Starting poll loop  interval={self.poll_interval}s  "
              f"mode={'BURST' if self.mode_flag == FLAG_BURST else 'NORMAL'}")
        print("[POLL] Press Ctrl+C to stop. Use inject_command() or --send flag to send commands.")

        try:
            while not self._stop.is_set():
                self._send_next_poll()
                time.sleep(self.poll_interval)
        except KeyboardInterrupt:
            print("\n[POLL] Stopped by user.")
        finally:
            self._stop.set()
            self.disconnect()


# ── Interactive command input thread ─────────────────────────────────────────

def input_thread(controller: LaserController):
    """
    Reads commands from stdin while the poll loop runs.
    Type a hex byte (e.g. '0a' or '12') and press Enter to inject it.
    Type 'burst' or 'normal' to toggle mode.
    Type 'quit' to exit.
    """
    print("\n[INPUT] Command console ready.")
    print("  Enter a hex command byte (e.g. 02, 07, 0a, 0d, 10, 12)")
    print("  Enter 'burst' or 'normal' to switch mode")
    print("  Enter 'quit' to exit\n")
    while True:
        try:
            raw = input("> ").strip().lower()
        except EOFError:
            break
        if not raw:
            continue
        if raw == "quit":
            controller._stop.set()
            break
        elif raw == "burst":
            controller.set_burst_mode(True)
        elif raw == "normal":
            controller.set_burst_mode(False)
        else:
            try:
                byte0 = int(raw, 16)
                if 0x00 <= byte0 <= 0xFF:
                    controller.inject_command(byte0)
                else:
                    print("  [!] Value out of byte range (0x00–0xFF)")
            except ValueError:
                print("  [!] Unknown input. Enter a hex byte like '0a', or 'burst'/'normal'/'quit'")



def main():
    parser = argparse.ArgumentParser(description="Laser CAN bus controller mimic")
    parser.add_argument("--channel",  default="can0",  help="SocketCAN channel (default: can0)")
    parser.add_argument("--burst",    action="store_true", help="Start in burst mode")
    parser.add_argument("--send",     type=str, default=None,
                        help="Inject a one-shot command (hex byte0) then exit")
    parser.add_argument("--interval", type=float, default=0.200,
                        help="Poll interval in seconds (default: 0.2)")
    args = parser.parse_args()

    ctrl = LaserController(
        channel=args.channel,
        burst=args.burst,
        poll_interval=args.interval,
    )

    if args.send:
        # One-shot mode: connect, send a single command, disconnect
        byte0 = int(args.send, 16)
        if ctrl.connect():
            ctrl.inject_command(byte0)
            time.sleep(0.1)
            ctrl.disconnect()
        return

    # Interactive mode: run poll loop + console input simultaneously
    poll_thread = threading.Thread(target=ctrl.run, daemon=False)
    poll_thread.start()

    time.sleep(0.5)  # give the poll loop time to start

    input_thread(ctrl)
    poll_thread.join(timeout=2.0)


if __name__ == "__main__":
    main()
