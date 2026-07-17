The [configuration tool](https://configtool.reprapfirmware.org/Configuration) along with the [json file](configtool.json) are used to generate the firmware configuration bundle that can be uploaded to the Duet board via the [DWC browser](http://192.168.2.14/Console).

## Kinematics
We're using a CoreXY type printer

## Accessories
Enable Direct Display should be checked and we're using an ST7567 type display (the BigTreeTech 12864 Mini V2)
TODO make this display work

## LED Strips
None for now

## Network

I'm using only direct-connect via ethernet because WPI's network is too restrictive to make anything else work (I think).

We want a static IP address, so under "Configure Ethernet" deselect "Acquire dynamic IP address via DHCP" and set the static IP Address and Subnet Mask following the [networking doc](Connecting_to_Duet.txt).

## Expansion
We're using an Duet3 Mini 2+ for the extruder motors

## Accelerometers
None

## Smart Drivers
The drivers used for the X and Y motors need to be in StealthChop mode for sensorless homing. All other axes can stay in SpreadCycle mode as it gets better performance.

| Driver | Associated Axis | Peak Current (mA) | Mode        |
|--------|-----------------|-------------------|-------------|
| 0.0    | Z               | 1000              | SpreadCycle |
| 0.1    | Z               | 1000              | SpreadCycle |
| 0.2    | X               | 1200              | StealthChop |
| 0.3    | Y               | 1200              | StealthChop |
| 0.4    | Theta (U)       | 1500              | SpreadCycle |
| 0.5    | E1              | 800               | SpreadCycle |
| 0.6    | E2              | 800               | SpreadCycle |

## Motor Current Reduction
Using default values

## Axes
Added the U axis for theta. See the table in the *Smart Drivers* section for which drivers are attatched to which axes. All axes use 16x microstepping.

### Microsteps per mm
I used the built-in calculator for these values
For X and Y axis motors: **80**
- belt pitch: 2mm
- driven pulley tooth count: 20
- motor steps per revolution: 200
- microstepping multiplier: 16

For Z motors: **1600**
- leadscrew pitch: 2mm
- gear ratio 1:1
- motor steps per revolution: 200
- microstepping multiplier: 16

For theta motor: **160.408**
we want the base layer of the 3D print when it's projected flat on the slicing plane to be π*1/4" or the circumference of the mandrel. Thus, a full revolution of the theta axis motor (which is 1:1 coupled to the mandrels) must correspond to a "distance" of 19.9491 mm. That's to say the steps/mm should be:

200 steper per rev \* 16 microsteps per step / 19.491 mm/rev = 160.408 microsteps/mm