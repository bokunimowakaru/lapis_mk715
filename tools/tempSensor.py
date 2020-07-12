#!/usr/bin/env python3
# coding: utf-8

################################################################################
# 温度センサ・モジュール
#
#                                               Copyright (c) 2020 Wataru KUNINO
################################################################################

class TempSensor():                                     # クラスTempSensorの定義
    _filename = ['/sys/class/thermal/thermal_zone0/temp',
                 '/sys/devices/platform/coretemp.0/temp0_input',
                 'temp.txt']                            # デバイスのファイル名
    print('温度センサ初期化中')
    fp = None
    for i in _filename:
        print('Sensor :',i,end='')
        try:                                            # 例外処理の監視を開始
            fp = open(i)                                # ファイルを開く
            print(', OK')
            break
        except Exception as e:                          # 例外処理発生時
            print(', Failed')
    if fp is None:
        print('温度センサの初期化に失敗しました')
        raise Exception('SensorDeviceNotFound')         # 例外を応答

    def __init__(self):                                 # コンストラクタ作成
        self.offset = float(30.0)                       # 温度センサ補正用
        self.value = float()                            # 測定結果の保持用

    def get(self):                                      # 温度値取得用メソッド
        self.fp.seek(0)                                 # 温度ファイルの先頭へ
        val = float(self.fp.read()) / 1000              # 温度センサから取得
        val -= self.offset                              # 温度を補正
        val = round(val,1)                              # 丸め演算
        self.value = val                                # 測定結果を保持
        return val                                      # 測定結果を応答

    def __del__(self):                                  # インスタンスの削除
        self.fp.close()                                 # ファイルを閉じる

