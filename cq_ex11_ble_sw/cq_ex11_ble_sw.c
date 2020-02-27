/*******************************************************************************
Lapis MK71511/MK71521用 サンプル・プログラム Example 11

モジュール上のDIPスイッチの状態をBLE送信します

                                          Copyright (c) 2020 Wataru KUNINO
                                          https://bokunimo.net/bokunimowakaru/
*******************************************************************************/

#include "main.c"                               // main.cの組み込み
#include "nrf_delay.h"                          // 待ち時間処理用ライブラリ
#define INTERVAL_ms 1000                        // BLE送信間隔を1秒(1000)

uint8_t seq = 0;                                // 送信回数 0～255

void setup(){                                   // 起動時に1回だけ実行する関数
    NRF_LOG_INFO("cq_ex11_ble_sw");             // タイトルのシリアル出力
    ble_stack_init();                           // BLEスタックを初期化
}

void loop(){                                    // 繰り返し実行する関数
    bsp_board_led_on(2);                        // LED6(GPIO P19)をON
    uint8_t payload[6];                         // ビーコンデータ用変数を定義
    memset(payload,0,6);                        // 変数payloadの初期化
    
    for(int i=0;i<4;i++){
        payload[i] = bsp_board_button_state_get(i); // DIPスイッチiの状態を取得
    }
    payload[5] = (uint8_t)seq;                  // 送信番号を代入
    advertising_init(payload,6,INTERVAL_ms);    // ビーコンの初期化とデータ代入
    advertising_start();                        // ビーコンの送信開始
    nrf_delay_ms(10);                           // 送信の待ち時間処理
    idle_state_handle();                        // 送信待機
    advertising_stop();                         // 送信停止
    idle_state_handle();                        // 送信停止の待機
    bsp_board_led_off(2);                       // LED6(GPIO P19)をOFF
    seq++;                                      // 送信番号に1を加算
    nrf_delay_ms(INTERVAL_ms);                  // 送信間隔の待ち時間処理
}
