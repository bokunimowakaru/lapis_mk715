#!/usr/bin/env python3
# coding: utf-8

################################################################################
# BLE Logger for ble_sensor ble_logger_vsspp.py
#
# Lapis独自のVSSPPプロファイルでセンサ値を取得するサンプル・プログラムです。
#
#                                         Copyright (c) 2019-2020 Wataru KUNINO
################################################################################

#【インストール方法】
#   bluepy (Bluetooth LE interface for Python)をインストールしてください
#       sudo pip3 install bluepy
#
#【実行方法】
#   実行するときは sudoを付与してください
#       sudo ./ble_logger_vsspp.py &
#
#【参考文献】
#   本プログラムを作成するにあたり下記を参考にしました
#   https://ianharvey.github.io/bluepy-doc/
#   https://ianharvey.github.io/bluepy-doc/scanner.html
#   https://ianharvey.github.io/bluepy-doc/notifications.html

interval = 1.01                     # Blutooth LE 受信動作間隔
target_rssi = -100                  # 接続対象デバイスの最低受信強度
target_devices = [  'LapisDev' ]
target_services = [ '0179bbd0-5351-48b5-bf6d-2167639bc867']
notify_cnf_hnd = [  [0x0025] ]
notify_val_hnd = [  [0x0024] ]

from bluepy import btle
from bluepy.btle import Peripheral, DefaultDelegate
from sys import argv
import getpass

class MyDelegate(DefaultDelegate):

    def __init__(self, params):
        DefaultDelegate.__init__(self)
        self.index = -1
        self.val = b'\x00'
        self.col = 0

    def handleNotification(self, cHandle, data):
        if self.index < 0:
            return
        print('\ndev =' + str(self.index) + ', Handle = ' + hex(cHandle) + ', Notify = ' + data.hex())
        if cHandle in notify_val_hnd[self.index]:
            self.val = data
            self.col = notify_val_hnd[self.index].index(cHandle)

    def value(self):
        return self.val

def parser(dev):
    sensors = dict()
    sensors['isTargetDev'] = None
    sensors['service'] = None
    sensors['index'] = None
    sensors['vals'] = None
    for (adtype, desc, value) in dev.getScanData():
        print('  %3d %s = %s (%d)' % (adtype, desc, value, len(value)))  # ad_t=[{8:'Short Local Name'},{9:'Complete Local Name'}]
        # GATT サービス
        if (adtype == 2 or adtype == 7) and (value in target_services):
            sensors['service'] = value
            sensors['index'] = target_services.index(value)
        if (adtype == 8 or adtype == 9) and (value in target_devices):
            sensors['isTargetDev'] = value
            sensors['index'] = target_devices.index(value)
        # ビーコンデータ
        if desc == 'Manufacturer':
            sensors['vals'] = value
    print('    isTargetDev   =',sensors['isTargetDev'], '(' + str(sensors['index']) + ')')
    return sensors

# 設定確認
if getpass.getuser() != 'root':
    print('使用方法: sudo', argv[0], '[対象MACアドレス(省略可)]...')
    exit()

# MAIN
scanner = btle.Scanner()
val = ''

while True:
    # BLEスキャン
    try:
        devices = scanner.scan(interval)
    except Exception as e:
        print('ERROR',e)
        print('Rebooting HCI, please wait...')
        subprocess.call(['hciconfig', 'hci0', 'down'])
        sleep(5)
        subprocess.call(['hciconfig', 'hci0', 'up'])
        sleep(interval)
        continue
    sensors = dict()
    target_index = None
    isTargetDev = None
    address = None
    addrType = 'random'

    # 受信データについてBLEデバイス毎の処理
    for dev in devices:
        if dev.rssi < target_rssi:
            continue
        print('\nDevice %s (%s), RSSI=%d dB, Connectable=%s' % (dev.addr, dev.addrType, dev.rssi, dev.connectable))
        if len(argv) == 1:
            sensors = parser(dev)
        else:
            for i in range(1, len(argv)):
                if argv[i].lower() == dev.addr:
                    sensors = parser(dev)
        target_index = sensors.get('index')
        if target_index is not None:
            isTargetDev = sensors.get('isTargetDev')
            address = dev.addr
            addrType = dev.addrType
            # print('    9 Complete Local Name =',isTargetDev)
            break
    if (target_index is None) or (isTargetDev is None) or (address is None):
        continue  # スキャンへ戻る

    # GATT処理部1.接続
    print('\nGATT Connect to',address,isTargetDev,'(' + str(target_index) + ')')
    try:
        p = Peripheral(address, addrType = addrType)
    except Exception as e:
    # except btle.BTLEDisconnectError as e:
        print('ERROR:',e)
        continue # スキャンへ戻る
    myDelegate = MyDelegate(DefaultDelegate)
    myDelegate.index = target_index
    p.setDelegate(myDelegate)

    # GATT処理部2.サービス確認
    try:
        svcs = p.getServices();
    except Exception as e:
    # except btle.BTLEDisconnectError as e:
    # except btle.BrokenPipeError as e:
        print('ERROR:',e)
        del p
        continue # スキャンへ戻る
    print('CONNECTED')
    for svc in svcs:
        print(svc)
        if svc.uuid in target_services:
            target_index = target_services.index(svc.uuid)
            myDelegate.index = target_index
    try:
        svc = p.getServiceByUUID(target_services[target_index])
    except Exception as e:
    # except btle.BTLEGattError as e:
        print('ERROR:',e)
        print('no service,',target_services[target_index])
        p.disconnect()
        del p
        continue  # スキャンへ戻る

    # GATT処理部3.Notify登録 Setup to turn notifications on
    err = None
    for hnd in notify_cnf_hnd[target_index]:
        data = b'\x01\x00'
        print('write Notify Config =', hex(hnd), data.hex(), end=' > ')
        try:
            print(p.writeCharacteristic(hnd, data, withResponse=True).get('rsp'))
            val = p.readCharacteristic(hnd)
        except Exception as e:
        # except btle.BTLEDisconnectError as e:
            print('ERROR:',e)
            err = e
            break # forを抜ける
        print('read  Notify Config =', hex(hnd), val.hex() )
        if val != data:
            err = 'Notifications Verify Error'
            print('ERROR:',err)
            break # forを抜ける
    if err is not None:
        del p
        continue  # スキャンへ戻る

    # GATT処理部4.Notify待ち受け
    print('Waiting for Notify...')
    while True:
        try:
            notified = p.waitForNotifications(interval)
        except btle.BTLEDisconnectError as e:
            print('ERROR:',e)
            break
        if notified:
            notified_val = myDelegate.value()
            if type(notified_val) is bytes and len(notified_val) > 0:
                s = notified_val.decode()
                if len(s) >= 2 and s[0:2] == 'AT':
                    print('VSSPPを切断します')
                    p.disconnect()
                    del p
                    break  # whileを抜ける
                print('    Value =', s)

################################################################################
# 関連レポジトリ
# - https://github.com/bokunimowakaru/rohm_iot_for_spresense
#   rohm_iot_for_spresense
#
# - https://github.com/bokunimowakaru/ble.git
#   ble_logger_gatt.py

################################################################################
''' cq_ex_at_2_temp.py による実行結果の一例

pi@raspberrypi:~/lapis_mk715/tools $ sudo ./ble_logger_vsspp.py

Device xx:xx:xx:xx:xx:xx (random), RSSI=-55 dB, Connectable=True
    8 Short Local Name = LapisDev (8)
    1 Flags = 06 (2)
    3 Complete 16b Services = 0000180f-0000-1000-8000-00805f9b34fb,0000180a-0000-1000-8000-00805f9b34fb (73)
  255 Manufacturer = 79010a0b0c0d0e0f (16)
    isTargetDev   = LapisDev (0)

GATT Connect to xx:xx:xx:xx:xx:xx LapisDev (0)
CONNECTED
Service <uuid=Generic Attribute handleStart=10 handleEnd=10>
Service <uuid=Battery Service handleStart=11 handleEnd=14>
Service <uuid=0179bbd0-5351-48b5-bf6d-2167639bc867 handleStart=34 handleEnd=65535>
Service <uuid=Device Information handleStart=15 handleEnd=33>
Service <uuid=Generic Access handleStart=1 handleEnd=9>
write Notify Config = 0x25 0100 > ['wr']
read  Notify Config = 0x25 0100
Waiting for Notify...

dev =0, Handle = 0x24, Notify = 33302e33
    Value = 30.3

dev =0, Handle = 0x24, Notify = 33302e33
    Value = 30.3

dev =0, Handle = 0x24, Notify = 32392e38
    Value = 29.8
'''
################################################################################
''' Gatt Toolを使った接続テストの例

pi@raspberrypi:~ $ gatttool -I -t random -b 74:90:50:ff:ff:ff
[74:90:50:ff:ff:ff][LE]> connect
Attempting to connect to 74:90:50:ff:ff:ff
Connection successful

[74:90:50:ff:ff:ff][LE]> primary
attr handle: 0x0001, end grp handle: 0x0009 uuid: 00001800-0000-1000-8000-00805f9b34fb
attr handle: 0x000a, end grp handle: 0x000a uuid: 00001801-0000-1000-8000-00805f9b34fb
attr handle: 0x000b, end grp handle: 0x000e uuid: 0000180f-0000-1000-8000-00805f9b34fb
attr handle: 0x000f, end grp handle: 0x0021 uuid: 0000180a-0000-1000-8000-00805f9b34fb
attr handle: 0x0022, end grp handle: 0xffff uuid: 0179bbd0-5351-48b5-bf6d-2167639bc867

[74:90:50:ff:ff:ff][LE]> char-desc
handle: 0x0001, uuid: 00002800-0000-1000-8000-00805f9b34fb
handle: 0x0002, uuid: 00002803-0000-1000-8000-00805f9b34fb
handle: 0x0003, uuid: 00002a00-0000-1000-8000-00805f9b34fb
handle: 0x0004, uuid: 00002803-0000-1000-8000-00805f9b34fb
handle: 0x0005, uuid: 00002a01-0000-1000-8000-00805f9b34fb
handle: 0x0006, uuid: 00002803-0000-1000-8000-00805f9b34fb
handle: 0x0007, uuid: 00002a04-0000-1000-8000-00805f9b34fb
handle: 0x0008, uuid: 00002803-0000-1000-8000-00805f9b34fb
handle: 0x0009, uuid: 00002aa6-0000-1000-8000-00805f9b34fb
handle: 0x000a, uuid: 00002800-0000-1000-8000-00805f9b34fb
handle: 0x000b, uuid: 00002800-0000-1000-8000-00805f9b34fb
handle: 0x000c, uuid: 00002803-0000-1000-8000-00805f9b34fb
handle: 0x000d, uuid: 00002a19-0000-1000-8000-00805f9b34fb
handle: 0x000e, uuid: 00002902-0000-1000-8000-00805f9b34fb
handle: 0x000f, uuid: 00002800-0000-1000-8000-00805f9b34fb
handle: 0x0010, uuid: 00002803-0000-1000-8000-00805f9b34fb
handle: 0x0011, uuid: 00002a29-0000-1000-8000-00805f9b34fb
handle: 0x0012, uuid: 00002803-0000-1000-8000-00805f9b34fb
handle: 0x0013, uuid: 00002a24-0000-1000-8000-00805f9b34fb
handle: 0x0014, uuid: 00002803-0000-1000-8000-00805f9b34fb
handle: 0x0015, uuid: 00002a25-0000-1000-8000-00805f9b34fb
handle: 0x0016, uuid: 00002803-0000-1000-8000-00805f9b34fb
handle: 0x0017, uuid: 00002a27-0000-1000-8000-00805f9b34fb
handle: 0x0018, uuid: 00002803-0000-1000-8000-00805f9b34fb
handle: 0x0019, uuid: 00002a26-0000-1000-8000-00805f9b34fb
handle: 0x001a, uuid: 00002803-0000-1000-8000-00805f9b34fb
handle: 0x001b, uuid: 00002a28-0000-1000-8000-00805f9b34fb
handle: 0x001c, uuid: 00002803-0000-1000-8000-00805f9b34fb
handle: 0x001d, uuid: 00002a23-0000-1000-8000-00805f9b34fb
handle: 0x001e, uuid: 00002803-0000-1000-8000-00805f9b34fb
handle: 0x001f, uuid: 00002a2a-0000-1000-8000-00805f9b34fb
handle: 0x0020, uuid: 00002803-0000-1000-8000-00805f9b34fb
handle: 0x0021, uuid: 00002a50-0000-1000-8000-00805f9b34fb
handle: 0x0022, uuid: 00002800-0000-1000-8000-00805f9b34fb
handle: 0x0023, uuid: 00002803-0000-1000-8000-00805f9b34fb
handle: 0x0024, uuid: 0179bbd1-5351-48b5-bf6d-2167639bc867 <-- Read Notify
handle: 0x0025, uuid: 00002902-0000-1000-8000-00805f9b34fb <-- Notify Client Char Config

[xx:xx:xx:xx:xx:xx][LE]> char-write-cmd 0x0025 0100
Notification handle = 0x0024 value: 35 32
Notification handle = 0x0024 value: 35 33
Notification handle = 0x0024 value: 35 34
Notification handle = 0x0024 value: 35 35
Notification handle = 0x0024 value: 35 36
Notification handle = 0x0024 value: 35 37
'''
