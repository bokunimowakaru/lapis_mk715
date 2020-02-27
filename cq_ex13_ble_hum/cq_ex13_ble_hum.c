/*******************************************************************************
Lapis MK71511/MK71521用 サンプル・プログラム Example 13

I2C接続の温湿度センサで測定した温度値と湿度値をBLE送信します

                                          Copyright (c) 2020 Wataru KUNINO
                                          https://bokunimo.net/bokunimowakaru/
*******************************************************************************/

#include "i2c_si7021.h"                         // 温湿度センサ用ライブラリ
#include "main.c"                               // main.cの組み込み
#include "nrf_delay.h"                          // 待ち時間処理用ライブラリ
#define INTERVAL_ms 1000                        // BLE送信間隔を1秒(1000ms)

uint8_t seq = 0;                                // 送信回数 0～255

void setup(){                                   // 起動時に1回だけ実行する関数
    NRF_LOG_INFO("cq_ex13_ble_hum");            // タイトルのシリアル出力
    si7021Setup();                              // センサSi7021の初期化
    ble_stack_init();                           // BLEスタックを初期化
}

void loop(){                                    // 繰り返し実行する関数
    bsp_board_led_on(2);                        // LED6(GPIO P19)をON
    uint8_t payload[6];                         // ビーコンデータ用変数を定義
    memset(payload,0,6);                        // 変数payloadの初期化
    
    float temp = getTemp();                     // 温度値を取得し変数tempへ
    float humi = getHum();                      // 湿度値を取得し変数humiへ
    uint16_t temp16 = (uint16_t)((temp + 45.)*65536./175.); // 2バイトに変換
    uint16_t humi16 = (uint16_t)(humi * 65536./100.); // 2バイトに変換
    payload[0] = (uint8_t)(temp16 % 256);       // 温度値の下位バイトを代入
    payload[1] = (uint8_t)(temp16 / 256);       // 温度値の上位バイトを代入
    payload[3] = (uint8_t)(humi16 % 256);       // 湿度値の下位バイトを代入
    payload[4] = (uint8_t)(humi16 / 256);       // 湿度値の上位バイトを代入
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
