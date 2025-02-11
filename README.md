### Bambu Labs LAN printer monitor / notifier

This is a simple monitor script that will call an executable whenever your bambu labs printer changes state from "RUNNING" to anything else - for example, "FAILED". 

Call the script like this:

    python3 monitor.py (IP ADDRESS) (LAN ACCESS CODE) (DEVICE SERIAL NUMBER) /usr/local/bin/mynotifier.sh

And, provided the script /usr/local/bin/mynotifier.sh exists and is executable, it will be called with the appropriate message as an argument whenever a notification is to be sent.

For your convienence, here is the dependencies to install on an ubuntu 22.04 system for this:

    apt-get install -y python3 python3-pip python3-dev
    pip3 install -U pip
    pip3 install -U paho-mqtt chump python-dateutil datetime tzlocal

This was developed for an X1C printer running X1Plus.  It should work on any other bambu printer operating in LAN only mode.  I am unsure if this will work with the new "Bambu Connect" firmware requirements, this software assumes you have a pre Jan 2025 firmware installed on your printer.

- HansonXYZ 2025
