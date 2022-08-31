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

devlist = [
	["0104","AMD","AM27256"],
	["010E","AMD","AM27C010"],
	["0110","AMD","AM27C256"],
	["0115","AMD","AM27C64"],
	["0116","AMD","AM27C128"],
	["0185","AMD","AM27512"],
	["0189","AMD","AM27128A"],
	["0191","AMD","AM27C512"],
	["0197","AMD","AM27C020"],
	["019B","AMD","AM27C040"],
	["0402","Fujitsu","MBM27256"],
	["04E3","Fujitsu","MBM27C512"],
	["04E6","Fujitsu","MBM27C1001"],
	["0710","HITACHI","HN27256"],
	["0738","HITACHI","HN27C1000G"],
	["0738","HITACHI","HN27C101"],
	["0794","HITACHI","HN27512"],
	["0794","HITACHI","HN27C512"],
	["07B0","HITACHI","HN27C256"],
	["1025","NEC","D27C512"],
	["10C4","NEC","D27256A"],
	["10C8","NEC","D27C4001"],
	["150B","Signetic","S27C64A"],
	["1515","Signetic","S27C010"],
	["151D","Signetic","S27C512"],
	["158C","Signetic","S27C256"],
	["1C04","Mitsubishi","M5M27256"],
	["1C07","Mitsubishi","M5M27C512A"],
	["1C0D","Mitsubishi","M5L27512"],
	["1C0E","Mitsubishi","M5M27C401"],
	["1C83","Mitsubishi","M5M27C101"],
	["1C8A","Mitsubishi","M5M27C201"],
	["1E05","Atmel","AT27BV010"],
	["1E05","Atmel","AT27C010"],
	["1E05","Atmel","AT27LV010A"],
	["1E0B","Atmel","AT27BV040"],
	["1E0B","Atmel","AT27C040"],
	["1E0D","Atmel","AT27BV512"],
	["1E0D","Atmel","AT27C512R"],
	["1E0D","Atmel","AT27C512R*PLCC32"],
	["1E0D","Atmel","AT27LV512A"],
	["1E86","Atmel","AT27BV020"],
	["1E86","Atmel","AT27C020"],
	["1E8A","Atmel","AT27C080"],
	["1E8C","Atmel","AT27BV256"],
	["1E8C","Atmel","AT27C256R"],
	["1E8C","Atmel","AT27C256R*PLCC32"],
	["1E8C","Atmel","AT27LV256A"],
	["2004","SGS","M27256"],
	["2004","ST","M27256"],
	["2005","ST","M27C1000"],
	["2005","ST","M27C1001"],
	["2005","ST","M27C1001*PLCC32"],
	["2005","ST","M27C1001*TSOP32"],
	["2005","ST","M27W101"],
	["2008","ST","M27C64A"],
	["200D","SGS","M27512"],
	["200D","ST","M27512"],
	["203D","ST","M27C512"],
	["2041","ST","M27C4001"],
	["2041","ST","M27W401"],
	["2042","ST","M27C801"],
	["2042","ST","M27W801"],
	["2061","ST","M27C2001"],
	["2061","ST","M27W201"],
	["2080","ST","M87C257"],
	["2089","ST","M27128A"],
	["208D","ST","M27C256B"],
	["208D","ST","M27C256B*PLCC32"],
	["23C1","Waferscale","WSI27C010L"],
	["2902","Microchip","27C64"],
	["2904","GI","27256"],
	["290D","GI","GI27C512"],
	["290D","Microchip","27C512"],
	["2983","Microchip","27C128"],
	["298C","Microchip","27C256"],
	["8904","INTEL","D27256"],
	["8905","INTEL","D27010"],
	["8907","INTEL","D27C64"],
	["890D","INTEL","D27512"],
	["8934","INTEL","D27C020"],
	["8935","INTEL","D27C010"],
	["893B","INTEL","D27C010A"],
	["893D","INTEL","D27C040"],
	["8989","INTEL","D27128A"],
	["898C","INTEL","D27C256"],
	["89FC","INTEL","D27C128"],
	["89FD","INTEL","D27C512"],
	["8F04","Fairchild","FM27C256"],
	["8F04","National","NM27C256"],
	["8F04","National","NM27C256B"],
	["8F04","National","NMC27C256"],
	["8F04","National","NMC27C256B"],
	["8F04","National","NMC87C257"],
	["8F07","National","NM27C020"],
	["8F08","Fairchild","FM27C040"],
	["8F08","National","NM27C040"],
	["8F83","National","NMC27C128B"],
	["8F85","Fairchild","FM27C512"],
	["8F85","National","NM27C512"],
	["8F85","National","NMC27C512A"],
	["8F86","Fairchild","FM27C010"],
	["8F86","National","NM27C010"],
	["8FC2","National","NMC27C64"],
	["9704","TI","TMS27256"],
	["9704","TI","TMS27C256"],
	["9707","TI","TMS27C64"],
	["9732","TI","TMS27C020"],
	["9746","TI","TMS27C010"],
	["9750","TI","TMS27C040"],
	["9783","TI","TMS27C128"],
	["9785","TI","TMS27C512"],
	["97D6","TI","TMS27C010A"],
	["9815","Toshiba","TMM27512A"],
	["9845","Toshiba","TC57256AD"],
	["9845","Toshiba","TC57256D"],
	["9852","Toshiba","TMM2764A"],
	["9885","Toshiba","TC57512A"],
	["988C","Toshiba","TC574000"],
	["9B04","ST","ST27C256"],
	["9B04","ST","TS27C256"],
	["9B08","Eurotechnique","27C64A"],
	["C20E","Macronix","MX27C1000"],
	["C210","Macronix","MX27C256"],
	["C220","Macronix","MX27C2000"],
	["C240","Macronix","MX27C4000"],
	["C280","Macronix","MX27C8000"],
	["C291","Macronix","MX27C512"]
]

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
        const="signature", help='Get EPROM Electonic Signature (set A9 to 12V)')
task.add_argument('-e', '--erace', dest="cmd", action="store_const",
        const="erace", help='Erace check to EPROM')

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
            ser.write(bytes("w "+format(args.address+i*256,'04x')+
                " 0100 "+format(args.page_size,'02x')+"\n",'ascii'))
        else:
            ser.write(bytes("w "+format(args.address+i*256,'04x')+
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
    print(format(sig[0],'02X')+" "+format(sig[1],'02X'))
    id = format(sig[0],'02X')+format(sig[1],'02X')
    for dev in devlist:
      if id == dev[0]:
        print(dev[1] + " " + dev[2])

def erace_check():
    print("EPROM erace check:")
    ser.flushInput()
    ser.write(bytes("r "+format(args.address,'04x')+" "+
        format(args.bytes*1024,'04x')+" 10\n", 'ascii'))
    print(bytes("r "+format(args.address,'04x')+" "+
        format(args.bytes*1024,'04x')+" 10\n", 'ascii'))
    eeprom = ser.read(args.bytes*1024)
    if(ser.read(1) != b'\0'):
        print("Error: no Ack")
        #sys.exit(1)
    noe = 0
    for b in eeprom:
        if(b != 255):
          noe = noe + 1;
    if (noe != 0):
        print("Erace error " + str(noe))
    else:
        print("Erace Ok")

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
elif args.cmd == 'erace':
    erace_check()

ser.close()
sys.exit(0)
