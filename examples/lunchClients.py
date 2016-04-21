import os
import time

port_begin = 5460

#just fix the putty and killall.txt and leaderRun.txt in below lines, in your machine

for i in range(1,10):

    os.system('start cmd /c python D:\CS505FinalProject\examples\client.py ' + str(port_begin))

    port_begin = port_begin + 1