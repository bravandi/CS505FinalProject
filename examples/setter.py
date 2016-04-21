from twisted.internet import reactor
from twisted.python import log
from kademlia.network import Server
import sys

log.startLogging(sys.stdout)

def done(result):
    print "Key result:", result
    #reactor.stop()

def setDone(result, server):
    #server.get("akey").addCallback(done)
    pass

def bootstrapDone(found, server):
    server.set("akey", "Hello!").addCallback(setDone, server)



server = Server(id="zefgdassdas")
server.listen(5456)
server.bootstrap([("127.0.0.1", 8468)]).addCallback(bootstrapDone, server)

reactor.run()
