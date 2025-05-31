# LinkVortex

LinkVortex is an great HTB machine for beginners trying to improve their enumeration skills, and basic code analysis. It focuses on 2 major vulnerabilities (independent of each other which is great) on Linux symlinks. Symlinks files are special file types in Linux systems which will point to an actual file. For system stability they are quite dangerous and difficult to manage. To create a link file one can execute the ln command like the following 
```ln <target file> <link file>```
This creates a link file which points us to a legit file on the system. 
One can also create link files to link files which is cool

1) nmap scan 
As usual we start with out nmap scan and we get the following results

2) Inspecting website
In order to inspect the website we add the linkvortex.htb domain to our hosts file.

3) I then start fuzzing using ffuf with the goal of finding hidden gems

4) Inspecting dev. subdomain
Our subdomain fuzzing ffuf resulted in dev. First thing I do since this is a ghost web server, looking for directories like .git and voila we have it