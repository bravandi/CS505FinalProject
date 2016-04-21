import sys
import locale
from twisted.internet import reactor
from twisted.python import log
from kademlia.network import Server
from threading import Thread

import time

class Menu(Thread):
    def __init__(self):
        Thread.__init__(self)

    def start(self):
        get_command()

log.startLogging(sys.stdout)

def get_done(result, server_ley):

    #server = server_ley[0]

    #print ">>Got key: ", server_ley[1], "-->", result
    print ">>Got key result: ",result
    print ">>Got key server_ley: ",server_ley

    get_command()

def set_done(result, server):

    print ">>set_done:", result

    get_command()

def bootstrapDone(found, server):
    print("INFO: Bootstrap done")
    #Menu().start()
    return
    # get_command()

def get_command():
    return

    correct_command_format = False

    while correct_command_format == False:

        correct_command_format = True

        print ">>enter command:"

        command_st = raw_input()#.decode(sys.stdin.encoding or locale.getpreferredencoding(True))

        commands = command_st.strip().split()

        # if len(commands) < 4:
        #
        #     print "Wrong Command format. format is {(add|get) {key} [value]"

        op = commands[0]

        key = value = None

        if(len(commands) > 1):
            key = commands[1]

            #key = str(unichr(int(commands[1])))

            key = str(commands[1])

            print "####KEY", key

            if(len(commands) > 2):
                value = commands[2].encode('ascii', 'ignore')

        if op == "q":

            reactor.stop()

        elif op == "set":

            print "adding key:", key, "-->", value
            server.set(key, value).addCallback(set_done, server)

        elif op == "get":

            print "getting key:", key
            #server.get(key).addCallback(get_done, (server, key))
            server.get(key).addCallback(get_done, server)

        else:

            correct_command_format = False

port = 5457

if(len(sys.argv) > 1):

    port = int(sys.argv[1])

server = Server(ksize=3)#id="1"
server.listen(port)

#log.startLogging(open("%s.txt" %port, 'w'))

server.bootstrap([("127.0.0.1", 8468)]).addCallback(bootstrapDone, server)
print("INFO: Continuing with main thread")
reactor.run()


