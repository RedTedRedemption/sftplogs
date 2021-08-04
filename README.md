# sftplogs
A simple python tool to analyze sftp logs

#Generating files that the program can read
running `journalctl -r > log.log` will generate a file that the program will read and then parse for valid sftp-server entries, but to save analysis time you might
want to run `journalctl -r | grep "sftp-server\[" > log.log` instead.

This program was written on fedora, so your log output format may be different. Please raise an issue if there is a different format for your system and I may address it.

# Installation and usage
Please note: this program will only work on Linux/BSD as it seems that there is no curses port for python on windows.

Simply download the file and run it with python3. The necessary libraries should be built into Python 3 by default.

If a file is not specified it will ask you to enter the name of one.
You can also specify a file on the command line. Please note that the program assumes you will invoke it in the following format:
`python3 sftpAnalyze.py <filename>`
