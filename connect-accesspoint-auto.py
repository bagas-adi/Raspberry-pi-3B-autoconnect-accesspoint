import paho.mqtt.publish as publish 
from subprocess import Popen, PIPE, check_output
import subprocess 
import math 
import argparse 
import re
import wifi
import threading 
import random 
from gps import *
import glob
import csv
import datetime
import RPi.GPIO as GPIO   #import the GPIO library
import time
import Adafruit_CharLCD as LCD
import os

global i
global sinyal1
global IP_NODE_1,IP_NODE_2, IP_GATEWAY, IP_HOST
global _isConnected
global namaFile
tSkrg = datetime.datetime.now()
tClock = time.clock()
i=1;
 
"""
    TODO :
    1. download fping -> apt-get install fping
    2. download module wifi -> pip install wifi
    3. testing
    
    NOTE :
    1. ifupWlan0 delay 1.5 s
    2. reConnecting delay 1.5 s
    3. tiap iterasi Main program 0.5 s
    4. jadi minimal perlu 2s tiap iterasi untuk reConnecting ke Gateway
     
"""
 
def Search(ip):
    wifilist = []

    if isConnected(ip) :
        try:
    	    cells = wifi.Cell.all('wlan0') #NOTE : menggunakan interface, jadi harus diperhatikan jeda command yg menggunakan interface
        except wifi.exceptions.InterfaceError as error :
            return wifilist
        else :
            for cell in cells:
                wifilist.append(cell)
            return wifilist
    else :
        ifupWlan0()
        return wifilist

def rssi():
    parser = argparse.ArgumentParser(description='Display WLAN signal strength.')
    parser.add_argument(dest='interface', nargs='?', default='wlan0',
                        help='wlan interface (default: wlan0)')
    args = parser.parse_args()
    cmd = subprocess.Popen('iwconfig %s' % args.interface, shell=True,
                           stdout=subprocess.PIPE)
    for line in cmd.stdout:
        if 'Link Quality' in line:
            strength = line[43:46]
            global sinyal1
            sinyal1 = strength
def cekPing(ip):
    stringCmd = 'fping -C 1 -q ' + ip  # output is 'time in ms' or ' - '
    # stringCmd = 'fping '+ ip #output 'is alive' or 'is unreachable'
    try:
        output = check_output(stringCmd.split(' '),
                              stderr=subprocess.STDOUT)
    except subprocess.CalledProcessError as error:
        cmd = error.output
    else:
        cmd = output
    return cmd
def isConnected(ip):
    #NOTE : output berupa kondisi T or F
    output = cekPing(ip) 
    if '-' not in output:
        err = True
    else :
        err = False
    return err
def ipStat(ip):
    #NOTE : output berupa waktu ping atau '-'
    output = cekPing(ip)
    splitOutput = output.split(':')
    splitOutput = splitOutput[1]
    if '-' not in output:
        err = splitOutput
    else :
        err = splitOutput
    return err 
def getmac(interface):
    try:
        mac = open('/sys/class/net/'+interface+'/address').readline()
    except:
        mac = "00:00:00:00:00:00"
    return mac[0:17]
def ifupWlan0():
    # NOTE : menggunakan interface, jadi harus diperhatikan jeda command yg menggunakan interface
    try :
        ifup_output = check_output(['sudo','/sbin/ifup','wlan0'],stderr=subprocess.STDOUT)
    except subprocess.CalledProcessError as error :
        output = error.output
    else :
        output = ifup_output
    print("ifup wlan0 : "+output)
    time.sleep(1.5)

def reConnecting(ip,ssid,pw):
    # NOTE : menggunakan interface, jadi harus diperhatikan jeda command yg menggunakan interface
    
    if isConnected(ip) :
        check_output(['sudo','/sbin/ifdown','wlan0'],stderr=subprocess.STDOUT)
        time.sleep(1.5)
        print("Not Connected!\nReconnecting ...") 
        try:
            ifup_output = check_output(
                ['sudo', '/sbin/ifup', 'wlan0', '-o', 'wpa-psk=' + pw, '-o', 'wpa-ssid='+ssid, '-o',
                 'wireless-channel=auto'], stderr=subprocess.STDOUT)
        except subprocess.CalledProcessError as error:
            output = error.output
        else:
            output = ifup_output
        # print("connected Again! : " + output)
    else :
    	try :
		ifup_output = check_output(['sudo','/sbin/ifup','wlan0','-o','wpa-psk='+pw,'-o','wpa-ssid='+ssid,'-o','wireless-channel=auto'],stderr=subprocess.STDOUT)
    	except subprocess.CalledProcessError as error :
		output = error.output
    	else :
		output = ifup_output
    	# print("connected Again! : "+output)

#NOTE : main Class
if __name__ == '__main__':
    # print("waktu : " + str(tClock))
    IP_NODE_1 = "192.168.10.7"
    IP_NODE_2 = "192.168.10.15"
    IP_GATEWAY = "192.168.10.1"
    PASSWORD="123456789"
    SSID = 'raspiraspi'
    IP_HOST = IP_GATEWAY 
    print("WELCOME!")  
    try:  
        while True:
            _isConnected = isConnected(IP_GATEWAY)
            if _isConnected:
                print("Connected")
                waktu3 = time.clock()
                delay1 = ipStat(IP_GATEWAY)  # GATEWAY
                delay = ipStat(IP_NODE_2)  # NODE 2
                if '-' in delay :
                    delay = 0
                    print("BLINDZONE")
                else :
                    delay = float(delay)
                if '-' in delay1 :
                    delay1 = 0
                    print("BLINDZONE")
                else :
                    delay1 = float(delay1)
                myMac = getmac("wlan0")
                rssi() 
                time.sleep(0.5)
                print("MAC="+myMac+"\ndBm : "+sinyal1) 

                # time.sleep(0.5)
            else: 
                list = Search(IP_NODE_1)
                # print(list)
                if range(len(list)) > 0 :
                    for i in range(len(list)):
                        if 'ssid='+SSID in str(list[i-1]):
                            print("re-connecting ...")
                            reConnecting(IP_NODE_1,SSID,PASSWORD) 
                time.sleep(0.5)
                print("Not Connected!") 
            tClock = time.clock()
            print("waktu : " + str(tClock))
    except (KeyboardInterrupt, SystemExit):
        print "Done."

