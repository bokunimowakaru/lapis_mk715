/*******************************************************************************
Lapis MK71511/MK71521用 サンプル・プログラム Example 21

モジュール上のLEDの状態をBLEで遠隔制御します

                                          Copyright (c) 2020 Wataru KUNINO
                                          https://bokunimo.net/bokunimowakaru/
*******************************************************************************/

#include "./main.c"                                 // main.cの組み込み

static void cq_lbs_rx_handler(uint8_t value){       // 制御指示をBLE受信したとき
    if(value){                                      // 指示値が0よりも大きいとき
        NRF_LOG_INFO("LED ON");                     // LED ONを表示
        bsp_board_led_on(1);                        // LED5(GPIO P18)をON
    }else{                                          // 指示値が0のとき
        NRF_LOG_INFO("LED OFF");                    // LED OFFを表示
        bsp_board_led_off(1);                       // LED5(GPIO P18)をOFF
    }
}

static uint8_t cq_lbs_tx_handler(uint8_t dipsw){    // DIPスイッチの変化時
    return dipsw;                                   // DIPスイッチの状態値を送信
}

void setup(){                                       // 起動時に1回だけ実行する
    NRF_LOG_INFO("cq_ex21_ble_led");                // タイトルのシリアル出力
    ble_stack_init();                               // BLEスタックを初期化
    gap_params_init("cq_ex21_ble_led");             // BLEデバイス名を設定
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
    <info> app: (Started)
    <info> app: cq_ex21_ble_led
    <info> app: Connected
    <info> app: conn_handle = 0, value = 1
    <info> app: LED ON
    <info> app: Disconnected
    <info> app: Connected
    <info> app: conn_handle = 0, value = 0
    <info> app: LED OFF
    <info> app: Disconnected
    
    <info> app_timer: RTC: initialized.
    <info> app: (Started)
    <info> app: cq_ex21_ble_led
    <info> app: Connected
    <info> app: button pin_no = 13, action = 1
    <info> app: Send button state change.
    <info> app: conn_handle = 0, value = 1
    <info> app: LED ON
    <info> app: button pin_no = 13, action = 0
    <info> app: Send button state change.
    <info> app: conn_handle = 0, value = 0
    <info> app: LED OFF

********************************************************************************
受信例

    pi@raspberrypi:~ $ git clone http://github.com/bokunimowakaru/lapis_mk715
    pi@raspberrypi:~ $ cd lapis_mk715/tools
    pi@raspberrypi:~/lapis_mk715/tools $ sudo ./ble_nordic_led.py

    Device xx:xx:xx:xx:xx:xx (random), RSSI=-49 dB, Connectable=True
        9 Complete Local Name = cq_ex21_ble_led
        LED = ON

    Device xx:xx:xx:xx:xx:xx (random), RSSI=-58 dB, Connectable=True
        9 Complete Local Name = cq_ex21_ble_led
        LED = OFF

    ----------------------------------------------------------------------------
    pi@raspberrypi:~/lapis_mk715/tools $ sudo ./ble_nordic_sw.py

    Device xx:xx:xx:xx:xx:xx (random), RSSI=-47 dB, Connectable=True
        9 Complete Local Name = cq_ex21_ble_led
    Notify config = 0100
    Waiting...

    Handle = 0xd , Notify = 01
        LED = ON

    Handle = 0xd , Notify = 00
        LED = OFF

    Handle = 0xd , Notify = 01
        LED = ON

    Handle = 0xd , Notify = 00
        LED = OFF

*******************************************************************************/
