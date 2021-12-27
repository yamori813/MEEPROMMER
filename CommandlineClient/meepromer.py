#!/usr/bin/env python
# vim:fileencoding=ISO-8859-1
#
#Meeprommer commandline interface
#By Zack Nelson
#Project Home:
#https://github.com/mkeller0815/MEPROMMER
#http://www.ichbinzustaendig.de/dev/meeprommer-en

#Adapted to work with EPROMDate programmer
#By Svetlana Tovarisch

#Backport to original MEEPROMMER and python3 support
#By Hiroki Mori

import serial, sys, argparse, time

# Parse command line arguments
parser = argparse.ArgumentParser(
        description='Meepromer Command Line Interface',
        epilog='Read source for further information')

task = parser.add_mutually_exclusive_group()
task.add_argument('-w', '--write', dest="cmd", action="store_const",
        const="write", help='Write to EPROM')
task.add_argument('-W', '--write_paged', dest="cmd", action="store_const",
        const="write_paged", help='Fast paged write to EPROM')
task.add_argument('-r', '--read', dest="cmd", action="store_const",
        const="read", help='Read from EPROM as ascii')
task.add_argument('-d', '--dump', dest="cmd", action="store_const",
        const="dump", help='Dump EPROM to binary file')
task.add_argument('-v', '--verify', dest="cmd", action="store_const",
        const="verify", help='Compare EPROM with file')
task.add_argument('-V', '--version', dest="cmd", action="store_const",
        const="version", help='Check burner version')
task.add_argument('-S', '--signature', dest="cmd", action="store_const",
        const="signature", help='Check EPROM Electonic Signature (set A9 to 12V)')

parser.add_argument('-a', '--address', action='store', default='0',
        help='Starting eeprom address (as hex), default 0')
parser.add_argument('-o', '--offset', action='store', default='0',
        help='Input file offset (as hex), default 0')
parser.add_argument('-b', '--bytes', action='store', default='32',
        type=int, help='Number of kBytes to r/w, default 32')
parser.add_argument('-p', '--page_size', action='store', default='256',
        type=int, help='Number of bytes per EPROM page e.g.:'+
            'CAT28C*=32, AT28C*=64, X28C*=64, default 32')
parser.add_argument('-f', '--file', action='store',
        help='Name of data file')
parser.add_argument('-c', '--com', action='store',
        default='COM3', help='Com port address')
parser.add_argument('-s', '--speed', action='store',
        type=int, default='57600', help='Com port baud, default 57600')

def dump_file():
    ser.flushInput()
    ser.write(bytes("r "+format(args.address,'04x')+" "+
        format(args.bytes*1024,'04x')+" 10\n", 'ascii'))
    print(bytes("r "+format(args.address,'04x')+" "+
        format(args.bytes*1024,'04x')+" 10\n", 'ascii'))
    eeprom = ser.read(args.bytes*1024)
    if(ser.read(1) != b'\0'):
        print("Error: no Ack")
        #sys.exit(1)
    try:
        fo = open(args.file,'wb+')
    except OSError:
        print("Error: File cannot be opened, verify it is not in use")
        sys.exit(1)
    fo.write(eeprom)
    fo.close()

def verify():
    print("Verifying...")
    ser.flushInput()
    ser.write(bytes("B "+format(args.address,'04x')+" "+
        format(args.bytes*1024,'04x')+" 10\n", 'ascii'))
    try:
        fi = open(args.file,'rb')
    except FileNotFoundError:
        print("Error: ",args.file," not found, please select a valid file")
        sys.exit(1)
    except TypeError:
        print("Error: No file specified")
        sys.exit(1)

    fi.seek(args.offset)
    file = fi.read(args.bytes*1024)
    eeprom = ser.read(args.bytes*1024)
    if ser.read(1) != b'\0':
        print("Error: no EOF received")

    if file != eeprom:
        print("Not equal")
        n = 0
        for i in range(args.bytes*1024):
            if file[i] != eeprom[i]:
                n+=1
        print(n,"differences found")
        sys.exit(1)
    else:
        print("Ok")
        sys.exit(0)
    if(ser.read(1) != b'\0'):
        print("Error: no Ack")
        sys.exit(1)

def read_eeprom():
    ser.flushInput()
    ser.write(bytes("R "+format(args.address,'04x')+" "+
        format(args.address+args.bytes*1024,'04x')+
        " 10\n", 'ascii'))
    ser.readline()#remove blank starting line
    for i in range(int(round(args.bytes*1024/16))):
        print(ser.readline().decode('ascii').rstrip())

def write_eeprom(paged):
    import time

    fi = open(args.file,'rb')
    fi.seek(args.offset)
    now = time.time() #start our stopwatch
    for i in range(args.bytes*4): #write n blocks of 256 bytes
        #if(i % 128 == 0):
        #    print("Block separation")
        #    time.sleep(1)
        output = fi.read(256)
        print("Writing from",format(args.address+i*256,'04x'),
              "to",format(args.address+i*256+255,'04x'))
        if paged:
            ser.write(bytes("W "+format(args.address+i*256,'04x')+
                " 0100 "+format(args.page_size,'02x')+"\n",'ascii'))
        else:
            ser.write(bytes("W "+format(args.address+i*256,'04x')+
                " 0100 00\n",'ascii'))

        ser.flushInput()
        ser.write(output)
        #time.sleep(0.08)
        #if(ser.read(1) != b'%'):
        #    print("Error: no Ack")
        #    sys.exit(1)
        while(ser.read(1) != b'%'):
            time.sleep(0.01)
    print("Wrote",args.bytes*1024,"bytes in","%.2f"%(time.time()-now),"seconds")

def version():
    print("Burner version:")
    ser.flushInput()
    ser.write(bytes("V 0000 0000 00\n", 'ascii'))
    print(ser.readline())

def signature():
    print("EPROM Signature:")
    ser.flushInput()
    ser.write(bytes("S 0000 0000 00\n", 'ascii'))
    sig = ser.read(2)
    print(format(sig[0],'02x')+" "+format(sig[1],'02x'))

args = parser.parse_args()
#convert our hex strings to ints
args.address = int(args.address,16)
args.offset = int(args.offset,16)

SERIAL_TIMEOUT = 1200 #seconds
try:
    ser = serial.Serial(args.com, args.speed, timeout=SERIAL_TIMEOUT)
    time.sleep(2)
except serial.serialutil.SerialException:
    print("Error: Serial port is not valid, please select a valid port")
    sys.exit(1)

if args.cmd == 'write':
    write_eeprom(False)
elif args.cmd == 'write_paged':
    write_eeprom(True)
    #verify()
elif args.cmd == 'read':
    read_eeprom()
elif args.cmd == 'dump':
    dump_file()
elif args.cmd == 'verify':
    verify()
elif args.cmd == 'unlock':
    unlock();
elif args.cmd == 'list':
    list_ports()
elif args.cmd == 'version':
    version()
elif args.cmd == 'signature':
    signature()

ser.close()
sys.exit(0)
