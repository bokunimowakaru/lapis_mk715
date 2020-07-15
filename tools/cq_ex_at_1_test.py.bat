@echo off

rem ################################################################################
rem # BLE AT Sender cq_ex_at_1_test.py 起動用 Windows BATファイル
rem #
rem # LAPIS MK715 ATコマンド・モード用です。
rem # PCを起動したときにラズベリー・パイと接続し、PC起動後の経過時間を知らせます
rem #
rem # ・LAPIS MK715のシリアルCOMポート番号を「COM3」の部分に書いてください。
rem # ・ショートカットを、Windowsスタートアップ・フォルダに保存しておいてください。
rem #
rem #                                          Copyright (c) 2020 Wataru KUNINO
rem ################################################################################

rem                          ↓ MK715開発ボードのCOMポート
python3 cq_ex_at_1_test.py COM3
pause
