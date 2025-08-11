import bz2
BACKUP_FILE = "www/password_backup"

hex_data_str = ""

with open(BACKUP_FILE, "r") as file:
    for line in file:
        parts = line.split()
        hex_parts = [p for p in parts[1:] if all(c in "0123456789abcdef" for c in p.lower())]
        hex_data_str += "".join(hex_parts)

data = bytes.fromhex(hex_data_str.strip())
decompressed = bz2.decompress(data)
with open("backup", "wb") as f:
    f.write(decompressed)
print(decompressed)
