// Reads both MyoWare sensors every 1 ms and prints them over USB as "flexor,extensor".
// Create the project with the Raspberry Pi Pico VS Code extension (Console over USB),
// add hardware_adc to target_link_libraries in its CMakeLists.txt, then use this file.

#include <stdio.h>
#include "pico/stdlib.h"
#include "hardware/adc.h"

int main(void) {
    stdio_init_all();
    adc_init();
    adc_gpio_init(26);   // ADC0: sensor 1 RAW output
    adc_gpio_init(27);   // ADC1: sensor 2 RAW output

    absolute_time_t next = get_absolute_time();
    while (true) {
        next = delayed_by_us(next, 1000);   // fixed 1 ms schedule, so the rate doesn't drift
        adc_select_input(0);
        uint16_t flexor = adc_read();
        adc_select_input(1);
        uint16_t extensor = adc_read();
        printf("%u,%u\n", flexor, extensor);
        sleep_until(next);
    }
}
