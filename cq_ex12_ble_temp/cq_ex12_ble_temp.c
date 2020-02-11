// BLE送信
#include "main.c"
#include "nrf_temp.h"
#include "nrf_delay.h"

uint8_t seq = 0;

float getTemp(){
    int i=0;
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
    printf("cq_ex12_ble_temp");
    ble_stack_init();
}

void loop(){
    bsp_board_led_on(1);
    uint8_t payload[6];
    memset(payload,0,6);
    
    float temp = getTemp();
    uint16_t temp16 = (uint16_t)((temp + 45.)*65536./175.);
    payload[0] = (uint8_t)(temp16 % 256);
    payload[1] = (uint8_t)(temp16 / 256);
    payload[5] = (uint8_t)seq;
    advertising_init(payload,6);
    advertising_start();
    for(int i=0;i<4;i++) idle_state_handle();
    advertising_stop();
    idle_state_handle();
    bsp_board_led_off(1);
    seq++;
    nrf_delay_ms(5000);
}
