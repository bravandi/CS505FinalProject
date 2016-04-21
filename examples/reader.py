from twisted.internet import reactor
from twisted.python import log
from kademlia.network import Server
import sys
import time

log.startLogging(sys.stdout)

def done(result):
    print "Key result: ", result
    reactor.stop()

def setDone(result, server):
    server.get("akey").addCallback(done)

def bootstrapDone(found, server):
    #server.set("a key", "a value").addCallback(setDone, server)

    server.get("akey").addCallback(done)

    #server.chat("2", "message")

server = Server(id="1")
server.listen(5457)

server.bootstrap([("127.0.0.1", 8468)]).addCallback(bootstrapDone, server)

reactor.run()


