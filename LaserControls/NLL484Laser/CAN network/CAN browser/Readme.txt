================================================================
            Ekspla UAB
            Savanoriu 237, Vilnius, Lituania
            CAN browser is utility dedicated to testing and troubleshooting of Ekspla products
            README File - February 2014
================================================================

This README.TXT file contains information which helps you to install and start 
laser software.

CONTENTS 

1. List of remotely controllable devices
2. Software package contents
3. System requirements 
4. Installing 
5. Release notes
6. Known issues and notes


Following devices may by controlled remotely by the software:
=========================================================

Ekspla made lasers and systems, motion controllers, flash lamp power supplies PS5XXX...
 
Software package contents in installation CD, CAN browser folder:
=========================

1.SetupCanBrowserXXX.exe. Installation file, single executable.
2.CAN_browser.zip Archived folder, for using without installation.
3.CDM*.exe USB drivers needed with p.2
  
Minimum Hardware and Software Requirements
==========================================
  *   Pentium processor
  *   Microsoft Windows XP/2000, Vista, Win 7, Win 8 32 bit and 64bit versions.
  *   CD-ROM drive (for installation only)
  *   USB port or  Serial port

Installing
=========
Following steps must be made:

1 Run executable SetupCanBrowserXXX.exe.  once for installation. For upgrading it is required to uninstall previous version at first. 
2.CanBrowser setup installs USB drivers automatically. You may need to run CDM*.exe in case of unsuccessful driver installing.

Using without CAN browser installation
===========================


1. Run CDM*.exe to install USB drivers.
2. Copy CAN_browser.zip to hard disk and extract all files. Run CAN browser.exe


Release notes
=============
2.00 Initial release
2.01 Fixed isue with menu breaking in Korean windows when menu contains non ASCII symbol.
2.02 Fixed COM port enumeration in Windows 7. Changed permissions for *.INI files
2.03 Fixed Set data (binary upload). 
2.04 Updated USD drivers.
2.05 Fixed issue with ID programmer not disabled in user mode.
V2.06 Fixed CANRS232.dll
V2.061 Help file udated with connection to comunication module
V3.09 CAN gate and 255 registers support

Known issues and notes
======================

1. Go HELP -> Show Help for user manual

 

