
# Hack The Box - Underpass Writeup

**Underpass** is a beginner-friendly CTF from Hack The Box. It’s a great challenge for testing essential skills like basic reconnaissance and Linux privilege escalation.

---

## Initial Recon

As usual, we begin with an `nmap` scan. I performed a SYN scan using the `-sS` flag for detailed output, but a regular TCP connect scan (`-sT`) would work just as well.

![img](./img/1nmap_tcp.png)

To be thorough, I also ran a full UDP scan. Since these scans can be time-consuming and I’m taking these screenshots after completing the challenge, I specified the port numbers manually to speed up the process.

![img](./img/2nmap_udp.png)

---

## Exploring the Web Server

Next, we check out the web service. First, we add the domain to our `/etc/hosts` file:

![img](./img/3etc_hosts.png)

Upon visiting the site, we’re greeted with the default Apache landing page.

![img](./img/4inspecting_website.png)

---

## Directory and Subdomain Enumeration

I began fuzzing for hidden directories and files. While tools like `gobuster` and `dirbuster` work well, I prefer using `ffuf` for its flexibility and speed.

Unfortunately, no significant results here:

![img](./img/5dirfuzz.png)

Since the domain is now in our hosts file, we can also fuzz for subdomains using `ffuf`.

![img](./img/6dnsfuzzing_garbage.png)

We got a lot of junk responses. A handy feature of `ffuf` is filtering by response size using the `-fs` flag.

Still, nothing useful at this stage:

![img](./img/7dnsfuzz.png)

---

## SNMP Enumeration

Back to our earlier UDP scan—notice that an SNMP server is running (SNMPv1). SNMP versions 1 and 2c are notoriously insecure, as they use plaintext community strings for authentication. From our scan results, we have access to the default `public` string, which allows us to poll OIDs with `snmpwalk`.

![img](./img/8snmpwalk.png)

Initially, the output looks like a mess. To convert these values into a human-readable format, we need to install and update MIB files.

First, install the required package and download the MIBs:

```bash
sudo apt install snmp-mibs-downloader
sudo download-mibs
```

![img](img/9download_mibs.png)

Now, using the updated database, we can retrieve readable output from the SNMP agent:

![img](img/10snmp_mib_translated.png)

Much better. From this, I noted some interesting details like the username `steve@underpass.htb`, the kernel version, and text like *"UnderPass.htb is the only daloradius server"*. While I didn’t directly use these during exploitation, it highlights how powerful SNMP enumeration can be.

---

## Discovering the Application

At this point, I realized I hadn’t done recursive fuzzing yet. Running `ffuf` again with recursion led us to the `/daloradius` directory—a web-based RADIUS management interface. Within it, we found `/operators` and `/users`.

![img](img/11ffuf_recursion.png)
![img](img/12ffuf_recursion_result.png)

Exploring `/users`, we’re presented with a login page:

![img](img/13inspecting_login.png)

A quick search revealed the default credentials for daloRADIUS:

![img](img/14research_default_credentials.png)
![img](img/15default_credentials.png)

I tried them, and—voilà—we’re in:

![img](img/16_admin_panel.png)

---

## Credentials Dump & Hash Cracking

The first thing that stood out was the *Users* panel.

![img](img/17user_list.png)

For some reason password hashes are stored here which I find quite strange. Let’s try cracking one.

First, save the hash to a file:

![img](img/18write_hash_txt.png)

Then, use `hash-identifier` to determine the hash type:

![img](img/19hash_identifier.png)

It’s an MD5 hash. Time to bring in `john` to crack it:

![img](img/20john.png)

Got it. We now have the password—time to SSH into the target.

![img](img/user_flag.png)

---

## Privilege Escalation

Let’s explore further. Running `sudo -l` reveals that we can start a `mosh-server` as root.

![img](img/sudo_l.png)

Running the server gives us an environment key:

![img](img/starting_mosh_server.png)

We export the key and connect using `mosh-client`:

![img](img/starting_smosh_client.png)

And just like that—we have a root shell.

![img](img/root_flag.png)

---

## Conclusion

Underpass is a solid challenge for beginners. It reinforces basic enumeration techniques, exposes the danger of default credentials and SNMP misconfigurations, and wraps up with a beginner privilege escalation using `mosh-server`.
