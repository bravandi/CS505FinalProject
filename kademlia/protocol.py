import random
from collections import Counter

from twisted.internet import defer

from rpcudp.protocol import RPCProtocol

from kademlia.node import Node
from kademlia.routing import RoutingTable
from kademlia.log import Logger
from kademlia.utils import digest
from base64 import b64encode

class KademliaProtocol(RPCProtocol):
    def __init__(self, sourceNode, storage, ksize):
        RPCProtocol.__init__(self)
        self.router = RoutingTable(self, ksize, sourceNode)
        self.storage = storage
        self.sourceNode = sourceNode

        self.log = Logger(system=self)

    # def _sendResponse(self, response, msgID, address):
    #     RPCProtocol._sendResponse(self, response, msgID, address)
    #     self.log.info("sending message with message id" + b64encode(msgID))
    #     pass

    # def datagramReceived(self, datagram, address):
    #     RPCProtocol.datagramReceived(self, datagram, address)
    #     self.log.info("datagramReceived message id" + str(b64encode(datagram[1:21])))

    def getRefreshIDs(self):
        """
        Get ids to search for to keep old buckets up to date.
        """
        ids = []
        for bucket in self.router.getLonelyBuckets():
            ids.append(random.randint(*bucket.range))
        return ids

    def rpc_stun(self, sender):
        return sender

    def rpc_ping(self, sender, nodeid):
        source = Node(nodeid, sender[0], sender[1])
        self.welcomeIfNewNode(source)
        return self.sourceNode.id

    def rpc_store(self, sender, nodeid, key, value):
        source = Node(nodeid, sender[0], sender[1])
        self.welcomeIfNewNode(source)
        self.log.debug("got a store request from %s, storing value" % str(sender))
        self.storage[key] = value
        return True

    def rpc_find_node(self, sender, nodeid, key):
        self.log.info("finding neighbors of %i in local table" % long(nodeid.encode('hex'), 16))
        source = Node(nodeid, sender[0], sender[1])
        self.welcomeIfNewNode(source)
        node = Node(key)
        return map(tuple, self.router.findNeighbors(node, exclude=source))

    def rpc_find_value(self, sender, nodeid, key):
        source = Node(nodeid, sender[0], sender[1])
        self.welcomeIfNewNode(source)
        value = self.storage.get(key, None)
        if value is None:
            return self.rpc_find_node(sender, nodeid, key)
        return { 'value': value }

    def callFindNode(self, nodeToAsk, nodeToFind):
        address = (nodeToAsk.ip, nodeToAsk.port)
        d = self.find_node(address, self.sourceNode.id, nodeToFind.id)
        return d.addCallback(self.handleCallResponse, nodeToAsk)

    def callFindValue(self, nodeToAsk, nodeToFind):
        address = (nodeToAsk.ip, nodeToAsk.port)
        d = self.find_value(address, self.sourceNode.id, nodeToFind.id)
        return d.addCallback(self.handleCallResponse, nodeToAsk)

    def callPing(self, nodeToAsk):
        address = (nodeToAsk.ip, nodeToAsk.port)
        d = self.ping(address, self.sourceNode.id)
        return d.addCallback(self.handleCallResponse, nodeToAsk)

    def callStore(self, nodeToAsk, key, value):
        address = (nodeToAsk.ip, nodeToAsk.port)
        d = self.store(address, self.sourceNode.id, key, value)
        return d.addCallback(self.handleCallResponse, nodeToAsk)

    def welcomeIfNewNode(self, node):
        """
        Given a new node, send it all the keys/values it should be storing,
        then add it to the routing table.

        @param node: A new node that just joined (or that we just found out
        about).

        Process:
        For each key in storage, get k closest nodes.  If newnode is closer
        than the furtherst in that list, and the node for this server
        is closer than the closest in that list, then store the key/value
        on the new node (per section 2.5 of the paper)
        """
        if self.router.isNewNode(node):
            ds = []
            for key, value in self.storage.iteritems():

                keynode = Node(digest(key))
                neighbors = self.router.findNeighbors(keynode)
                if len(neighbors) > 0:
                    newNodeClose = node.distanceTo(keynode) < neighbors[-1].distanceTo(keynode)
                    thisNodeClosest = self.sourceNode.distanceTo(keynode) < neighbors[0].distanceTo(keynode)
                if len(neighbors) == 0 or (newNodeClose and thisNodeClosest):
                    ds.append(self.callStore(node, key, value))
            self.router.addContact(node)
            return defer.gatherResults(ds)

    def handleCallResponse(self, result, node):
        """
        If we get a response, add the node to the routing table.  If
        we get no response, make sure it's removed from the routing table.
        """
        if result[0]:
            self.log.info("got response from %s, adding to router" % node)
            self.welcomeIfNewNode(node)
        else:
            self.log.debug("no response from %s, removing from router" % node)
            self.router.removeContact(node)
        return result


class LookupInfo:
    def __init__(self):
        self.counter = Counter()
        self.deferred = defer.Deferred()


class KademliaQuorumProtocol(KademliaProtocol):

    def __init__(self, sourceNode, storage, ksize):
        KademliaProtocol.__init__(self, sourceNode, storage, ksize)
        self.lookup = {}

    def callStore(self, key, value, peers):

        for peer in peers:

            self.forward_request(
                (peer.ip, peer.port),
                self.sourceNode.id,
                key,
                {"type":"set", "value": value})

        return defer.succeed(True)


    def callFindKey(self, key, peers):

        self.lookup[key] = LookupInfo()
        #sender = (self.sourceNode.ip, self.sourceNode.port)

        self.log.info("Find Key peers: %s" %peers)

        for peer in peers:
            self.forward_request(
                (peer.ip, peer.port),
                self.sourceNode.id,
                key,
                {"type":"get"})

        return self.lookup[key].deferred

    def rpc_forward_request(self, sender, nodeid, key, request):
        # Forward request to lookup key quorum

        if(request["type"] == "get" and "sender" not in request):

            request["sender"] = sender

        # self.log.info("Received request %s from %s looking for %s" %(request["type"], sender, key))
        self.log.info("Received Forward request %s from %s looking for a key" %(request["type"], sender))

        source = Node(nodeid, sender[0], sender[1])
        self.welcomeIfNewNode(source)
        neighbors = self.router.findNeighbors(Node(key))
        # Termination condition

        self.log.info("Forward Request neighbors: %s" %neighbors)

        if self.terminateForward(key, neighbors) == False:

            # Replace neighbors with k/2 + 1 instead
            for n in neighbors:
                self.forward_request((n.ip,  n.port),
                                     self.sourceNode.id, key, request)
        else:

            if(request["type"] == "set"):

                value = request["value"]

                self.log.debug("Storing value for key %s and value %s" %("[ENCODED KEY]", value))
                self.storage[key] = value

            elif(request["type"] == "get"):

                origin = request["sender"]
                value = self.storage.get(key)
                self.log.debug("Sending RPC Found Key to " + str(origin) + " with found value or NULL")
                self.found_key(origin, key, value)

    def rpc_found_key(self, sender, key, value):

        self.log.info("Found key, value :" + str(value) + " sender :" + str(sender))

        if(key in self.lookup):
            counter = self.lookup[key].counter
            counter[value] += 1

            if ( counter.most_common(1)[0][1] > self.router.ksize * 2 / 3 ):

                self.log.info("Majority accepted value :" + str(value))

    def terminateForward(self, key, neighbors):
        """
        Args:
            key: key that is being looked up
            neighbors: list of k closest neighbors

        Returns:
            if key is closest to quorum nodes than k closest
            neighbors
        """

        k = Node(key)
        min_distance = min([n.distanceTo(k) for n in neighbors])
        min_quorum_distance =  min([n.distanceTo(k) for n in self.sourceNode.getQuorums()])

        self.log.info("min_distance: %s min_quorum_distance: %s" %(min_distance, min_quorum_distance))

        return min_distance <= min_quorum_distance