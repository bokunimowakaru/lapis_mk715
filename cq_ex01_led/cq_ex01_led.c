#include "main.c"

void setup(){
    printf("cq_ex01_led\n");
}

void loop(){
    bool in;
    printf("Hello, world!\n");
    for (int i = 0; i < 4; i++){
        in = bsp_board_button_state_get(i);
        printf("Port(%d)=%d\n",i,in);
        bsp_board_led_on(i);
        nrf_delay_ms(50);
        if(in){
            bsp_board_led_off(i);
        }
        nrf_delay_ms(450);
    }
    bsp_board_leds_off();
}
