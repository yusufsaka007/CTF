'''
Original Code
https://github.com/haseebT/mRemoteNG-Decrypt.git
'''

#!/usr/bin/env python3

import hashlib
import base64
from Cryptodome.Cipher import AES
import argparse
import sys

encrypted_data = ""

def status_line(msg):
    sys.stdout.write("\r" + " " * 80 + "\r")  # clear previous line (80 chars wide)
    sys.stdout.write(msg)
    sys.stdout.flush()

def decrypt(password, salt, associated_data, nonce, ciphertext, tag):
    try:
        key = hashlib.pbkdf2_hmac("sha1", password.encode(), salt, 1000, dklen=32)

        cipher = AES.new(key, AES.MODE_GCM, nonce=nonce)
        cipher.update(associated_data)
        plaintext = cipher.decrypt_and_verify(ciphertext, tag)
        print("Password: {}".format(plaintext.decode("utf-8")))
        return True
    except Exception as e:
        return False


def main():
    global encrypted_data

    parser = argparse.ArgumentParser(description="Decrypt mRemoteNG passwords.")
    group = parser.add_mutually_exclusive_group()
    group.add_argument(
        "-f", "--file", help="name of file containing mRemoteNG password"
    )
    group.add_argument("-s", "--string", help="base64 string of mRemoteNG password")
    parser.add_argument("-p", "--password", help="Custom password", default="mR3m")
    parser.add_argument("-w", "--wordlist", help="Custom wordlist to attempt a brute force attack")

    if len(sys.argv) < 2:
        parser.print_help(sys.stderr)
        sys.exit(1)

    args = parser.parse_args()
    if args.file:
        with open(args.file) as f:
            encrypted_data = f.read()
            encrypted_data = encrypted_data.strip()
            encrypted_data = base64.b64decode(encrypted_data)

    elif args.string:
        encrypted_data = args.string
        encrypted_data = base64.b64decode(encrypted_data)

    else:
        print("Please use either the file (-f, --file) or string (-s, --string) flag")
        sys.exit(1)

    salt = encrypted_data[:16]
    associated_data = encrypted_data[:16]
    nonce = encrypted_data[16:32]
    ciphertext = encrypted_data[32:-16]
    tag = encrypted_data[-16:]

    if args.wordlist:
        with open(args.wordlist, "r", encoding="utf8") as file:
            for password in file:
                password = password.strip()
                status_line(f"Attempting: {password}")
                rc = decrypt(password, salt, associated_data, nonce, ciphertext, tag)
                if not rc:
                    continue
                break
    else:     
        rc = decrypt(args.password, salt, associated_data, nonce, ciphertext, tag)
        if not rc:
            print("Failed to decrypt password")

if __name__ == "__main__":
    main()
