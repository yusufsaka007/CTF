import argparse
import os

def cisco_7_decrypt(encoded_password):
    # Standard 53-byte Cisco XOR key
    key = "dsfd;kfoA,.iyewrkldJKDHSUBsgvca69834ncxv9873254k;fg87"
    
    try:
        # First 2 digits are the salt (index into the key)
        salt = int(encoded_password[:2])
        # The rest is the hex-encoded cipher
        cipher_hex = encoded_password[2:]
        
        plaintext = ""
        for i in range(0, len(cipher_hex), 2):
            # Grab two hex chars and convert to decimal
            byte = int(cipher_hex[i:i+2], 16)
            # XOR with the key character at the current shifted index
            key_char = ord(key[(salt + (i // 2)) % len(key)])
            plaintext += chr(byte ^ key_char)
            
        return plaintext
    except Exception as e:
        return f"[Error: {e}]"




if __name__ == "__main__":
    parser = argparse.ArgumentParser("Cisco7 decryptor")
    parser.add_argument("-f","--file",required=True,help="File that contain the passwords (eg. <USER> password 7 <PASS>)")
    args = parser.parse_args()
    file = args.file

    if os.path.exists(file):
        with open(file, "r") as f:
            for line in f:
                username = line.split()[0]
                password = line.split()[-1]
                print(username + ":" + cisco_7_decrypt(password))
