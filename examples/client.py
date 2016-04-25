import sys
import locale
from twisted.internet import reactor, task, threads
from twisted.python import log
from kademlia.network import Server, QuorumServer
from threading import Thread
from twisted.internet.threads import deferToThread

import time

log.startLogging(sys.stdout)

def get_done(result, server_ley):

    #server = server_ley[0]

    #print ">>Got key: ", server_ley[1], "-->", result
    print ">>Got key result: ",result
    print ">>Got key server_ley: ",server_ley

    #get_command()

def set_done(result, server):

    print ">>set_done:", result

    #get_command()

def get_input():

    def command_result(command_st):

        commands = command_st.strip().split()

        # if len(commands) < 4:
        #
        #     print "Wrong Command format. format is {(add|get) {key} [value]"


        if(len(commands) > 1):

            op = commands[0]

            key = value = None

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

                print "command: ",command_st," is wrong format"

        get_input()

    def get_command():

        print ">>enter command:"

        return raw_input()

    # deferToThread(get_command).addCallback(command_result)
    d = threads.deferToThread(get_command)
    d.addCallback(command_result)

def bootstrapDone(found, server):

    print("INFO: Bootstrap done")

    get_input()

    #lc = task.LoopingCall(get_input)
    #lc.start(1)
    #lc.stop()

    #Menu().start()
    return

port = 5485

if(len(sys.argv) > 1):

    port = int(sys.argv[1])

server = QuorumServer(ksize=2)#id="1"
server.listen(port)

#log.startLogging(open("%s.txt" %port, 'w'))

server.bootstrap([("127.0.0.1", 8468)]).addCallback(bootstrapDone, server)
print("INFO: Continuing with main thread")
# reactor.callInThread(aSillyBlockingMethod, "2 seconds have passed")

get_input()

reactor.run()
