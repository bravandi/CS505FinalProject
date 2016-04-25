
import sys
import locale
from twisted.internet import reactor, task
from twisted.python import log
from kademlia.network import Server
from threading import Thread

import time

log.startLogging(sys.stdout)
def menu(servers):
    try:
        print ">> enter command:"
        command_st = raw_input()#.decode(sys.stdin.encoding or locale.getpreferredencoding(True))
        commands = command_st.strip().split()
        sid = int(commands[0])
        op = commands[1]
        key = value = None
        if(len(commands) > 1):
            key = commands[2]
            print ">>> Key: ", key

        if op == "q":
            reactor.stop()

        elif op == "set":
            value = commands[3]
            print "adding key:", key, "-->", value
            servers[key].set(key, value).addCallback(set_done, server)

        elif op == "get":
            print "getting key:", key
            servers[key].get(key).addCallback(get_done, server)
    except:
        pass


def get_done(result, server_key):
    print ">> Got key result: ", result
    print ">> Got key server_key: ", server_key


def set_done(result, server):
    print ">> set_done:", result


def bootstrapDone(found, server):
    print("INFO: Bootstrap done")


def main(servers):
    start_port = 5457

    if(len(sys.argv) > 1):
        num_ports = int(sys.argv[1])

    for port in range( start_port, start_port + num_ports ):
        server = Server(ksize=3)#id="1"
        server.listen(port)
        server.bootstrap([("127.0.0.1", 8468)]).addCallback(bootstrapDone, server)
        servers.append(server)

    l = task.LoopingCall(menu, servers)
    l.start(10)
    print("INFO: Continuing with main thread")
    reactor.run()


servers = []
main(servers)
