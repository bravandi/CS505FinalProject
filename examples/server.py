from twisted.application import service, internet
from twisted.python.log import ILogObserver
from twisted.internet import reactor, task

import sys, os
sys.path.append(os.path.dirname(__file__))
from kademlia.network import Server, QuorumServer
from kademlia import log

application = service.Application("kademlia")
application.setComponent(ILogObserver, log.FileLogObserver(sys.stdout, log.INFO).emit)


#if os.path.isfile('cache.3'):
#    kserver = Server.loadState('cache.pickle3')
#else:

kserver = QuorumServer(ksize=2)#id="0"
kserver.bootstrap([("127.0.0.1", 8468)])

#kserver.saveStateRegularly('cache.pickle3', 10)

server = internet.UDPServer(8468, kserver.protocol)
server.setServiceParent(application)
