## Materials
- Test sample: 1/4" solid carbon fiber mandrel (2153T52 McMaster)

## Electrical Setup
- HY810H optical beam sensor
    - Diode side connected 5V -> 220 ohm resistor -> diode -> GND. Resistor drops voltage to ~1.2V at diode
    - Phototransistor side connected 5V -> "H" pin, "Y" pin -> 1M ohm resistor -> GND. Resistor keeps output voltage in range ~0-3V.

- NIDAQ USB6421
    - Supplies GND, 5V
    - AI0 connected to "Y" pin of HY810H
    - DI08 connected to ADMET start of test pin

## Procedure
Initial testing shows ~0.055" of usable range from the sensor. I zero the ADMET when the NIDAQ just starts seeing a falling signal from moving the rod downwards. The test profile moves to the 0 position at the center of the sensor's usable range, then moves sinusoidally across the sensor's whole usable range (0.055" p2p amplitude) at a rate of 1 cycle per 30 seconds.