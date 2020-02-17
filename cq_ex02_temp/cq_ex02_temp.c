/*******************************************************************************
Lapis MK71511/MK71521用 サンプル・プログラム Example 2

モジュール内蔵の温度センサの値を読み取ります

                                          Copyright (c) 2020 Wataru KUNINO
                                          https://bokunimo.net/bokunimowakaru/
*******************************************************************************/

#include "main.c"                               // main.cの組み込み
#include "nrf_temp.h"                           // 内蔵温度センサ用ライブラリ
#include "nrf_delay.h"                          // 待ち時間処理用ライブラリ
#define INTERVAL_ms 1000                        // 動作間隔を1秒(1000ms)に設定

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
    printf("cq_ex02_temp\n");                   // プログラム名をシリアル出力
    nrf_temp_init();                            // 内蔵温度センサの初期化
}

void loop(){                                    // 繰り返し実行する関数
    int temp;                                   // 温度値を保持するための変数
    bsp_board_led_on(1);                        // LED5(GPIO P18)をON
    temp = (int)(10. * getTemp());              // 温度値を取得
    printf("Temperature   = %d.%1d\n", temp/10, temp%10);   // 温度値を出力
    bsp_board_leds_off();                       // 全てのLEDをOFF
    nrf_delay_ms(INTERVAL_ms);                  // 待ち時間処理
}
