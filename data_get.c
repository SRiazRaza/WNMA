

#include <stdio.h>
#include "stdlib.h"
#include "hardware/pwm.h"
#include "hardware/clocks.h"

// Measures PWM on this pin
const uint PINS [] = {3,5,7,9,11,13};

float measure_duty_cycle(uint gpio) {
    // Only the PWM B pins can be used as inputs.
    assert(pwm_gpio_to_channel(gpio) == PWM_CHAN_B);
    uint slice_num = pwm_gpio_to_slice_num(gpio);

    // Count once for every 100 cycles the PWM B input is high
    pwm_config cfg = pwm_get_default_config();
    pwm_config_set_clkdiv_mode(&cfg, PWM_DIV_B_HIGH);
    pwm_config_set_clkdiv(&cfg, 100);
    pwm_init(slice_num, &cfg, false);
    gpio_set_function(gpio, GPIO_FUNC_PWM); 

    pwm_set_enabled(slice_num, true);
    sleep_ms(10);
    pwm_set_enabled(slice_num, false);
    float counting_rate = clock_get_hz(clk_sys) / 100;
    float max_possible_count = counting_rate * 0.01;
    return pwm_get_counter(slice_num) / max_possible_count;
}



int main() {
    stdio_init_all();

    while (true) {
        printf("Reading\n");
        sleep_ms(1000);

    for (int i = 5; i >= 0; --i) {
        float measured_duty_cycle1 = measure_duty_cycle(PINS[i]);
	// read twice and uses highest value
	float measured_duty_cycle2 = measure_duty_cycle(PINS[i]);
	float pin_value = measured_duty_cycle1 > measured_duty_cycle2 ? measured_duty_cycle1 : measured_duty_cycle2;
	pin_value *= 100;
	// if 0 then not connected / switched off
	if (pin_value < 0.1) 
	    {
	    printf ("Input %d * Turned off *\n",6-i);
	    }
	// minimum duty cycle is 10, max is 20
	else if (pin_value < 10 || pin_value > 20)
	    {
	    printf ("Input %d ** Invalid **\n",6-i);
	    }
        else printf("Input %d = %.1f%%\n", 6-i,
               pin_value );
	sleep_ms(10);
    }



    }
    return 0;
}
