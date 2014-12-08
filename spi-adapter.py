#!/usr/bin/python
"""
************************************************************************
* spi-adapter.py 
* 
* Test program for Attiny24 door controller on c-Lever zigbee main PCB
*
* 12/2014, stefan.wyss(at)kaba(dot)com
************************************************************************
"""
import spidev
import time
import RPi.GPIO as GPIO

# debug output 
verbose = 1

# commands
CMD_GETVERSION = [0x02,0x02,0,0,0,0,0,0]
CMD_GETINPUT = [0x01,0x01,0,0,0,0,0,0]

""" function BytesToHex(Bytes) """
def BytesToHex(Bytes):
		return ''.join(["0x%02X " % x for x in Bytes]).strip()

""" function SendCmd(Cmd) """
def SendCmd(Cmd):
	
	# make a copy of the list because xfer2 overwrites input
	tmp = list(Cmd)
	
	GPIO.output(8,False)
	spi.xfer2(tmp)		
	GPIO.output(8,True)
	if verbose:
		print '>'+BytesToHex(Cmd)
		print '<'+BytesToHex(tmp)
	
	crc_should = tmp[-1]
	
	crc_is = 0
	for i in tmp[3:-1]:
			crc_is = crc_is ^ i
	
	if crc_is != crc_should:
		print "Attiny SPI checksum error (0x%02X)" % crc_is 
		exit()
	
	return tmp

# set BCM numbering scheme, GPIO8=CS, CPIO24=DATA_READY
GPIO.setmode(GPIO.BCM) 	
GPIO.setup(8,GPIO.OUT)
GPIO.setup(24,GPIO.IN)

# setup SPI. Use GPIO8 instead of CS0
spi = spidev.SpiDev()
spi.open(0,0)
spi.max_speed_hz=125000
spi.mode = 0 		# requires mode 0

# CS high for the first time
GPIO.output(8,True)
time.sleep(0.01)

# GET_INPUT command (function fails with program exit!)
ans = SendCmd(CMD_GETVERSION)
print "Attiny firmware version is: %02X." % ans[-3], 
print "%02X" % ans[-2]

while True:
	
	# wait for DATA_READY
	while not GPIO.input(24):
		time.sleep(0.01)
		
	ans = SendCmd(CMD_GETINPUT)
	print "Input Number Byte is %02X" % ans[-2]
