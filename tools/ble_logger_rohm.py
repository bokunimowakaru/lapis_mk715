#!/usr/bin/env python3
# coding: utf-8

################################################################################
# BLE Logger
#
# for:
#   iot_exp_press_ble
#   iot_exp_press_udp_ble
#   iot_exp_sensorShield_ble
#   iot_exp_sensorShield_ble_rh
#   iot_exp_sensorShield_udp_ble
#   LAPIS MK715用 cq_ex11_ble_sw, cq_ex12_ble_temp, cq_ex13_ble_hum
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

ambient_chid='00000'                # ここにAmbientで取得したチャネルIDを入力
ambient_wkey='0123456789abcdef'     # ここにはライトキーを入力
ambient_interval = 30               # Ambientへの送信間隔
interval = 1.01                     # 動作間隔
savedata = False                    # ファイル保存の要否
username = 'pi'                     # ファイル保存時の所有者名
udp_sendto = '255.255.255.255'      # UDP送信宛先
udp_port   = 1024                   # UDP送信先ポート番号
udp_suffix = '4'                    # UDP送信デバイス名に付与する番号
udp_interval = 30                   # UDP送信間隔

from bluepy import btle
from sys import argv
import getpass
from shutil import chown
from time import sleep
import urllib.request                           # HTTP通信ライブラリを組み込む
import json                                     # JSON変換ライブラリを組み込む
import datetime
import subprocess
import socket

url_s = 'https://ambidata.io/api/v2/channels/'+ambient_chid+'/data' # アクセス先
head_dict = {'Content-Type':'application/json'} # ヘッダを変数head_dictへ
body_dict = {'writeKey':ambient_wkey, \
            'd1':0, 'd2':0, 'd3':0, 'd4':0, 'd5':0, 'd6':0, 'd7':0, 'd8':0}

def udp_sender(udp):
    if udp_port <= 0:
        return
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # ソケットを作成
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST,1)
    except Exception as e:                                  # 例外処理発生時
        print(e)                                            # エラー内容を表示
        exit()                                              # プログラムの終了
    if sock:                                                # 作成に成功したとき
        udp = udp.strip('\r\n')                             # 改行を削除してudpへ
        print('UDP Sender =', udp)
        udp=(udp + '\n').encode()                           # 改行追加とバイト列変換
        sock.sendto(udp,('255.255.255.255',udp_port))       # UDPブロードキャスト送信
        sock.close()                                        # ソケットの切断

def udp_sender_sensor(sensors):
    d1 = sensors.get('Temperature')
    d2 = sensors.get('Humidity')
    d3 = sensors.get('Pressure')
    if d1 is not None:
        if d2 is not None and d3 is None and d2 != 0.:
            udp_sender( 'humid_' + udp_suffix + ',' + str(round(d1,2)) + ' ,' + str(round(d2,2)) )
            return
        if d2 is None and d3 is not None:
            udp_sender( 'press_' + udp_suffix + ',' + str(round(d1,2)) + ' ,' + str(round(d3,3)) )
            return
        if d2 is not None and d3 is not None:
            udp_sender( 'envir._' + udp_suffix + ',' + str(round(d1,2)) + ' ,' + str(round(d2,2)) + ' ,' + str(round(d3,3)) )
            return
        udp_sender( 'temp._' + udp_suffix + ',' + str(round(d1,2)) )
        return
    d1 = sensors.get('Illuminance')
    if d1 is not None:
        udp_sender( 'illum_' + udp_suffix + ',' + str(d1) )
        return

def save(filename, data):
    try:
        fp = open(filename, mode='a')                   # 書込用ファイルを開く
    except Exception as e:                              # 例外処理発生時
        print(e)                                        # エラー内容を表示
    fp.write(data + '\n')                               # dataをファイルへ
    fp.close()                                          # ファイルを閉じる
    chown(filename, username, username)                 # 所有者をpiユーザへ

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
    print('    ' + name + ' ' * (14 - len(name)) + '=', value, unit, end='')
    if name == 'Accelerometer' or name == 'Geomagnetic':
        print(' (',round(sensors[name + ' X'],n),\
            round(sensors[name + ' Y'],n),\
            round(sensors[name + ' Z'],n), unit + ')')
    else:
        print()

def parser(dev):
    global val
    sensors = dict()
    isRohmMedal = ''
    for (adtype, desc, value) in dev.getScanData():
        #print("  %3d %s = %s" % (adtype, desc, value))  # ad_t=[{8:'Short Local Name'},{9:'Complete Local Name'}]
        # ローム製 センサメダル
        if adtype == 8 and value[0:10] == 'ROHMMedal2':
            isRohmMedal = 'Sensor Medal'
        # ローム製 センサ・シールド・キット
        if adtype == 9 and value[0:7] == 'espRohm':
            isRohmMedal = 'Sensor Kit espRohm'
        # ESP32マイコン＋Si7021センサ
        if adtype == 9 and value[0:11] == 'espRohmHumi':
            isRohmMedal = 'ESP32 Si7021'
        # ローム製 センサ・シールド・キット
        if adtype == 9 and value == 'R':
            isRohmMedal = 'Sensor Kit RH'
        # Spresens用 IoTセンサ
        if adtype == 8 and value[0:8]  == 'LapisDev':
            isRohmMedal = 'Spresense Rohm IoT'
        # Lapis MK715用 IoTセンサ
        if (adtype == 8 or adtype == 9) and (value  == 'nRF5x'):
            isRohmMedal = 'Nordic nRF5'
        if desc == 'Manufacturer':
            val = value
        if isRohmMedal == '' or val == '':
            continue
        print("\nDevice %s (%s), RSSI=%d dB, Connectable=%s" % (dev.addr, dev.addrType, dev.rssi, dev.connectable))
        sensors = dict()
        print('    isRohmMedal   =',isRohmMedal)

        if isRohmMedal == 'Sensor Medal':
            # センサ値を辞書型変数sensorsへ代入
            sensors['ID'] = hex(payval(2,2))
            sensors['Temperature'] = -45 + 175 * payval(4,2) / 65536
            sensors['Humidity'] = 100 * payval(6,2) / 65536
            sensors['SEQ'] = payval(8)
            sensors['Condition Flags'] = bin(int(val[16:18],16))
            sensors['Accelerometer X'] = payval(10,2,True) / 4096
            sensors['Accelerometer Y'] = payval(12,2,True) / 4096
            sensors['Accelerometer Z'] = payval(14,2,True) / 4096
            sensors['Accelerometer'] = sensors['Accelerometer X']\
                                     + sensors['Accelerometer Y']\
                                     + sensors['Accelerometer Z']
            sensors['Geomagnetic X'] = payval(16,2,True) / 10
            sensors['Geomagnetic Y'] = payval(18,2,True) / 10
            sensors['Geomagnetic Z'] = payval(20,2,True) / 10
            sensors['Geomagnetic']   = sensors['Geomagnetic X']\
                                     + sensors['Geomagnetic Y']\
                                     + sensors['Geomagnetic Z']
            sensors['Pressure'] = payval(22,3) / 2048
            sensors['Illuminance'] = payval(25,2) / 1.2
            sensors['Magnetic'] = hex(payval(27))
            sensors['Steps'] = payval(28,2)
            sensors['Battery Level'] = payval(30)
            sensors['RSSI'] = dev.rssi

        if isRohmMedal == 'Sensor Kit espRohm' and len(val) < 17 * 2:
            sensors['ID'] = hex(payval(2,2))
            sensors['Temperature'] = -45 + 175 * payval(4,2) / 65536
            press = payval(6,3)
            if press > 0:
                sensors['Pressure'] = payval(6,3) / 2048
            sensors['SEQ'] = payval(9)
            sensors['RSSI'] = dev.rssi

        if isRohmMedal == 'Sensor Kit espRohm' and len(val) >= 17 * 2:
            sensors['ID'] = hex(payval(2,2))
            sensors['Temperature'] = payval(4,1) / 4 - 15
            sensors['Pressure'] = payval(5,1,True) + 1027
            sensors['Illuminance'] = payval(6,2) / 1.2
            sensors['Proximity'] = payval(8,1)
            sensors['Color R'] = payval(9,1) / 256 * 100
            sensors['Color B'] = payval(10,1) / 256 * 100
            sensors['Color G'] = payval(11,1) / 256 * 100
            sensors['Color IR'] = 100 - sensors['Color R']\
                                      - sensors['Color G']\
                                      - sensors['Color B']
            if sensors['Color IR'] < 0:
                sensors['Color IR'] = 0
            sensors['Accelerometer X'] = payval(12,1,True) / 64
            sensors['Accelerometer Y'] = payval(13,1,True) / 64
            sensors['Accelerometer Z'] = payval(14,1,True) / 64
            sensors['Accelerometer'] = (sensors['Accelerometer X'] ** 2\
                                      + sensors['Accelerometer Y'] ** 2\
                                      + sensors['Accelerometer Z'] ** 2) ** 0.5
            sensors['Geomagnetic X'] = payval(15,1,True)
            sensors['Geomagnetic Y'] = payval(16,1,True)
            sensors['Geomagnetic Z'] = payval(17,1,True)
            sensors['Geomagnetic']  = (sensors['Geomagnetic X'] ** 2\
                                     + sensors['Geomagnetic Y'] ** 2\
                                     + sensors['Geomagnetic Z'] ** 2) ** 0.5
            sensors['SEQ'] = payval(18)
            sensors['RSSI'] = dev.rssi

        if isRohmMedal == 'Sensor Kit RH':
            sensors['ID'] = hex(payval(2,2))
            sensors['Temperature'] = -45 + 175 * payval(4,2) / 65536
            sensors['Illuminance'] = payval(6,2) / 1.2
            sensors['SEQ'] = payval(8)
            sensors['Condition Flags'] = bin(int(val[16:18],16))
            sensors['Accelerometer X'] = payval(10,2,True) / 4096
            sensors['Accelerometer Y'] = payval(12,2,True) / 4096
            sensors['Accelerometer Z'] = payval(14,2,True) / 4096
            sensors['Accelerometer'] = (sensors['Accelerometer X'] ** 2\
                                      + sensors['Accelerometer Y'] ** 2\
                                      + sensors['Accelerometer Z'] ** 2) ** 0.5
            sensors['Geomagnetic X'] = payval(16,2,True) / 10
            sensors['Geomagnetic Y'] = payval(18,2,True) / 10
            sensors['Geomagnetic Z'] = payval(20,2,True) / 10
            sensors['Geomagnetic']  = (sensors['Geomagnetic X'] ** 2\
                                     + sensors['Geomagnetic Y'] ** 2\
                                     + sensors['Geomagnetic Z'] ** 2) ** 0.5
            sensors['Pressure'] = payval(22,3) / 2048
            sensors['RSSI'] = dev.rssi

        if isRohmMedal == 'Spresense Rohm IoT':
            sensors['ID'] = hex(payval(2,2))
            sensors['Temperature'] = -45 + 175 * payval(4,2) / 65536
            sensors['Pressure'] = payval(6,3) / 2048
            sensors['SEQ'] = payval(9)
            sensors['RSSI'] = dev.rssi

        if isRohmMedal == 'ESP32 Si7021':
            sensors['ID'] = hex(payval(2,2))
            sensors['Temperature'] = -45 + 175 * payval(4,2) / 65536
            sensors['Humidity'] = payval(7,2) / 65536 * 100
            sensors['SEQ'] = payval(9)
            sensors['RSSI'] = dev.rssi

        if isRohmMedal == 'Nordic nRF5':
            sensors['ID'] = hex(payval(2,2))
            sensors['Button'] = format(payval(6), '04b')
            sensors['Temperature'] = -45 + 175 * payval(4,2) / 65536
            sensors['Humidity'] = payval(7,2) / 65536 * 100
            sensors['SEQ'] = payval(9)
            sensors['RSSI'] = dev.rssi

        if sensors:
            printval(sensors, 'ID', 0, '')
            printval(sensors, 'SEQ', 0, '')
            printval(sensors, 'Button', 0, '')
            printval(sensors, 'Temperature', 2, '℃')
            printval(sensors, 'Humidity', 2, '%')
            printval(sensors, 'Pressure', 3, 'hPa')
            printval(sensors, 'Illuminance', 1, 'lx')
            printval(sensors, 'Proximity', 0, 'count')
            if(sensors.get('Color R')):
                print('    Color RGB     =',round(sensors['Color R']),\
                                            round(sensors['Color G']),\
                                            round(sensors['Color B']),'%')
                print('    Color IR      =',round(sensors['Color IR']),'%')
            printval(sensors, 'Accelerometer', 3, 'g')
            printval(sensors, 'Geomagnetic', 1, 'uT')
            printval(sensors, 'Magnetic', 0, '')
            printval(sensors, 'Steps', 0, '歩')
            printval(sensors, 'Battery Level', 0, '%')
            printval(sensors, 'RSSI', 0, 'dB')
        isRohmMedal = ''

        # センサ個別値のファイルを保存
        date=datetime.datetime.today()
        if savedata:
            for sensor in sensors:
                if (sensor.find(' ') >= 0 or len(sensor) <= 5 or sensor == 'Magnetic') and sensor != 'Color R':
                    continue
                s = date.strftime('%Y/%m/%d %H:%M')
                # s += ', ' + sensor
                if sensor == 'Button':
                    s += ', ' + sensors['Button'][3]
                    s += ', ' + sensors['Button'][2]
                    s += ', ' + sensors['Button'][1]
                    s += ', ' + sensors['Button'][0]
                else:
                    s += ', ' + str(round(sensors[sensor],3))
                if sensor == 'Color R':
                    s += ', ' + str(round(sensors['Color R'],3))
                    s += ', ' + str(round(sensors['Color G'],3))
                    s += ', ' + str(round(sensors['Color B'],3))
                    s += ', ' + str(round(sensors['Color IR'],3))
                    sensor = 'Color'
                if sensor == 'Accelerometer':
                    s += ', ' + str(round(sensors['Accelerometer X'],3))
                    s += ', ' + str(round(sensors['Accelerometer Y'],3))
                    s += ', ' + str(round(sensors['Accelerometer Z'],3))
                if sensor == 'Geomagnetic':
                    s += ', ' + str(round(sensors['Geomagnetic X'],3))
                    s += ', ' + str(round(sensors['Geomagnetic Y'],3))
                    s += ', ' + str(round(sensors['Geomagnetic Z'],3))
                # print(s, '-> ' + sensor + '.csv') 
                save(sensor + '.csv', s)
    return sensors

# MAIN
if getpass.getuser() != 'root':
    print('使用方法: sudo', argv[0], '[対象MACアドレス]...')
    exit()
scanner = btle.Scanner()
time_amb = 999
time_udp = 999
if ambient_interval < 30:
    ambient_interval = 30
val = ''

while True:
    # BLE受信処理
    try:
        devices = scanner.scan(interval)
    except Exception as e:
        print("ERROR",e)
        subprocess.call(["hciconfig", "hci0", "down"])
        sleep(5)
        subprocess.call(["hciconfig", "hci0", "up"])
        sleep(interval)
        continue
    sensors = dict()

    # 受信データについてBLEデバイス毎の処理
    for dev in devices:
        #print("\nDevice %s (%s), RSSI=%d dB, Connectable=%s" % (dev.addr, dev.addrType, dev.rssi, dev.connectable))
        if len(argv) == 1:
            sensors = parser(dev)
        else:
            for i in range(1, len(argv)):
                if argv[i].lower() == dev.addr:
                    sensors = parser(dev)

    # UDP送信
    if time_udp < udp_interval / interval:
        time_udp += 1
    else:
        time_udp = 0
        udp_sender_sensor(sensors)

    # クラウドへの送信処理
    if int(ambient_chid) == 0 or not sensors or time_amb < ambient_interval / interval:
        time_amb += 1
        continue
    time_amb = 0
    body_dict['d1'] = sensors.get('Temperature')
    body_dict['d2'] = sensors.get('Humidity')
    if not body_dict['d2']:
        body_dict['d2'] = sensors.get('Proximity')
    body_dict['d3'] = sensors.get('Pressure')
    body_dict['d4'] = sensors.get('Illuminance')
    body_dict['d5'] = sensors.get('Accelerometer')
    body_dict['d6'] = sensors.get('Geomagnetic')
    body_dict['d7'] = sensors.get('Steps')
    if not body_dict['d7']:
        body_dict['d7'] = sensors.get('Color R')
    body_dict['d8'] = sensors.get('Battery Level')
    if not body_dict['d8']:
        body_dict['d8'] = sensors.get('Color IR')

    print(head_dict)                                # 送信ヘッダhead_dictを表示
    print(body_dict)                                # 送信内容body_dictを表示
    post = urllib.request.Request(url_s, json.dumps(body_dict).encode(), head_dict)
                                                    # POSTリクエストデータを作成
    try:                                            # 例外処理の監視を開始
        res = urllib.request.urlopen(post)          # HTTPアクセスを実行
    except Exception as e:                          # 例外処理発生時
        print(e,url_s)                              # エラー内容と変数url_sを表示
    res_str = res.read().decode()                   # 受信テキストを変数res_strへ
    res.close()                                     # HTTPアクセスの終了
    if len(res_str):                                # 受信テキストがあれば
        print('Response:', res_str)                 # 変数res_strの内容を表示
    else:
        print('Done')                               # Doneを表示


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
