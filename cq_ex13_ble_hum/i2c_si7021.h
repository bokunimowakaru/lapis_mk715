#ifndef SI7021_H__
#define SI7021_H__

#ifdef __cplusplus
extern "C" {
#endif

#include "nrf_drv_twi.h"

float getTemp();
float getHum();
void twi_handler(nrf_drv_twi_evt_t const * p_event, void * p_context);
void si7021Setup();

#ifdef __cplusplus
}
#endif

#endif // SI7021_H__
