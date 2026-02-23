#include <firmware_apis.h>
#include "CF_TMR32.h"

// -------------------------------
// CF_TMR32 base addresses
// -------------------------------
#define PWM0_BASE  0x30000000
#define PWM3_BASE  0x30030000
#define PWM6_BASE  0x30060000
#define PWM9_BASE  0x30090000

#define PWM0 ((CF_TMR32_TYPE_PTR)PWM0_BASE)
#define PWM3 ((CF_TMR32_TYPE_PTR)PWM3_BASE)
#define PWM6 ((CF_TMR32_TYPE_PTR)PWM6_BASE)
#define PWM9 ((CF_TMR32_TYPE_PTR)PWM9_BASE)

void main(void)
{
    // Housekeeping & pads
    enableHkSpi(false);

    // GPIOs driven by the PWM outputs
    GPIOs_configure(5,  GPIO_MODE_USER_STD_OUTPUT);
    GPIOs_configure(8,  GPIO_MODE_USER_STD_OUTPUT);
    GPIOs_configure(11, GPIO_MODE_USER_STD_OUTPUT);
    GPIOs_configure(14, GPIO_MODE_USER_STD_OUTPUT);

    GPIOs_loadConfigs();
    User_enableIF();

    // 1) Signal: firmware ready / pads configured
    vgpio_write_output(1);

    // Configure example PWM on 4 instances
    CF_TMR32_configureExamplePWM(PWM0);
    CF_TMR32_configureExamplePWM(PWM3);
    CF_TMR32_configureExamplePWM(PWM6);
    CF_TMR32_configureExamplePWM(PWM9);

    // 2) Signal: peripherals enabled
    vgpio_write_output(2);

    // (Optional) small warm-up busy-wait
    for (volatile int i = 0; i < 1000; ++i) { }

    // 3) Signal: begin data/sample phase
    vgpio_write_output(3);

    // Idle forever; testbench will observe pins
    while (1) { }
}
