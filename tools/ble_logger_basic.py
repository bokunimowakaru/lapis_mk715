#!/usr/bin/env python3
# coding: utf-8

################################################################################
# BLE Logger
#
# LAPIS MK715用 cq_ex11_ble_sw, cq_ex12_ble_temp, cq_ex13_ble_hum
#
# cq_ex11_ble_sw, cq_ex12_ble_temp, cq_ex13_ble_hum が送信するビーコンを受信し
# ビーコンに含まれる、温度センサ値（humは湿度センサ値）を表示します。
#
#                                          Copyright (c) 2019-2020 Wataru KUNINO
################################################################################

#【インストール方法】
#   bluepy (Bluetooth LE interface for Python)をインストールしてください
#       sudo pip3 install bluepy
#
#【実行方法】
#   実行するときは sudoを付与してください
#       sudo ./ble_logger_sens_scan.py &
#
#【参考文献】
#   本プログラムを作成するにあたり下記を参考にしました
#   https://ianharvey.github.io/bluepy-doc/scanner.html
#   https://www.rohm.co.jp/documents/11401/3946483/sensormedal-evk-002_ug-j.pdf

interval = 1.01                     # 動作間隔

from bluepy import btle
from sys import argv
import getpass
#from shutil import chown
from time import sleep

def payval(num, bytes=1, sign=False):
    global val
    a = 0
    if num < 2 or len(val) < (num - 2 + bytes) * 2:
        print('ERROR: data length',len(val))
        return 0
    for i in range(0, bytes):
        a += (256 ** i) * int(val[(num - 2 + i) * 2 : (num - 1 + i) * 2],16)
    if sign:
        if a >= 2 ** (bytes * 8 - 1):
            a -= 2 ** (bytes * 8)
    return a

def printval(dict, name, n, unit):
    value = dict.get(name)
    if value == None:
        return
    if type(value) is not str:
        if n == 0:
            value = round(value)
        else:
            value = round(value,n)
    print('    ' + name + ' ' * (14 - len(name)) + '=', value, unit)

scanner = btle.Scanner()

while True:
    try:
        devices = scanner.scan(interval)
    except Exception as e:
        print("ERROR",e)
        if getpass.getuser() != 'root':
            print('使用方法: sudo', argv[0])
            exit()
        sleep(interval)
        continue
    sensors = dict()

    for dev in devices:
        isRohmMedal = ''
        val = ''
        for (adtype, desc, value) in dev.getScanData():
            if (adtype == 8 or adtype == 9) and (value  == 'nRF5x'):
                isRohmMedal = 'Nordic nRF5'
            if desc == 'Manufacturer':
                val = value
            if isRohmMedal == '' or val == '':
                continue
            print("\nDevice %s (%s), RSSI=%d dB, Connectable=%s" % (dev.addr, dev.addrType, dev.rssi, dev.connectable))
            sensors = dict()
            print('    isRohmMedal   =',isRohmMedal)
            if isRohmMedal == 'Nordic nRF5':
                sensors['ID'] = hex(payval(2,2))
                sensors['Button'] = format(payval(6), '04b')
                sensors['Temperature'] = -45 + 175 * payval(4,2) / 65536
                sensors['Humidity'] = payval(7,2) / 65536 * 100
                sensors['SEQ'] = payval(9)
                sensors['RSSI'] = dev.rssi
            isRohmMedal = ''


''' 実行結果の一例
pi@raspberrypi:~ $ cd
pi@raspberrypi:~ $ git clone http://github.com/bokunimowakaru/lapis_mk715
pi@raspberrypi:~ $ cd ~/lapis_mk715/tools
pi@raspberrypi:~/lapis_mk715/tools $ sudo ./ble_logger_rohm.py

Device xx:xx:xx:xx:xx:xx (random), RSSI=-51 dB, Connectable=False
    isRohmMedal   = Nordic nRF5
    ID            = 0x59
    SEQ           = 0
    Button        = 1111
    Temperature   = 19.05 ℃
    Humidity      = 76.96 %
    RSSI          = -51 dB

Device xx:xx:xx:xx:xx:xx (random), RSSI=-47 dB, Connectable=False
    isRohmMedal   = Nordic nRF5
    ID            = 0x59
    SEQ           = 1
    Button        = 1111
    Temperature   = 19.07 ℃
    Humidity      = 76.96 %
    RSSI          = -47 dB

Device xx:xx:xx:xx:xx:xx (random), RSSI=-51 dB, Connectable=False
    isRohmMedal   = Nordic nRF5
    ID            = 0x59
    SEQ           = 2
    Button        = 1111
    Temperature   = 19.07 ℃
    Humidity      = 76.96 %
    RSSI          = -51 dB
'''
