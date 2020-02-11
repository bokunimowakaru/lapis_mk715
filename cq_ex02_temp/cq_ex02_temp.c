#include "main.c"
#include "nrf_temp.h"
#include "nrf_delay.h"

float getTemp(){
    int i=0;
    bsp_board_led_on(2);
    NRF_TEMP->TASKS_START = 1;
    while(NRF_TEMP->EVENTS_DATARDY == 0){
        nrf_delay_ms(1);
        i++;
        if(i>5) return -999.99;
    }
    NRF_TEMP->EVENTS_DATARDY = 0;
    return (float)nrf_temp_read() / 4.;
}

void setup(){
    nrf_temp_init();
    printf("cq_ex02_temp\n");
}

void loop(){
    int temp;
    bsp_board_led_on(1);
    temp = (int)(10. * getTemp());
    printf("Temperature   = %d.%1d\n", temp/10, temp%10);
    bsp_board_leds_off();
    nrf_delay_ms(500);
}
