/*******************************************************************************
Lapis MK71511/MK71521用 サンプル・プログラム Example 3

I2C接続の温湿度センサの値を読み取ります
SILICON LABS社 Si7021

                                          Copyright (c) 2020 Wataru KUNINO
                                          https://bokunimo.net/bokunimowakaru/
*******************************************************************************/

#include "main.c"                               // main.cの組み込み
#include "i2c_si7021.h"                         // 温湿度センサ用ライブラリ
#include "nrf_delay.h"                          // 待ち時間処理用ライブラリ
#define INTERVAL_ms 500                         // 動作間隔を0.5秒(500ms)に設定

void setup(){                                   // 起動時に1回だけ実行する関数
    printf("cq_ex03_hum\n");                    // タイトルのシリアル出力
    si7021Setup();                              // センサSi7021の初期化
}

void loop(){                                    // 繰り返し実行する関数
    int temp,humi;                              // 温度値と湿度値を保持する変数
    bsp_board_led_on(1);                        // LED5(GPIO P18)をON
    temp = (int)(10. * getTemp());              // 温度値を取得し変数tempへ
    printf("Temperature = %d.%1d, ", temp/10, temp%10); // 温度値を表示
    humi = (int)(10. * getHum());               // 湿度値を取得し変数humiへ
    printf("Humidity = %d.%1d\n", humi/10, humi%10);    // 湿度値を表示
    bsp_board_leds_off();                       // 全てのLEDをOFF
    nrf_delay_ms(INTERVAL_ms);                  // 待ち時間処理
}

/*******************************************************************************
I2C接続の温湿度センサ SILICON LABS社 Si7021 の値を取得する

    I2C_si7021     0x40             // Si7021 の I2C アドレス
    I2C_si7021_SCL 26               // Si7021用 の SCLピン
    I2C_si7021_SDA 27               // Si7021用 の SDAピン
    
    温度    getTemp()
    湿度    getHum()

********************************************************************************
動作例

    (Started)
    cq_ex03_hum
    si7021Setup, nrf_drv_twi_config_t
     I2C ADR = 0x40
         SCL = P26
         SDA = P27
    si7021Setup, nrf_drv_twi_init, e=0
    si7021Setup, nrf_drv_twi_tx, e=0
    Temperature = 17.5, Humidity = 68.8
    Temperature = 17.5, Humidity = 68.7
    Temperature = 17.5, Humidity = 68.7

*******************************************************************************/
