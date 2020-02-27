/*******************************************************************************
Lapis MK71511/MK71521用 サンプル・プログラム Example 12

モジュール内蔵の温度センサで測定した温度値をBLE送信します

                                          Copyright (c) 2020 Wataru KUNINO
                                          https://bokunimo.net/bokunimowakaru/
*******************************************************************************/

#include "main.c"                               // main.cの組み込み
#include "nrf_temp.h"                           // 内蔵温度センサ用ライブラリ
#include "nrf_delay.h"                          // 待ち時間処理用ライブラリ
#define INTERVAL_ms 1000                        // BLE送信間隔を1秒(1000)

uint8_t seq = 0;                                // 送信回数 0～255

float getTemp(){                                // 内蔵温度センサ値の取得関数
    int i=0;                                    // 待機時間保持用変数iに0を代入
    NRF_TEMP->TASKS_START = 1;                  // 温度測定の開始
    while(NRF_TEMP->EVENTS_DATARDY == 0){       // 温度値未取得のとき
        nrf_delay_ms(1);                        // 1ms待機
        i++;                                    // iに1を加算
        if(i>5) return -999.99;                 // 5msを超えた時-999.99を応答
    }
    NRF_TEMP->EVENTS_DATARDY = 0;               // 温度値取得フラグをリセット
    return (float)nrf_temp_read() / 4.;         // 温度値を応答
}

void setup(){                                   // 起動時に1回だけ実行する関数
    NRF_LOG_INFO("cq_ex12_ble_temp");           // タイトルのシリアル出力
    nrf_temp_init();                            // 内蔵温度センサの初期化
    ble_stack_init();                           // BLEスタックを初期化
}

void loop(){                                    // 繰り返し実行する関数
    bsp_board_led_on(2);                        // LED6(GPIO P19)をON
    uint8_t payload[6];                         // ビーコンデータ用変数を定義
    memset(payload,0,6);                        // 変数payloadの初期化
    
    float temp = getTemp();                     // 温度値を取得
    uint16_t temp16 = (uint16_t)((temp + 45.)*65536./175.); // 2バイトに変換
    payload[0] = (uint8_t)(temp16 % 256);       // 温度値の下位バイトを代入
    payload[1] = (uint8_t)(temp16 / 256);       // 温度値の上位バイトを代入
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
