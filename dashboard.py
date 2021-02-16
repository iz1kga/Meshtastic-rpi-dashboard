#!python3

import meshtastic
import cherrypy


interface = meshtastic.SerialInterface()



class HelloWorld(object):
    @cherrypy.expose
    def index(self):
        return interface.nodes[]

cherrypy.quickstart(HelloWorld())

