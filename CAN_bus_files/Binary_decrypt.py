import pandas as pd
import binascii
import string

def hex_to_ascii(hexstr):
    """Convert hex string to ASCII, replace non-printables with '.' """
    try:
        hexstr = str(hexstr).strip()  # force to string
        bytes_data = binascii.unhexlify(hexstr)
        return ''.join([chr(b) if chr(b) in string.printable else '.' for b in bytes_data])
    except Exception:
        return ""

def decode_can_csv(filename):
    # Load CSV
    df = pd.read_csv(filename)

    # Ensure column names
    if "data" not in df.columns:
        df.columns = ["Timestamp", "Arbitration_id", "dlc", "data"]

    # Force all "data" values to strings
    df["data"] = df["data"].astype(str)

    # Convert to ASCII
    df["ascii"] = df["data"].apply(hex_to_ascii)

    # Reassemble messages
    decoded_messages = []
    buffer = ""
    for raw_text in df["ascii"]:
        text = str(raw_text)  # ensure string
        if any(c.isalpha() for c in text):
            buffer += text
        else:
            if buffer:
                decoded_messages.append(buffer.replace(".", "").strip())
                buffer = ""
    if buffer:
        decoded_messages.append(buffer.replace(".", "").strip())

    return decoded_messages

if __name__ == "__main__":
    filename = "can_log_change_burst_modeV2.csv"  # change this
    messages = decode_can_csv(filename)
    print("Decoded messages found in log:")
    for m in messages:
        print("-", m)
