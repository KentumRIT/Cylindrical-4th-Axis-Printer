# Experimental Aim
We will investigate how various 3D printing parameters affect the strength of plastic adhesion to the braided mesh substrate in our cylindrical FFF printing setup.

# Experimental Design
## Inititial Factors
We first made a list of all controllable factors we thought would have an effect on adhesion strength through intuition and literature review. Our initial thoughts are listed below:

| Factor                                              | Lit Review Findings                                                                                                | Are We Testing This Parameter                                                                                                                                                                                                                                                                                                                                                                   | Anticipated Interactions | Anticipated Main Effect                                                                                                                                                                                                                                     | Anticipated Range | Anticipated Levels          |
|-----------------------------------------------------|--------------------------------------------------------------------------------------------------------------------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|--------------------------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|-------------------|-----------------------------|
| **Printing Temperature:** Temp defined for first layer, with second layer taking the mid-point between the first layer temp and the standard printing temp (220 C) | Linear effect with higher temperatures yielding stronger adhesion                                                  | **Yes** Although all literature review data suggests higher temperatures yield stronger adhesion, two factor interactions are likely to be significant with this parameter.                                                                                                                                                                                                                     |                          | **Linear** Higher temp = stronger adhesion                                                                                                                                                                                                                  | 190 - 280 C       | **2** (Linear)              |
| **Ironing:** Number of passes over the first layer without extrusion                                             | N/A                                                                                                                | **Yes** It would be nice if we could get good adhesion without this parameter, as it requires G-code manipulation so raises the barrier to entry for this fabrication. However, through manual testing it seems nearly essential to getting good results.                                                                                                                                       |                          | **Linear or Saturating** More ironing passes = stronger adhesion with weakening effect from more passes                                                                                                                                                     | 0 - 2 repeats     | **2** (Linear/Saturating)   |
| **Ironing Speed:** Move speed for ironing moves                                       | N/A                                                                                                                | **No** We haven't modified this yet, and we don't have data from prior literature to support that this matters. However, it makes sense that we'd want the plastic to be exposed to the nozzle during ironing for longer to get better adhesion.                                                                                                                                                |                          | **Linear or Saturating** More time under the nozzle during ironing will increase strength up until complete plastic infiltration                                                                                                                            |                   | **2-5** (Linear/Saturating) |
| **Printing Speed:** Speed defined using a multiplier of the standard print speed settings. Defined for first layer, with second layer taking the mid-point between the first layer speed and 1.                                         | Quadratic effect with peak adhesion strength at a medium speed                                                     | **Yes** The effect was significant, but weak in the paper we found. However, I feel like this is one of the most obvious parameters to test so it might raise questions if we don't test it.                                                                                                                                                                                                    |                          | **Quadratic** Peak strength at some medium speed                                                                                                                                                                                                            | 0.2 - 2.0      | **3** (Quadratic)           |
| **First Layer Z Offset:** Z distance from the *mandrel* for printing to start                                | Starting at low value, increasing offset increases strength up to a point, and then strength falls saturating to 0 | **Yes** Prior literature shows a huge effect and our manual testing shows inconsistent results that likely come from Z offset deviations between samples.                                                                                                                                                                                                                                       |                          | **Quadratic saturating** Initially higher Z offset increases strength up to max strength then it decreases strength saturating to 0                                                                                                                         | -0.30 - 0.8 mm     | **3** (Saturating)          |
| **First Layers Height:** Z distance between layers 1 & 2 and 2 & 3 (all other layers at standard Z distance)                                        | Smaller layer heights yield stronger adhesion                                                                      | **No** We see from prior literature that smaller layer heights (0.1 mm) yield better adhesion than thicker layers (0.3 mm). However, it seems reasonable to suspect that this is caused by an ironing effect created by thinner layers, where  the second layer irons the first into the mesh during printing. Since we are studying the effects of ironing, we can likely drop this parameter. |                          | **Linear or Saturating** The paper that tested this parameter only tested 2 data points which showed a significant linear effect. However, it seems reasonable to expect the ironing effect created by smaller layer height to saturate with thicker layers |                   | **2-5** (Linear/Saturating) |
| **First Layer Flow % (Extrusion Multiplier):** Multiplier on positive extrusions for printing moves in the first layer   | N/A                                                                                                                | **Yes** There's no other parameter that affects the amount of extrusion on the first layer(s). Speed and layer height are both compensated for by less extrusion in the slicer.                                                                                                                                                                                                                 |                          | **Linear** More plastic will increase infiltration of the mesh but also the attachment area, thus increasing strength                                                                                                                                       | 100 - 200%        | **2** (Linear)              |
| **Mesh Coating:** Chemical coating of the polyester mesh to increase adhesion                                        | PLA dissolved in acetone was shown to increase adhesion strength                                                   | **No** Unless we *need* to do this, it seems too much work, which would lower the accessibility (and therefore impact) of our fabrication method.                                                                                                                                                                                                                                               |                          | **Unknown**                                                                                                                                                                                                                                                 |                   | **3-5** (Unknown)           |
| **Printed Material:** Extrudate material for printing                                    | TPU and CoPE had better adhesion than PLA                                                                          | **No For Now** PLA has desirable material properties (it is quite stiff compared to other plastics), but the effect with TPU in particular was very strong in prior literature.                                                                                                                                                                                                                 |                          | **N/A**                                                                                                                                                                                                                                                     |                   | **3** (PLA, CoPE, TPU)      |
| **Mesh Neutral Diameter:** Advertized minimum diameter of the mesh (1/4" in our case)                               | N/A                                                                                                                | **No** A wider mesh may have larger pores, which would likely have an effect on attachment strength. We also do want to print on smaller mesh in the future. However, it would be a lot of work to test this (designing new mandrel mounts and buying new mandrel hardware).                                                                                                                    |                          | **Quadratic** Sparser meshes have better attachment strength due to better plastic infiltration up to a point, but then weakness from fewer mesh strands takes over                                                                                         |                   | **3** (Quadratic)           |
| **Mandrel OD During Printing:** Outer diameter of the mandrel on which we're printing                          | N/A                                                                                                                | **No** Printing on a mandrel larger than the mesh neutral diameter makes you lose range of motion in an actuator, so I don't think we'd want to do this even if it made adhesion better.                                                                                                                                                                                                        |                          | **Quadratic** Expect 45 deg mesh angle to be optimal                                                                                                                                                                                                        |                   | **3** (Quadratic)           |
| **Mandrel OD During Testing:** Outer diameter of the mandrel used to support the mesh during testing                           | N/A                                                                                                                | **No** The permanently attached regions restrict mesh expansion, so there is a limited range of diameters we can test. This is also just changing boundary conditions, not directly related to fabrication.                                                                                                                                                                                     |                          | **Unknown**                                                                                                                                                                                                                                                 |                   | **3-5** (Unknown)           |
| **Attachment Region Width:** Width of the printed object at the first layer (width is measured perpendicular to the mandrel axis)                             | N/A                                                                                                                | **Not yet** We can use this metric to demonstrate a primary benefit of 4th axis printing, but we should find optimal *print* parameters before looking into print geometry                                                                                                                                                                                                                                                                                                  |                          | **Saturating** On the Prusa, the nozzle gets further from and less normal to the mandrel surface as width increases, reducing the benefit of extra width                                                                                                    | 2 - 6 mm          | **2** (Saturating)          |
| **Attachment Region Length:** Length of the printed object at the first layer (length is measured parallel to the mandrel axis)                            | N/A                                                                                                                | **No** The size of the attachment region will definitely affect its strength, but that's so obvious maybe it's not worth testing.                                                                                                                                                                                                                                                               |                          | **Linear** We originally expected to see a 'stepped' response where adhesion surfaces get stronger very rapidly as they touch another mesh strand, but I don't think that will happen because the mesh won't be in the exact same position sample to sample |                   | **2-3** (Linear)            |

## Factor Level Characterization
### Purpose
Before running any study of the above parameters, we need to determine reasonable ranges for each factor that will define our study space. It's important that prints don't fail during a study, as we can't measure the failure force (the response variable) for those samples.

### Initial testing
**Methods**
For each factor, we divided the *anticipated range* in the above table into six evenly-spaced levels, one for each mandrel in our setup (randomly assigned). We record the lowest and highest values for each parameter that don't cause total print failure.

Because we don't want *any* prints to fail during testing, we intentionally pick the worst-performing value of all previously-tested factors when testing subsequent factors. For example, if we find that 210 C is the lowest temperature that can create successful prints, then we keep temperature at 210 C for the rest of the factors as we test them. This becomes an iterative process, where we cycle from temperature, to ironing, to speed, etc. back to temperature and through the list again, shrinking our process window each time. This iteration will end when we've made it a full cycle with no changes needed

At the start of testing, before we've tested each factor, we pick the center point of the range of each other factor (ironing rounded down). For the first go-around, if no prints in the range fail, we immediately test that parameter again outside of the range previously tested. We repeat this until either a hardware limit is reached, the print fails, or some reasonable limit is reached (i.e. if 0 ironing is successful, it's unlikely any amount of ironing will cause failure, so we cap this parameter at 3 passes). If all prints in the range fail, we either reduce the range of the previously tested parameter or move on to the next parameter.

"Failing" here means that the plastic comes off the mesh when trying to remove the mesh from the mandrel. This includes "spaghetti" prints that never manage to connect to the mesh, but doesn't include "ugly" prints that stay on the mesh. "Failing" can also happen if the printer crashes as a result of poorly chosen print parameters (i.e. if z offset was chosen to be -1 mm the nozzle would likely crash into the mandrel).

**Results**
- Increasing print temperature improved adhesion strength
- Increasing ironing passes improved adhesion strength
- Decreasing print speed improved ahdhesion strength
- Decreasing Z offset improved ahdhesion strength
- Increasing flow multiplier improved ahdhesion strength
- Z offset seems to be the most sensitive parameter

### Final Testing
**Methods**
From initial testing, we learned the 'bad' directions for each parameter (e.g. lower printing temperature yields worse outcomes). We can bound each parameter on the 'bad' side by the standard printing parameters; there's no reason to choose parameter combinations worse than the standard printing parameters.

We also suspect from initial testing that Z offset is the most sensitive parameter. Thus, we start by testing a range of Z offsets and observe the feasible region. Then, if the feasible region is too small, we improve all the other parameters (except for ironing passes) by a small increment and test again. This is repeated until the feasible region for Z offset is sufficiently large. I did not improve ironing passes as a factor here because it only has 3 levels (0, 1, 2) and I didn't want to lose resolution there.

There are 3 potential outcomes for a sample in this test:
- High pass: Print is attached well enough along its entire length that I can't rip it off the mesh with my fingers
- Low pass: When I rip the print off the underlying mesh, there are at least 4 strands of mesh pulled out of the mesh
- Failure: Not high or low pass

Notice that the failure condition is more strict here than in the initial testing.

**Results**
- Print temperature: 240 - 280C
- Ironing: 0 - 2 passes
- Print speed multiplier: 0.2 - 0.7
- Z offset: 0.20 - 0.30 mm
- Flow multiplier: 1.5 - 2.0
We threw out Z offsets below 0.2 mm even though they passed because they caused substantial deflection of the mandrel during printing. If we printed in this manner, then results would be much less transferable to other machines, as mandrel stiffness would affect print quality.


### Print Settings
Printing G-code is generated first using the Prusa slicer version 2.9.6 with the following settings:
- Print settings: 0.20mm SPEED
- Filament: "Mandrel PLA"
- Supports: For support enforcers only
- Infill: 15%
- No Brim
- Printer: "Mandrel Printing"

"Mandrel PLA" is a user-defined filament based off "Generic PLA" settings with bed temp set to 0 because we're not using the heated bed.

"Mandrel Printing" is a user-defined printer based off of the "Original Prusa XL - 5T Input Shaper 0.4 nozzle". We've changed the custom start G-code to enable mesh bed leveling across the mandrels; see [Start G-code.txt](../PrusaGcodeEditing/Start%20G-code.txt) for details. We've also turned off "Supports binary G-code", so that outputs will be in ASCII ".gcode" format.

The Prusa slicer output is then sent through our [G-code editing script](../PrusaGcodeEditing/scripts/MultiFileEditor.py), which updates all tested parameters to their test values.

### Printed Geometry
A 30mm long, 5mm wide, 2mm high bar centered on each mandrel in X and Y.

### Experimental Notes
See the [Excel sheet](/Parameter%20Sweep%20Testing/Parameter%20Sweep%20Results.xlsx) for details.

## Center Point Variance Testing
### Purpose
We need a good estimation of our process variance to size our future studies to appropriate statistical power. We only need to extract the process variance (not mandrel-to-mandrel variation) because mandrel number will be included as a blocking variable in future studies.

### Methods
**ADMET Testing**
- Mesh placed all the way down to the end of the rod for testing on ADMET
- Samples secured to rod for ADMET shear testing using 4 hose clamps, 2 on either end tightened using the makita hand drill to clutch setting 1 for consistency
- The rod is not straightened using the end nut on the ADMET connector; it's allowed to swing slightly
- Clamp was balanced with a plastic piece in the other end of the jaw of equal thickness (width) to the tested piece
- Load cell zeroed after clamp closed just before testing using "Shear Test to Failure"
- Samples tested to failure, with peak load as the recorded parameter (though full profiles are recorded as well)
- 18 samples total, 3 per mandrel

**Statistical Analysis**
Looking at our results as if we would like to model mandrel-to-mandrel devitation via ANOVA yields:

$SST = SSM + SSE$

Where $SSE$ represents the total error in our model not attributable to mandrel-to-mandrel deviation. We calculate $SSE$ as:

$SSE = \sum_{i=1}^{6} \sum_{j=1}^{3} (y_{ij} - \bar{Y}_i)^2$

Where $y_{ij}$ represents the adhesion strength of the $j^{th}$ print on mandrel $i$, and $\bar{Y}_i$ represents the group mean for mandrel $i$. We can use this to calculate the mean square error:

$MSE = \frac{SSE}{df_E}$

Here $df_E$ reprsents the degrees of freedom of the error, which is equal to the number of samples $18$ minus the number of mandrels $6$, or $12$.

### Results
The mean square error of the process was $187.9832 \text{ lbs}^2$, which gives an RMSE of $13.71069 \text{ lbs}$.

### Print Settings
Same as [Factor Level Characterization](#factor-level-characterization).

### Printed Geometry
A 30mm long, 5mm wide, 15mm high bar centered on each mandrel in X and Y

### Experimental Notes
Same file as [Factor Level Characterization](#factor-level-characterization).

## Adhesion Strength Optimization Study
### Purpose
Identify optimal printing parameters for our process specifically, and identify significant trends that could inform print parameters for other processes

### Methods
**Chosen Statistical Structure**
- RSM I-optimal design using JMP's custom design tool
- 60 freely chosen points, 12 repeats, and 18 centerpoints from [variance testing](#center-point-variance-testing) for a total of 90 samples


**JMP Process**
*Sample Size Estimation*:
1) Set optimality criterion to I-optimal.
2) Add response (adhesion strength) and factors (tested printing parameters).
3) Decide on the number of samples to try (60 minimum for our set of parameters).
4) Add mandrel as a blocking factor with runs per block equal to the number of samples / 6.
5) Add all RSM terms to model (main effects, 2FI, and 2nd order terms).
6) Hold center points at 18, then choose a number of replicate runs and enter the previously-decided total number of runs. The blocking factor (mandrel) should now have 6 levels.
7) Make design, and under power analysis fill in the anticipated RSME and anticipated coefficients as seen in the figure below.
8) We want to achieve at least 0.8 statistical power - the interdisciplinary standard minimum according to the [literature](https://pmc.ncbi.nlm.nih.gov/articles/PMC7425741/). Repeat steps 3-7 until sufficient power has been achieved.
\
    We found that 90 samples with 12 repeats and 18 centerpoints was an adequate size, providing reasonably high statistical power without being an onerous number of samples. Below is the statistical power achieved by this design:

    In [center point testing](#center-point-variance-testing), we found mandrels had an average absolute effect of 10.8152 lbs from the mean. Thus, we aren't interested in identifying effects much smaller than ~5 lbs, as at that size mandrel-to-mandrel deviation will begin to dominate.


    
    


We use the RMSE found in the previous section to identify an acceptable number of samples. A custom design was chosen with I-optimal critera. We selected 12 repeats and 18 centerpoints, then tweaked the number of total samples until sufficient statistical power was achieved. To estimate power, we assume an anticipated coefficient of 10 lbs for all primary effects and 5 lbs (around the same ), and we used the measured effect from variance testing for each mandrel. We decided **90 samples total** was the best middle-ground between catching all main effects and some 2FI and curvature. This [file](/Optimization%20Testing/I%20Optimal%20Design.jmp) shows the JMP analysis and results. Power analysis results are also shown below:
![Power Analysis Results](/Optimization%20Testing/Power%20Analysis.png)

2) The optimal design created in the previous step is not suitable for our analysis, as the 18 centerpoints created there aren't distributed across our blocking factor (mandrels) evenly like was the case during variance testing. As suggested on this [JMP community board](https://community.jmp.com/t5/Discussions/Custom-Design-Around-Existing-Data-With-Blocking-Factor/m-p/975146/thread-id/110640#M110641), we create a new I-optimal design. This design has the same settings as in step 1, except it has no 0 centerpoints and correspondingly 18 less runs (72 runs). Excluding the previously-collected runs from the custom design optimization shouldn't impact the distribution of other samples much, as the expected response surface variance shouldn't be impacted much by the inclusion of an extra sample location. This [file](/Optimization%20Testing/I%20Optimal%20Design%20No%20Centerpoints.jmp) shows the resulting design.

3) We add our 18 centerpoints from variance testing to the front of our design from the previous step and can now analyze the whole thing

- Printing and ADMET testing were carried out in the same manner as in [midpoint variance testing](#midpoint-variance-testing).

### Results
