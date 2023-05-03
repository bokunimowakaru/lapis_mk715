# lapis_mk715
Code Exapmles for ROHM/LAPIS MK715x1 EK1, Nordic nRF52811, nRF52832.  

This repository contains code exapmles including project files, for Segger Embedded Studio IDE (Integrated Development Environment).  

## 詳細

無料の統合開発環境IDE Segger Embedded Studio 用のプロジェクト・ファイル一式を含む、サンプル・プログラム集です。  

## 解説書

ROHM/LAPIS MK715x1 を使った入門書「ローコストIoT センサ・ネットワーク プログラミング入門」を公開しています。  
本入門書は、エレキジャックIoT No.3 P.40～P.67「用途別サンプル・プログラム6 本で学びながら試すBLE プログラミング」の後編です。  
エレキジャックIoT No.3で紹介したプログラムの説明は含まれていませんが、本書だけでもプログラムを動かしてみることは可能です。動作を試した後に、エレキジャックIoT No.3を購入していただくことで、より理解が深まると思います。  

- Bluetooth LE マイコン搭載 LAPIS MK715 開発ボードによる  
PDF版 [ローコストIoT センサ・ネットワーク プログラミング入門](https://bokunimo.net/cq/nrf528)  
※ご注意：エレキジャックIoTに掲載したプログラムの説明はありません  

- 用途別サンプル・プログラム6 本で学びながら試すBLE プログラミング  
アマゾン販売サイト：　　　[エレキジャックIoT No.3 Bluetooth通信プログラミング 単行本](https://amzn.to/3Z3Tzyp)  
筆者ブログ内の紹介ページ：[bokunimo.net/blog内の紹介ページ](https://bokunimo.net/blog/esp/883/#Bluetooth_LE%E3%83%9E%E3%82%A4%E3%82%B3%E3%83%B3%E6%90%AD%E8%BC%89LAPIS_MK715%E9%96%8B%E7%99%BA%E3%83%9C%E3%83%BC%E3%83%89_%E7%94%A8%E9%80%94%E5%88%A5%E3%82%B5%E3%83%B3%E3%83%97%E3%83%AB%E3%83%BB%E3%83%97%E3%83%AD%E3%82%B0%E3%83%A9%E3%83%A06%E6%9C%AC%E3%81%A7%E5%AD%A6%E3%81%B3%E3%81%AA%E3%81%8C%E3%82%89%E8%A9%A6%E3%81%99BLE%E3%83%97%E3%83%AD%E3%82%B0%E3%83%A9%E3%83%9F%E3%83%B3%E3%82%B0)  
出版社の紹介ページ：　　　[eleki-jack-iot.com 内の紹介ページ](https://eleki-jack-iot.com/2020/07/28/bluetooth-le%e3%83%9e%e3%82%a4%e3%82%b3%e3%83%b3%e6%90%ad%e8%bc%89-lapis-mk715%e9%96%8b%e7%99%ba%e3%83%9c%e3%83%bc%e3%83%89-%e7%94%a8%e9%80%94%e5%88%a5%e3%82%b5%e3%83%b3%e3%83%97%e3%83%ab%e3%83%bb/)  

## Lapis MK71511/MK71521, Nordic nRF52811, nRF52832用 サンプル・プログラム 収録内容

本レポジトリに含まれているコンテンツは以下の通りです。  

- cq_ex01_led

	サンプル1 LEDの点滅とHello, World!  
	ディップスイッチDIP1～3の状態に応じて、LED4～LED7を点滅制御します。  

- cq_ex02_temp

	サンプル2 マイコン内蔵の温度センサ  
	モジュール内蔵の温度センサの値を読み取ります  

- cq_ex03_hum

	サンプル3 I2Cディジタル・インターフェース搭載・温湿度センサ  
	I2C接続の温湿度センサ SILICON LABS社 Si7021 の値を読み取ります  

- cq_ex11_ble_sw

	サンプル4 Bluetooth LEビーコンの送信  
	モジュール上のDIPスイッチ(4bit)の状態をBLEビーコンで送信します  

- cq_ex12_ble_temp

	サンプル5 温度をビーコン送信  
	モジュール内蔵の温度センサで測定した温度値をBLEビーコンで送信します  

- cq_ex12_ble_temp_le

	サンプル5-LE 温度をビーコン送信 低消費電力版  
	モジュール内蔵の温度センサで測定した温度値をBLE送信します  

- cq_ex12_ble_temp_gatt

	サンプル5-GATT 温度をビーコン送信 (独自)GATT対応版  
	モジュール内蔵の温度センサで測定した温度値を(独自)GATTで提供します  

- cq_ex13_ble_hum

	サンプル6 I2C接続センサ値をビーコンで送信  
	I2C接続の温湿度センサで測定した温度値と湿度値をBLE送信します  

- cq_ex13_ble_hum_le

	サンプル6-LE I2C接続センサ値をビーコンで送信 低消費電力版  
	I2C接続の温湿度センサで測定した温度値と湿度値をBLE送信します  

- cq_ex21_ble_led (次号以降で使用)

	サンプル7 BLE GATTによる双方向通信①  
	モジュール上のLEDの状態をBLEで遠隔制御します  

- cq_ex22_ble_sw (次号以降で使用)

	サンプル8 BLE GATTによる双方向通信②  
	モジュール上のDIPスイッチ又はPIRセンサの状態変化をBLEで通知します  

- tools

	各種サンプル・プログラムの動作確認をするためのツール類です。  
	
	- ble_logger_basic.py  
		Bluetooth LEビーコンをラズベリー・パイで受信します。  
	
	- ble_logger_rohm.py  
		上記の機能に加えセンサ値の保存やクラウド・サービスAmbientへの送信なども可能。  
	
	次号以降で使用するツールも含まれています。  

- LICENSE

	本ソフトウェアを配布するときは同梱してください。  

- README.md

	本説明書です。  

## ライセンス

ソースリストごとにライセンスが異なります。  
ライセンスについては各ソースリストならびに各フォルダ内のファイルに記載の通りです。  
使用・変更・配布は可能ですが、権利表示を残してください。  
また、提供情報や配布ソフトによって生じたいかなる被害についても，一切，補償いたしません。  

Copyright (c) 2020-2023 Wataru KUNINO
<https://bokunimo.net/>

----------------------------------------------------------------

## GitHub Pages (This Document)
* [https://git.bokunimo.com/lapis_mk715/](https://git.bokunimo.com/lapis_mk715/)  

----------------------------------------------------------------

# git.bokunimo.com GitHub Pages site
[http://git.bokunimo.com/](http://git.bokunimo.com/)  

----------------------------------------------------------------
