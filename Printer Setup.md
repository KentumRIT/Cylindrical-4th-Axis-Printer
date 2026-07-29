# Useful Links
https://docs.duet3d.com/User_manual/Machine_configuration/Networking
https://docs.duet3d.com/User_manual/Overview/Getting_started_Duet_3_Mini_5+
https://docs.duet3d.com/How_to_guides/Getting_connected/Getting_connected_to_your_Duet
https://docs.duet3d.com/User_manual/Reference/Duet_Web_Control_Manual
https://docs.duet3d.com/User_manual/Reference/Gcodes
https://docs.duet3d.com/How_to_guides/Configuring_firmware

# Configuration
RepRap firmware has an online [configuration tool](https://configtool.reprapfirmware.org/Configuration), which along with our [json file](configtool.json) is used to generate config files that can be uploaded to the Duet board via [Duet Web Control](https://docs.duet3d.com/User_manual/Reference/Duet_Web_Control_Manual). The following section walks through decisions made when filling out the configuration tool and any additional modifications to config files needed.

## General
Our board is the Duet 3 Mini 5+ Ethernet

## Kinematics
We're using a CoreXY type printer

## Accessories
Enable Direct Display should be checked. We're using an ST7567 type display (the BigTreeTech 12864 Mini V2)

**TODO**: make this display work

## LED Strips
None for now

## Network
We're directly connecting the Duet board to a computer via ethernet because WPI's network is too restrictive to make anything else work (I think). For this we want a static IP address, so under "Configure Ethernet" deselect "Acquire dynamic IP address via DHCP" and set the static IP Address and Subnet Mask to 192.168.2.14 and 255.255.255.0 respectively.

## Expansion
We're using an Duet 3 Mini 2+ for the extruder motors

## Accelerometers
None

## Smart Drivers
The drivers used for the X and Y motors need to be in StealthChop mode for sensorless homing. All other axes can stay in SpreadCycle mode as it gets better performance.

| Driver | Associated Axis | Peak Current (mA) | Mode        |
|--------|-----------------|-------------------|-------------|
| 0.0    | Z               | 1000              | SpreadCycle |
| 0.1    | Z               | 1000              | SpreadCycle |
| 0.2    | X/Y             | 1200              | StealthChop |
| 0.3    | Y/Y             | 1200              | StealthChop |
| 0.4    | Theta (U)       | 1500              | SpreadCycle |
| 0.5    | E0              | 800               | SpreadCycle |
| 0.6    | E1              | 800               | SpreadCycle |

## Motor Current Reduction
Using default values (30% idle current and 30s timeout)

## Axes
- Along with X, Y, and Z axes, added the U axis for theta. See the table in [Smart Drivers](#smart-drivers) section for which drivers are attatched to which axes.
- All axes use 16x microstepping.
- All axes use default Max. Speed Change, Max. Speed, and Acceleration

### Axis Minimum and Maximums
The X, Y, and Z axes each have a minimum of 0. To get the maximum values for these axes, I measured the distance between the hard stops in each axis and subtracted the carriage length to get the maximum travel. The theta axis must be capable of rotating more than one revolution, so I just picked really big numbers. This gives:
|  Axis  |   Minimum (mm)  |    Maximum (mm)   |
|--------|-----------------|-------------------|
| X      | 0               | 1000              |
| Y      | 0               | 1000              |
| Z      | 0               | 1200              |
| U      | -999999999      | 999999999         |

### Microsteps per mm
I used the built-in calculator for these values
For X and Y axis motors: **80**
- belt pitch: 2 *mm*
- driven pulley tooth count: 20
- motor steps per revolution: 200
- microstepping multiplier: 16

For Z motors: **1600**
- leadscrew pitch: 2 *mm*
- gear ratio 1:1
- motor steps per revolution: 200
- microstepping multiplier: 16

For theta motor: **160.408**
We want the base layer of the 3D print when it's projected flat on the slicing plane to be π × 1/4"—the circumference of the mandrel. Thus, a full revolution of the theta axis motor (which is 1:1 coupled to the mandrels) must correspond to a "distance" of 19.9491 *mm*. That's to say the steps/mm should be:

200 *steps per rev* × 16 *microsteps per step* / 19.491 *mm/rev* = 160.408 *microsteps/mm*

## Extruders
**TODO**: Measure extruder steps per mm

## Filament Monitors
The Nextruder filament monitors work at 3.3V, so it makes sense to use io5 and io6 (input-only pins @ 3.3V) for this task

## Z-Probes
Z probing will be done by the force sensor built into the Nextruder heatsink. An ESP32 communicating with an HX711 chip will convert that force signal to a digital signal for probing because the Duet board can't directly read the load cell signal. Thus, we use a digital probe type. We use the io0 port for this because it has a 5V level which can energize the load cell and power the ESP32

## Endstops
X and Y directions use "Single Motor Load Detection", Z uses extruder probe setup in prev section, and theta uses an optical limit switch (Switch type on io1).

### XY Load Detection
Looking at the notes for load detection, they want a speed minimum of 200 full steps per second (or 1 rps for the motor shaft). For the X and Y axes, this equates to a linear speed of:

- 200 steps/second * 16 microsteps/step = 3200 microsteps/s
- (3200 microsteps/s) / (80 microsteps/mm) = **40 mm/s**

I'll probe then 2x at 40 mm/s

If I just tried using the configuration files given by the online reprap config tool, I'd get a warning that 40 mm/s is both too slow AND too fast for homing. The Duet thinks it's too slow because it gives a bit of tolerance on the 40 mm/s (2400 mm/min) minimum. The Duet thinks 40 mm/s is too fast because the default M569 tpwmthrs value brings the motor out of StealthChop mode (which is needed for sensorless homing) at very low speeds. 

To fix the above issues, I had to add code beyond what the online config tool provided. These lines were added to `homeall.g`, `homex.g`, and `homey.g`:

```
; set homing parameters
; set homing parameters
M915 X Y S5 H170 R0     ; lower minimum speed threshold with H parameter
M913 X50 Y50            ; drop current to 50% to reduce belt-slip risk while homing
M569 P2 V10             ; stay in stealthchop mode at higher speeds
M569 P3 V10             ; stay in stealthchop mode at higher speeds


; homing code here...

; revert parameters
M915 X Y S3 H200        ; S3 and H200 are default values
M913 X100 Y100          ; use 100% motor power after homing
M569 P2 V2000           ; get default tpwmthrs value by running "M569 P2" in console
M569 P3 V2000

```

### Theta Axis Homing
When the theta axis homes, it will think it's at the low end of its travel range (-9999999). We want it to be at 0 when homed so that it can spin freely in either direction without hitting a travel limit, thus we have to add the following to `homeu.g`:
```
; homing gcode

G92 U0  ; make current position theta = 0
```
## Compensation
N/A

## Sensors
Thermistors are connected to ports temp1 and temp2 (print bed would be temp0)

## Heaters
Nozzles are connected to out1 and out2 (print bed would be out0)

## Fans
- Fan 0 and Fan 1 are heatsink fans for nozzles, but need to be pin active low
- Fan 2 and Fan 3 are part cooling fans on out 5 and out 6

## Tools
- Tool 0 is connected to fans 0 and 2
- Tool 1 ais connected to fans 1 and 3

# Connecting To The Duet Board
When configuring firmware, we set the Duet board's IP address to `192.168.2.14`. We'll be setting up a **wired direct connection** as described in the [Duet Networking Documentation](https://docs.duet3d.com/User_manual/Machine_configuration/Networking). The steps necessary to connect to a general Duet board are described in [this documentation](https://docs.duet3d.com/How_to_guides/Getting_connected/Getting_connected_to_your_Duet), but I'll include our specific steps here:

1) On a Windows machine go to: Control Panel > Network and Internet > Network and Sharing Center > Change Adapter Settings > Ethernet > Properties > Internet Protocol Version 4 (TCP/IPv4) Properties

2) Select "Use the following IP address" and: 
    - Enter IP: `192.168.2.13`, the same IP as the Duet board with the last digits changed
    - Set the subnet mask to `255.255.255.0`
    - Leave the default gateway blank
    - Select "ok" and exit out of the network menus

1) Connect your Duet board to your computer via USB while the Duet board is not connected to its power supply unit

2) Install USB drivers for the Duet board, [this link](https://github.com/Duet3D/RepRapFirmware/releases/download/2.05.1/DuetDriverFiles.zip) may be old

3) Install a serial terminal software like [YAT](https://sourceforge.net/projects/y-a-terminal/) on your computer and connect to the Duet
    - Make sure "DTR on" is selected in terminal settings
    - Set EOL (end of line) sequence to \<LF\> in text settings

4) Disable the network module with `M552 S0`

5) Enable the network module with the desired IP address with `M552 S1 P192.168.2.14`; the Duet should return "Network running" after 10-30 seconds

6) Enter the [Duet's IP address](http://192.168.2.14/) into your browser; you should be directed to Duet Web Control (DWC)

7) On DWC, navigate to System > Upload System Files and select the zipped folder generated by the configuration tool

8) Reset the Duet with the reset button on its side. DWC will say it's lost connection, but it should reconnect. If DWC doesn't reconnect properly you'll need to go back to your serial terminal and troubleshoot from step 6


