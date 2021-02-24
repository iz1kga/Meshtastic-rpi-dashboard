#!/usr/bin/python3

import logging
import os
import sys
import time

from server import serverDaemon
from client import clientDaemon



if __name__ == '__main__':

    action = sys.argv[1]
    Logfile = os.path.join(os.getcwd(), "dashboard.log")
    serverPidfile = os.path.join(os.getcwd(), "server.pid")
    clientPidfile = os.path.join(os.getcwd(), "client.pid")

    logging.basicConfig(filename=Logfile, level=logging.DEBUG)
    s = serverDaemon(pidfile=serverPidfile)
    c = clientDaemon(pidfile=clientPidfile)

    if action == "startServer":
        s.start()
    if action == "startClient":
        c.start()

    elif action == "stopServer":
        s.stop()
    elif action == "stopClient":
        c.stop()

    elif action == "restartServer":
        s.restart()
    elif action == "restartClient":
        c.restart()
