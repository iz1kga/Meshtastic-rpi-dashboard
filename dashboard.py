#!/usr/bin/python3

import logging
import os
import sys
import time

from server import serverDaemon
from client import clientDaemon



if __name__ == '__main__':

    action = sys.argv[1]
    serverLogfile = os.path.join(os.getcwd(), "server.log")
    serverPidfile = os.path.join(os.getcwd(), "server.pid")

    clientLogfile = os.path.join(os.getcwd(), "client.log")
    clientPidfile = os.path.join(os.getcwd(), "client.pid")

    logging.basicConfig(filename=serverLogfile, level=logging.DEBUG)
    s = serverDaemon(pidfile=serverPidfile)

    logging.basicConfig(filename=clientLogfile, level=logging.DEBUG)
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