/*******************************************************************************
Lapis MK71511/MK71521用 サンプル・プログラム Example 1

ディップスイッチDIP1～3の状態に応じて、LED4～LED7を点滅制御します。

DIP1(GPIO P13): bsp_board_button_state_get(0);
DIP2(GPIO P14): bsp_board_button_state_get(1);
DIP3(GPIO P15): bsp_board_button_state_get(2);
DIP4(GPIO P16): bsp_board_button_state_get(3);

LED4(GPIO P17): bsp_board_led_on(0); bsp_board_led_off(0);
LED5(GPIO P18): bsp_board_led_on(1); bsp_board_led_off(1);
LED6(GPIO P19): bsp_board_led_on(2); bsp_board_led_off(2);
LED7(GPIO P20): bsp_board_led_on(3); bsp_board_led_off(3);

                                          Copyright (c) 2020 Wataru KUNINO
                                          https://bokunimo.net/bokunimowakaru/
*******************************************************************************/

#include "main.c"                               // main.cの組み込み
#include "nrf_delay.h"                          // 待ち時間処理用ライブラリ
#define INTERVAL_ms 500                         // 動作間隔を0.5秒(500ms)に設定

void setup(){                                   // 起動時に1回だけ実行する関数
    printf("cq_ex01_led\n");                    // タイトルのシリアル出力
}

void loop(){                                    // 繰り返し実行する関数
    bool in;                                    // ブール型変数inを定義
    printf("Hello, world!\n");                  // 「Hello, world!」を表示
    for (int i = 0; i < 4; i++){                // i=0から3まで4回、繰り返す
        in = bsp_board_button_state_get(i);     // DIPスイッチiの状態を取得
        printf("Port(%d)=%d\n",i,in);           // 取得した内容を表示
        bsp_board_led_on(i);                    // LEDを点灯
        nrf_delay_ms(50);                       // 50msの短い待ち時間処理
        if(in){                                 // スイッチがONのとき
            bsp_board_led_off(i);               // すぐにLEDを消灯
        }
        nrf_delay_ms(INTERVAL_ms - 50);         // 50msを減算した待ち時間処理
    }
    bsp_board_leds_off();                       // 全てのLEDを消灯
}
