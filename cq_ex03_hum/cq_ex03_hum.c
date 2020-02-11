// I2C接続の温湿度センサの値を読み取る
// SILICON LABS社 Si7021

// I2C_si7021     0x40             // Si7021 の I2C アドレス
// I2C_si7021_SCL 26               // Si7021用 の SCLピン
// I2C_si7021_SDA 27               // Si7021用 の SDAピン

#include "main.c"
#include "i2c_si7021.c"
#include "nrf_delay.h"

void setup(){
    printf("cq_ex03_hum\n");
    si7021Setup();
}

void loop(){
    int temp,humi;
    bsp_board_led_on(1);
    temp = (int)(10. * getTemp());
    printf("Temperature   = %d.%1d\n", temp/10, temp%10);
    humi = (int)(10. * getHum());
    printf("Humidity      = %d.%1d\n", humi/10, humi%10);
    bsp_board_leds_off();
    nrf_delay_ms(500);
}
