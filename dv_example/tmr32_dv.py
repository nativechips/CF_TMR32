

import cocotb
from cocotb.triggers import ClockCycles
from caravel_cocotb.caravel_interfaces import test_configure, report_test
from caravel_cocotb.caravel_interfaces import VirtualGPIOModel

@cocotb.test()
@report_test
async def tmr32_dv(dut):
    caravelEnv = await test_configure(dut, timeout_cycles=500_000)
    cocotb.log.info("[TEST] Starting tmr32_dv (VGPIO-based)")

    await caravelEnv.release_csb()

    # Start Virtual GPIO model (listens to 0x30FFFFFC)
    vgpio = VirtualGPIOModel(caravelEnv)
    vgpio.start()

    # Handshake sequence via VGPIO
    await vgpio.wait_output(1)
    cocotb.log.info("[TEST] Firmware ready (pads configured)")

    await vgpio.wait_output(2)
    cocotb.log.info("[TEST] PWM instances enabled")

    await vgpio.wait_output(3)
    cocotb.log.info("[TEST] Entering sampling phase")

    # Allow some settling time
    await ClockCycles(caravelEnv.clk, 10_000)

    # Sample four GPIOs for 5000 cycles
    sample_cycles = 5000
    pins = [5, 8, 11, 14]

    highs = {p: 0 for p in pins}
    lows  = {p: 0 for p in pins}

    for _ in range(sample_cycles):
        await ClockCycles(caravelEnv.clk, 1)
        for p in pins:
            val = caravelEnv.monitor_gpio(p, p).integer
            if val == 1:
                highs[p] += 1
            else:
                lows[p] += 1

    # Compute duty cycles
    def duty(p):
        total = highs[p] + lows[p]
        return (highs[p] / total * 100.0) if total else 0.0

    cocotb.log.info(
        "[TEST] Results:\n"
        f"  GPIO 5 : {highs[5]} high,  {lows[5]} low,  duty={duty(5):.2f}%\n"
        f"  GPIO 8 : {highs[8]} high,  {lows[8]} low,  duty={duty(8):.2f}%\n"
        f"  GPIO 11: {highs[11]} high, {lows[11]} low, duty={duty(11):.2f}%\n"
        f"  GPIO 14: {highs[14]} high, {lows[14]} low, duty={duty(14):.2f}%"
    )

    # Basic toggling checks: both high and low counts should be "significant"
    test_passed = True
    threshold = 100  # same spirit as your original check

    for p in pins:
        if highs[p] > threshold and lows[p] > threshold:
            cocotb.log.info(f"[TEST] GPIO {p} PWM toggling - PASS")
        else:
            cocotb.log.error(f"[TEST] GPIO {p} PWM NOT toggling - FAIL")
            test_passed = False

    if test_passed:
        cocotb.log.info("[TEST] tmr32_dv complete - PASS")
    else:
        cocotb.log.error("[TEST] tmr32_dv complete - FAIL")
