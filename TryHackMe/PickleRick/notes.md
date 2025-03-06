# First look
## Looking at the source file and robots.txt we get the following values

R1ckRul3s
Wubbalubbadubdub

## After initiating a gobuster I found out that there is a login.php which we can login using the credentials we found.

It brings us to a command panel which we can execute certain commands in a restricted fashion.
I could execute a python reverse shell which but I wanted to make things difficult and wrote my own reverse shell which can be found in the scripts folder. I coded that in few hours so certain errors are expected.

Started a python server on my local machine in order to upload that script into the target machine.

After looking at certain folders like root folder, or rick's own folder we were able to detect the secret ingredients.
