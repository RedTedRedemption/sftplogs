# sftplogs
A simple python tool to analyze sftp logs

Generating files that the program can read
running `journalctl -r > log.log` will generate a file that the program will read and then parse for valid sftp-server entries, but to save analysis time you might
want to run `journalctl -r | grep "sftp-server\[" > log.log` instead.

This program was written on fedora, so your log output format may be different. Please raise an issue if there is a different format for your system and I may address it.

# Installation and usage
Please note: this program is designed to work on Linux. While there is a curses library that can be installed on windows manually, I have not tested it, so your milage will vary.

To create logfiles that this program can read, you will need to enable logging in `/etc/ssh/sshd_config` by changing `Subsystem   sftp    /usr/lib/openssh/sftp-server` to read
`Subsystem   sftp    /usr/lib/openssh/sftp-server -l INFO`. Please note that sftp activity can be read by normal users using `journalctl` when this setting is activated. If you care about normal users not reading others' sftp activity this may create a security concern.

Simply download sftpAnalyze.py and run it or run `git clone https://github.com/RedTedRedemption/sftplogs`. The necessary libraries should be built into Python 3 by default on Linux/BSD.

If a file is not specified it will ask you to enter the name of one.
You can also specify a file on the command line.

Syntax is:
`./sftpAnalyze.py <filename>` or
`./sftpAnalyze.py`

# Concepts Demonstrated
+ Efficient text processing
+ Regular Expressions
+ Text-Based GUI design
+ UX design
