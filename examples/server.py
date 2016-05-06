from twisted.application import service, internet
from twisted.python.log import ILogObserver
from twisted.internet import reactor, task, threads

import sys, os
sys.path.append(os.path.dirname(__file__))
from kademlia.network import Server, QuorumServer
from kademlia import log

def get_done(result, server_ley):

    print ">>Got key result: ",result
    print ">>Got key server_ley: ",server_ley

def set_done(result, server):

    print ">>set_done:", result

def get_input():

    def command_result(command_st, aa=1, bb=2, cc=3):

        commands = command_st.strip().split()

        if(len(commands) > 1):

            op = commands[0]

            key = str(commands[1])

            print "####KEY", key

            if(len(commands) > 2):
                value = commands[2].encode('ascii', 'ignore')

            if op == "q":

                reactor.stop()

            elif op == "set":

                print "adding key:", key, "-->", value
                kserver.set(key, value).addCallback(set_done, kserver)

            elif op == "get":

                print "getting key:", key

                kserver.get(key).addCallback(get_done, kserver)

            else:

                print "command: ",command_st," is wrong format"

        get_input()

    def get_command():

        print ">>enter command:"

        return raw_input()

    d = threads.deferToThread(get_command)
    d.addCallback(command_result)

def bootstrapDone(found, server):

    print("INFO: Bootstrap done")

    get_input()

# Default port number
port = 8468

application = service.Application("kademlia")
application.setComponent(ILogObserver, log.FileLogObserver(sys.stdout, log.INFO).emit)


kserver = QuorumServer(ksize=3)
kserver.bootstrap([("127.0.0.1", port)]).addCallback(bootstrapDone, kserver)

server = internet.UDPServer(port, kserver.protocol)
server.setServiceParent(application)
