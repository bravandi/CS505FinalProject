Installation

    Required packages:

    1) Twisted
        (from http://twistedmatrix.com/trac/wiki/Downloads)
        Twisted allow implementation of RPC over UDP.
    2) RPCUDP
        pip install rpcudp
        (from https://github.com/bmuller/rpcudp)

    Running python setup.py with sufficient privileges will install the dependencies

Usage

    Run the first node using below command:

        twistd.py -noy examples\server.py

        default port number is 8468. since Twisted does not accept any unknown switch,
        to change the port please modify the code.

    Join nodes with below command:

        examples\client.py -b <bootstrap node IP:port> -p <node port number>

        by default bootstrap node is 127.0.0.1:8468


Implementation Details

    The protocol is designed to be as small and fast as possible. Python objects are serialized using MsgPack.
    All calls must fit within 8K (generally small enough to fit in one datagram packet).

Compatibility

    Python 2.7