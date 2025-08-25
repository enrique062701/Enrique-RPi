find_lazserv.exe looks for Lazserv devices on local network using DNS Service Discovery (DNS-SD). 

On Linux Avahi DNS-SD software is usually preinstalled. And you may look for Lazserv devices:

# avahi-browse _ek_lazserv._tcp
+   eth0 IPv6 Ekspla lazserv on rcserv-2                    _ek_lazserv._tcp     local
+   eth0 IPv4 Ekspla lazserv on rcserv-2                    _ek_lazserv._tcp     local
+   eth0 IPv6 Ekspla lazserv on rcserv                      _ek_lazserv._tcp     local
+   eth0 IPv4 Ekspla lazserv on rcserv                      _ek_lazserv._tcp     local


Here you may see two Lazserv devices, rcserv-2 and rcserv, domain is always local for DNS-SD. So to connect 
or ping one of these you should 

# ping rcserv.local



Windows (10) currently partially supports DNS-SD. Name resolving works*) so you can connect or 
ping something like rcserv.local, but you can't see all connected devices, no tools for device discovery.
find_lazserv.exe discovers Lazserv devices and should make life easier.

* Windows name resolving mostly works, but not always. For some weird reasons IE browser unable 
to resolve device IP address unless you install Apple Bonjour service. Bonjour is often installed 
on Windows along with some drivers or software. As well if you have Bonjour installed, you may try 
issuing from command prompt

> dns-sd -B _ek_lazserv._tcp local
Browsing for _ek_lazserv._tcp.local
Timestamp	A/R Flags if Domain	Service Type 	 Instance Name
10:22:22.123	Add	2 6  local.	_ek_lazserv._tcp Ekspla lazserv on rcserv

Here you have one Lazserv instance "on rcserv". So you may ping rcserv.local or retrieve IP address

> dns-sd -G v4 rcserv.local
Timestamp	A/R Flags if Hostname		Address		TTL
10:22:22.123    Add     2  6 rcserv.local	192.168.11.84	120

Once DNS-SD hostname is known you may also get IP address this way

> ping -a -4 rcserv.local

Pinging rcserv.local [192.168.11.84] with 32 bytes of data:


To get Bonjour you may look for and download from Apple.com Bonjour Print Services for Windows.