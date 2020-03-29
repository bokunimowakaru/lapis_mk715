/*******************************************************************************
Lapis MK71511/MK71521用 サンプル・プログラム Example 22

モジュール上のDIPスイッチの状態変化をBLEで通知します

                                          Copyright (c) 2020 Wataru KUNINO
                                          https://bokunimo.net/bokunimowakaru/
*******************************************************************************/

#include "./main.c"                                 // main.cの組み込み

static void cq_lbs_rx_handler(uint8_t value){       // 制御指示をBLE受信したとき
    NRF_LOG_INFO("RX %d %d %d %d , hex = 0x%02x",
        (value >> 0) & 0x01,                        // RX1
        (value >> 1) & 0x01,                        // RX2
        (value >> 2) & 0x01,                        // RX3
        (value >> 3) & 0x01,                        // RX4
        value
    );
    if(value) bsp_board_led_on(1);                  // 0よりも大きいとき LED ON
    else      bsp_board_led_off(1);                 // 0のとき LED OFF
}

static uint8_t cq_lbs_tx_handler(uint8_t dipsw){    // DIPスイッチの変化時
    NRF_LOG_INFO("TX %d %d %d %d , hex = 0x%02x",
        (dipsw >> 0) & 0x01,                        // DIP1
        (dipsw >> 1) & 0x01,                        // DIP2
        (dipsw >> 2) & 0x01,                        // DIP3
        (dipsw >> 3) & 0x01,                        // DIP4
        dipsw
    );
    return dipsw;                                   // DIPスイッチの状態値を送信
}

void setup(){                                       // 起動時に1回だけ実行する
    NRF_LOG_INFO("cq_ex22_ble_sw");                 // タイトルのシリアル出力
    ble_stack_init();                               // BLEスタックを初期化
    gap_params_init("cq_ex22_ble_sw");              // BLEデバイス名を設定
    gatt_init();                                    // GATTの初期化
    services_init();                                // BLEサービスの初期化
    advertising_init();                             // アドバタイジングの初期化
    conn_params_init();                             // BLE接続設定値の初期化
    advertising_start();                            // BLEビーコン送信の開始
}

void loop(){                                        // 繰り返し実行する関数
    ;                                               // (BLE通信処理の繰り返し)
}

/*******************************************************************************
動作例

    <info> app_timer: RTC: initialized.
    <info> app: button state = 00
    <info> app: (Started)
    <info> app: cq_ex22_ble_sw
    <info> app: Connected
    
    <info> app: button pin_no = 13, action = 1
    <info> app: Send button state 00 change to 01
    <info> app: TX 1 0 0 0 , hex = 0x01
    <info> app: conn_handle = 0, value = 1
    <info> app: RX 1 0 0 0 , hex = 0x01
    
    <info> app: button pin_no = 14, action = 1
    <info> app: Send button state 01 change to 03
    <info> app: TX 1 1 0 0 , hex = 0x03
    <info> app: conn_handle = 0, value = 3
    <info> app: RX 1 1 0 0 , hex = 0x03
    
    <info> app: button pin_no = 13, action = 0
    <info> app: Send button state 03 change to 02
    <info> app: TX 0 1 0 0 , hex = 0x02
    <info> app: conn_handle = 0, value = 2
    <info> app: RX 0 1 0 0 , hex = 0x02
    
    <info> app: button pin_no = 14, action = 0
    <info> app: Send button state 02 change to 00
    <info> app: TX 0 0 0 0 , hex = 0x00
    <info> app: conn_handle = 0, value = 0
    <info> app: RX 0 0 0 0 , hex = 0x00
    
    <info> app: Disconnected


********************************************************************************
受信例

    pi@raspberrypi:~ $ sudo pip3 install bluepy
    pi@raspberrypi:~ $ git clone http://github.com/bokunimowakaru/lapis_mk715
    pi@raspberrypi:~ $ cd lapis_mk715/tools
    pi@raspberrypi:~/lapis_mk715/tools $ sudo ./ble_nordic_sw.py

    Device xx:xx:xx:xx:xx:xx (random), RSSI=-47 dB, Connectable=True
        9 Complete Local Name = cq_ex21_ble_led
    Notify config = 0100
    Waiting...

    Handle = 0xd , Notify = 01
        LED = ON

    Handle = 0xd , Notify = 03
        LED = ON

    Handle = 0xd , Notify = 02
        LED = ON

    Handle = 0xd , Notify = 00
        LED = OFF
    Device disconnected
*******************************************************************************/
