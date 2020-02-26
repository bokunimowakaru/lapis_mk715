/*********************************************************************
本ソースリストおよびソフトウェアは、ライセンスフリーです。(詳細は別記)
利用、編集、再配布等が自由に行えますが、著作権表示の改変は禁止します。

I2C接続の温湿度センサの値を読み取る
SILICON LABS社 Si7021
                               Copyright (c) 2017-2020 Wataru KUNINO
                               https://bokunimo.net/bokunimowakaru/
*********************************************************************/

// 参考資料：~/nRF5_SDK/examples/peripheral/twi_sensor

#include "i2c_si7021.h"

// #include "boards.h"
#include "nrf_drv_twi.h"
#include "nrfx_twim.h"
#include "nrf_delay.h"
// #include "nrf_gpio.h"

#define I2C_si7021     0x40             // Si7021 の I2C アドレス
#define I2C_si7021_SCL 26               // Si7021用 の SCLピン
#define I2C_si7021_SDA 27               // Si7021用 の SDAピン

float _i2c_si7021_hum = -1;
static volatile bool m_xfer_done = false;
static const nrf_drv_twi_t m_twi = NRF_DRV_TWI_INSTANCE(0);

float getTemp(){
    uint32_t e;
    uint8_t reg[2] = {0xF5,0};
    uint16_t temp,hum;
    _i2c_si7021_hum=-999.;
    
    m_xfer_done = false;
    e = nrf_drv_twi_tx(&m_twi, I2C_si7021, reg, 1, false);
    if(e) printf("si7021getHum, nrf_drv_twi_tx, APP_ERROR_CHECK:%x\n",e);
    do nrf_delay_ms(1); while(m_xfer_done == false);
    nrf_delay_ms(30);                  // 15ms以上
    
    m_xfer_done = false;
    e = nrf_drv_twi_rx(&m_twi, I2C_si7021, reg, 2);
    if(e) printf("si7021getHum, nrf_drv_twi_rx, APP_ERROR_CHECK:%x\n",e);
    do nrf_delay_ms(1); while(m_xfer_done == false);
    nrf_delay_ms(18);                  // 15ms以上
    
    hum = (reg[0] << 8) + reg[1];
    
    reg[0]=0xE0;
    
    m_xfer_done = false;
    e = nrf_drv_twi_tx(&m_twi, I2C_si7021, reg, 1, false);
    if(e) printf("si7021getTemp, nrf_drv_twi_tx, APP_ERROR_CHECK:%x\n",e);
    do nrf_delay_ms(1); while(m_xfer_done == false);
    nrf_delay_ms(30);                  // 15ms以上

    m_xfer_done = false;
    e = nrf_drv_twi_rx(&m_twi, I2C_si7021, reg, 2);
    if(e) printf("si7021getTemp, nrf_drv_twi_rx, APP_ERROR_CHECK:%x\n",e);
    do nrf_delay_ms(1); while(m_xfer_done == false);
    nrf_delay_ms(18);                  // 15ms以上
    
    temp = (reg[0] << 8) + reg[1];
    
    _i2c_si7021_hum = (float)hum / 65536. * 125. - 6.;
    return (float)temp / 65535. * 175.72 - 46.85;
}

float getHum(){
    float hum;
    if(_i2c_si7021_hum < 0) getTemp();
    hum = _i2c_si7021_hum;
    _i2c_si7021_hum = -1;
    return hum;
}

void twi_handler(nrf_drv_twi_evt_t const * p_event, void * p_context){
    if(p_event->type == NRF_DRV_TWI_EVT_DONE){
        m_xfer_done = true;
    }
}

void si7021Setup(){
    uint32_t e;
    printf("si7021Setup, nrf_drv_twi_config_t\n");
    printf(" I2C ADR = 0x%02x\n",I2C_si7021);
    printf("     SCL = P%02d\n",I2C_si7021_SCL);
    printf("     SDA = P%02d\n",I2C_si7021_SDA);
    /*
    nrf_gpio_cfg_output(I2C_si7021_GND);
    nrf_gpio_pin_write(I2C_si7021_GND,0);
    nrf_gpio_cfg_output(I2C_si7021_VDD);
    nrf_gpio_pin_write(I2C_si7021_VDD,1);
    */
    nrf_delay_ms(20);                   // 1ms以上
    
    const nrf_drv_twi_config_t twi_config = {
       .scl                = I2C_si7021_SCL,
       .sda                = I2C_si7021_SDA,
       .frequency          = NRF_DRV_TWI_FREQ_100K,
       .interrupt_priority = APP_IRQ_PRIORITY_HIGH,
       .clear_bus_init     = false
    };
    
    e = nrf_drv_twi_init(&m_twi, &twi_config, twi_handler, NULL);
    printf("si7021Setup, nrf_drv_twi_init, e=%x\n",e);
    nrf_drv_twi_enable(&m_twi);
    nrf_delay_ms(18);                  // 15ms以上
    
    uint8_t reg[2] = {0xE6, 0x3A};

    m_xfer_done = false;
    e = nrf_drv_twi_tx(&m_twi, I2C_si7021, reg, sizeof(reg), false);
    printf("si7021Setup, nrf_drv_twi_tx, e=%x\n",e);
    do nrf_delay_ms(1); while(m_xfer_done == false);
    nrf_delay_ms(18);                  // 15ms以上
}
