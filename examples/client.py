import sys
import locale
from twisted.internet import reactor, task, threads
from twisted.python import log
from kademlia.network import Server, QuorumServer

log.startLogging(sys.stdout)

def get_done(result, server_ley):

    print ">>Got key result: ",result
    print ">>Got key server_ley: ",server_ley

def set_done(result, server):

    print ">>set_done:", result

def get_input():

    def command_result(command_st):

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
                server.set(key, value).addCallback(set_done, server)

            elif op == "get":

                print "getting key:", key

                server.get(key).addCallback(get_done, server)

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

    return

port = 5485

if(len(sys.argv) > 1):

    port = int(sys.argv[1])

server = QuorumServer(ksize=3)
server.listen(port)

server.bootstrap([("127.0.0.1", 8468)]).addCallback(bootstrapDone, server)

get_input()

reactor.run()
