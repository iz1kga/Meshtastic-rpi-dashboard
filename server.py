# -*- coding: utf-8 -*-
import argparse
import random
import os

import cherrypy

from ws4py.server.cherrypyserver import WebSocketPlugin, WebSocketTool
from ws4py.websocket import WebSocket
from ws4py.messaging import TextMessage


class consoleWebSocketHandler(WebSocket):
    def received_message(self, m):
        #cherrypy.engine.publish('websocket-broadcast', m)
        cherrypy.engine.publish('websocket-broadcast', m)

#    def closed(self, code, reason="A client left the room without a proper explanation."):
#        cherrypy.engine.publish('websocket-broadcast', "{'closed':true}")

class Root(object):
    def __init__(self, host, port, ssl=False):
        self.host = host
        self.port = port
        self.scheme = 'wss' if ssl else 'ws'

    @cherrypy.expose
    def index(self):
        return """<html>
        <head>

        <link rel="stylesheet" href="https://cdn.jsdelivr.net/gh/openlayers/openlayers.github.io@master/en/v6.5.0/css/ol.css" type="text/css">

        <script type='application/javascript' src='https://ajax.googleapis.com/ajax/libs/jquery/1.8.3/jquery.min.js'></script>
        <script src="https://cdn.jsdelivr.net/gh/openlayers/openlayers.github.io@master/en/v6.5.0/build/ol.js"></script>
        <script type='application/javascript'>


        var jsonData;
        var nodeList = [];


        var lat=45.07;
        var lon=7.51;
        var z=10;

var icon="http://www.openstreetmap.org/openlayers/img/marker.png";
var iconFeatures=[];
var vectorSource = new ol.source.Vector({
    features: iconFeatures //add an array of features
});

var iconStyle = new ol.style.Style({
    image: new ol.style.Icon(/** @type {olx.style.IconOptions} */ ({
        anchor: [0.5, 46],
        anchorXUnits: 'fraction',
        anchorYUnits: 'pixels',
        opacity: 0.95,
        src:icon
    }))
});

var vectorLayer = new ol.layer.Vector({
    source: vectorSource,
    style: iconStyle
});


function addMarker(lon,lat,icon) {
var iconGeometry=new ol.geom.Point(ol.proj.transform([lon,lat], 'EPSG:4326','EPSG:3857'));
var iconFeature = new ol.Feature({
    geometry:iconGeometry
});

iconFeatures.push(iconFeature);
}

        function mapInit() {
            var map = new ol.Map({
            target: 'map',
            layers: [
                new ol.layer.Tile({
                source: new ol.source.OSM()
                })
            ],
            view: new ol.View({
                center: ol.proj.fromLonLat([lon, lat]),
                zoom: z
                })
            });
            map.addLayer(vectorLayer);
        }

        function writeConsole(txt){
            $('#console').val($('#console').val() + txt + '\\n');
            $('#console').scrollTop($('#console')[0].scrollHeight);
        }

        $(document).ready(function() {
          mapInit();

          websocket = '%(scheme)s://%(host)s:%(port)s/ws';
          if (window.WebSocket) {
            ws = new WebSocket(websocket);
          }
          else if (window.MozWebSocket) {
            ws = MozWebSocket(websocket);
          }
          else {
            console.log('WebSocket Not Supported');
            return;
          }

          window.onbeforeunload = function(e) {
            writeConsole("Bye bye");
            ws.close(1000, '%(username)s left the room');

            if(!e) e = window.event;
            e.stopPropagation();
            e.preventDefault();
          };
          ws.onmessage = function (evt) {
             writeConsole(evt.data);
             jsonData = JSON.parse(evt.data)


             nodeList = [];
             for (let [key, value] of Object.entries(jsonData.nodes)) {
                 nodeList.push({"id":key,
                                "user":value.user.longName,
                                "pos":{"lat":parseFloat(value.position.latitude).toFixed(4),
                                       "lon":parseFloat(value.position.longitude).toFixed(4),
                                       "alt":parseInt(value.position.altitude)}, 
                                "batt":parseInt(value.position.batteryLevel),
                                "lh":value.position.time});
             }


             nodeList.sort((a,b) => {
                                    // two undefined values should be treated as equal ( 0 )
                                    if( typeof a.lh === 'undefined' && typeof b.lh === 'undefined' )
                                        return 0;
                                    // if a is undefined and b isn't a should have a lower index in the array
                                    else if( typeof a.lh === 'undefined' )
                                        return 1;
                                    // if b is undefined and a isn't a should have a higher index in the array
                                    else if( typeof b.lh === 'undefined' )
                                        return -1;
                                    // if both lhs are defined compare as normal
                                    else
                                        return b.lh - a.lh;
                                    });

             //Nodes Table
             $('#nodes').val("");
             iconFeatures = []
             vectorSource.clear()
             $("#nodesTable tbody").empty();
             nodeList.forEach(element => {
                 var elePos = "";
                 var eleBatt = "";
                 var eleLh = "";
                 if(!isNaN(element.lh))
                     eleLh = new Date(element.lh*1000).toLocaleString();
                 else
                     eleLh = "---";

                 if(isNaN(element.pos.lat))
                 {
                     elePos = "---";
                 }
                 else
                 {
                     elePos = element.pos.lat+"°, "+element.pos.lon+"°, "+element.pos.alt+" m" ;
                     var createIcon=addMarker(element.pos.lon,element.pos.lat,icon);
                     //markerObj[element.id] = 
                 }

                 if(isNaN(element.batt))
                     eleBatt = "---";
                 else
                     eleBatt = element.batt+"&#37;";

                 $("#nodesTable tbody").append("<tr><td>"+element.id+
                                               "</td><td>"+element.user+
                                               "</td><td>"+elePos+
                                               "</td><td>"+eleBatt+
                                               "</td><td>"+
                                               "</td><td>"+eleLh+
                                               "</td></tr>")});

             vectorSource.addFeatures(iconFeatures);
             if(jsonData.packet.decoded.data.portnum == "TEXT_MESSAGE_APP")
             {
                 $('#messages').val($('#messages').val() + jsonData.packet.fromId +": "+ jsonData.packet.decoded.data.text  + '\\n');
             }
          };
          //ws.onopen = function() {
          //   ws.send('{"asd":"lol"}');
          //};
          ws.onclose = function(evt) {
             writeConsole('Connection closed by server: ' + evt.code + ' ' + evt.reason);
          };

          $('#send').click(function() {
             console.log($('#message').val());
             $('#message').val("");
             return false;
          });
        });
      </script>
    </head>
    <body>
      <table id="nodesTable" class="table table-bordered table-condensed table-striped">
          <thead>
              <tr>
                  <th>ID</th>
                  <th>User</th>
                  <th>Position</th>
                  <th>Battery</th>
                  <th>SNR</th>
                  <th>Last Heard</th>
              </tr>
          </thead>
          <tbody>
          </tbody>
      </table>
      <div id="map" style="width:100%%; height:400px"></div>
      <textarea id='console' style='width: 100%%; heigth:350px'></textarea>

    </body>
    </html>
    """ % {'username': "User%d" % random.randint(0, 100), 'host': self.host, 'port': self.port, 'scheme': self.scheme}

    @cherrypy.expose
    def ws(self):
        cherrypy.log("Handler created: %s" % repr(cherrypy.request.ws_handler))
        print("Starting serint")


if __name__ == '__main__':
    import logging
    from ws4py import configure_logger


    configure_logger(level=logging.DEBUG)

    parser = argparse.ArgumentParser(description='Echo CherryPy Server')
    parser.add_argument('--host', default='127.0.0.1')
    parser.add_argument('-p', '--port', default=9000, type=int)
    parser.add_argument('--ssl', action='store_true')
    args = parser.parse_args()

    cherrypy.config.update({'server.socket_host': args.host,
                            'server.socket_port': args.port,
                            'tools.staticdir.root': os.path.abspath(os.path.join(os.path.dirname(__file__), 'static'))})

    if args.ssl:
        cherrypy.config.update({'server.ssl_certificate': './server.crt',
                                'server.ssl_private_key': './server.key'})

    WebSocketPlugin(cherrypy.engine).subscribe()
    cherrypy.tools.websocket = WebSocketTool()

    cherrypy.quickstart(Root(args.host, args.port, args.ssl), '', config={
        '/ws': {
            'tools.websocket.on': True,
            'tools.websocket.handler_cls': consoleWebSocketHandler
            },
        '/js': {
              'tools.staticdir.on': True,
              'tools.staticdir.dir': 'js'
            }
        }
    )



