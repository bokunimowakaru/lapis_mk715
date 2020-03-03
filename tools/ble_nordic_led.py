#!/usr/bin/env python3
# coding: utf-8

################################################################################
# BLE Example for Nordic LED
#
#                                          Copyright (c) 2019-2020 Wataru KUNINO
################################################################################

#【インストール方法】
#   bluepy (Bluetooth LE interface for Python)をインストールしてください
#       sudo pip3 install bluepy
#
#【実行方法】
#   実行するときは sudoを付与してください
#       sudo ./ble_nordic_led.py
#
#【参考文献】
#   本プログラムを作成するにあたり下記を参考にしました
#   https://ianharvey.github.io/bluepy-doc/scanner.html
#   https://ianharvey.github.io/bluepy-doc/peripheral.html

target_device  = 'cq_ex21_ble_led'                      # ここに接続するデバイス名を入力
target_service = '00001523-1212-efde-1523-785feabcd123' # ここに接続するサービスUUIDを入力
interval = 5                                            # 動作間隔

from bluepy import btle
from bluepy.btle import Peripheral
import getpass

scanner = btle.Scanner()

while True:
    # BLE受信処理
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

    # 受信データについてBLEデバイス毎の処理
    for dev in devices:
        #print("\nDevice %s (%s), RSSI=%d dB, Connectable=%s" % (dev.addr, dev.addrType, dev.rssi, dev.connectable))
        isRohmMedal = ''
        val = ''
        for (adtype, desc, value) in dev.getScanData():
            #print("  %3d %s = %s" % (adtype, desc, value))  # ad_t=[{8:'Short Local Name'},{9:'Complete Local Name'}]
            if adtype == 9 and (value == target_device or value == 'Nordic_Blinky'):
                isRohmMedal = value
            if adtype == 7 and value == target_service:
                val = value
            if isRohmMedal == '' or val == '':
                continue
        if isRohmMedal:
            print("\nDevice %s (%s), RSSI=%d dB, Connectable=%s" % (dev.addr, dev.addrType, dev.rssi, dev.connectable))
            print("    9 Complete Local Name =",isRohmMedal)
            isRohmMedal = ''
            p = Peripheral(dev.addr, addrType='random')
            led = p.readCharacteristic(0x0010)
            if led == b'\x00':
                led = b'\x01'
                print('    LED = ON')
            else:
                led = b'\x00'
                print('    LED = OFF')
            p.writeCharacteristic(0x0010, led)
            p.disconnect()

'''

################################################################################
Gatt Toolを使った接続テストの例

pi@raspberrypi:~/lapis_mk715/tools $ gatttool -I -t random -b xx:xx:xx:xx:xx:xx
[xx:xx:xx:xx:xx:xx][LE]> connect
Attempting to connect to xx:xx:xx:xx:xx:xx
Connection successful
[xx:xx:xx:xx:xx:xx][LE]> primary
attr handle: 0x0001, end grp handle: 0x0009 uuid: 00001800-0000-1000-8000-00805f9b34fb
attr handle: 0x000a, end grp handle: 0x000a uuid: 00001801-0000-1000-8000-00805f9b34fb
attr handle: 0x000b, end grp handle: 0xffff uuid: 00001523-1212-efde-1523-785feabcd123 <-- LEDサービス
[xx:xx:xx:xx:xx:xx][LE]> char-desc 0x000b
handle: 0x000b, uuid: 00002800-0000-1000-8000-00805f9b34fb
handle: 0x000c, uuid: 00002803-0000-1000-8000-00805f9b34fb
handle: 0x000d, uuid: 00001524-1212-efde-1523-785feabcd123
handle: 0x000e, uuid: 00002902-0000-1000-8000-00805f9b34fb
handle: 0x000f, uuid: 00002803-0000-1000-8000-00805f9b34fb
handle: 0x0010, uuid: 00001525-1212-efde-1523-785feabcd123 <-- LEDキャラクタリスティクス・ディスクリプタ
[xx:xx:xx:xx:xx:xx][LE]> char-write-req 0010 01
Characteristic value was written successfully
[xx:xx:xx:xx:xx:xx][LE]> char-write-req 0010 00
Characteristic value was written successfully
'''
