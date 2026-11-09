# Natural-paced English narration

300 seconds; AI speech at -8%, no audio time compression.

## 00:00:00.000–00:00:05.480

Our project studies complete physical pick-and-place with a Franka Panda in MuJoCo.

## 00:00:05.480–00:00:10.640

We investigate blocked approaches, corrupted geometry and contact retention.

## 00:00:10.640–00:00:15.280

The aim is to explain task failures and test bounded interventions.

## 00:00:15.280–00:00:21.720

The baseline loads six public YCB models and supports seeded random object selection and placement.

## 00:00:21.720–00:00:26.280

This complete run starts with a checked approach and physical finger closure.

## 00:00:26.280–00:00:31.120

Contact lifts and holds the target before the robot begins its transfer.

## 00:00:31.120–00:00:36.280

The arm carries the object to the destination, lowers it and opens the fingers.

## 00:00:36.280–00:00:41.280

Release and table support are checked; failures remain in the evaluation.

## 00:00:41.280–00:00:49.200

Mesh-based candidates are proposals. Inverse kinematics and collision checks decide which can execute.

## 00:00:49.200–00:00:56.040

Complete success requires an eighty-millimeter lift, a one-second hold and sustained bilateral contact.

## 00:00:56.040–00:01:01.160

Release must be stable, within fifty-five millimeters of the destination.

## 00:01:01.160–00:01:05.840

Planning still uses simulator geometry; sensing is synthetic.

## 00:01:05.840–00:01:10.720

The original candidates are rejected because a nearby can blocks the palm.

## 00:01:10.720–00:01:17.160

We keep the scene and safety checks, adding bounded inclined and offset grasp alternatives.

## 00:01:17.160–00:01:23.600

The chosen alternative lifts the target and carries it through the checked corridor.

## 00:01:23.600–00:01:31.240

The robot lowers and releases it. This development demonstration is separate from the paired evaluation.

## 00:01:31.240–00:01:37.400

This elastic model genuinely deforms; the YCB foam brick in the baseline remains rigid.

## 00:01:37.400–00:01:43.400

The controller regulates the weaker finger contact to retain the object during lift and transfer.

## 00:01:43.400–00:01:49.600

Fixed preload completes two of six soft-object tasks; regulation completes six of six.

## 00:01:49.600–00:01:55.240

These force and strain curves illustrate one development run, rather than a group average.

## 00:01:55.240–00:02:01.480

Across formal trials, mean peak strain rises from about three-point-seven to four-point-nine percent.

## 00:02:01.480–00:02:07.400

Retention improves within the tested limits; reduced deformation is not demonstrated.

## 00:02:07.400–00:02:12.960

A separate rigid-load study randomizes mass, friction and actuator delay.

## 00:02:12.960–00:02:17.680

Regulation changes completion from ten of twelve to twelve of twelve.

## 00:02:17.680–00:02:24.040

Synthetic depth includes missing stripes, drift, outliers and a persistent calibration bias.

## 00:02:24.040–00:02:29.760

The single-packet method completes six of twelve tasks; naive fusion completes only one.

## 00:02:29.760–00:02:36.200

Cross-packet voxel support rejects transient outliers and reaches nine successes in twelve trials.

## 00:02:36.200–00:02:44.320

This successful development example uses the robust observer, without target CAD or instance labels in grasp estimation.

## 00:02:44.320–00:02:51.160

Planning still uses simulator geometry; measured observations do not make the entire system vision-only.

## 00:02:51.160–00:02:55.520

The robot carries and releases the object in this illustration.

## 00:02:55.520–00:02:59.760

The formal failures remain wedge slips, in separate trials.

## 00:02:59.760–00:03:04.560

A transient command fault leaves the first closure wider than the target.

## 00:03:04.560–00:03:09.080

No bilateral contact is detected; the grasp is rejected.

## 00:03:09.080–00:03:12.640

The robot opens and withdraws safely.

## 00:03:12.640–00:03:17.080

It reobserves and makes a second grasp in the same evolving scene.

## 00:03:17.080–00:03:22.760

The second grasp holds through lift and transfer; the scene was never reset.

## 00:03:22.760–00:03:27.960

After lowering and release, table support and final placement are verified.

## 00:03:27.960–00:03:33.080

All six controlled episodes recover; broader recovery remains unproven.

## 00:03:33.080–00:03:37.840

A passive hinge remains dynamic while the whole assembly is transported.

## 00:03:37.840–00:03:43.360

All six assembly tasks succeed; deliberate lid opening is not demonstrated.

## 00:03:43.360–00:03:48.880

Measured points propose grasps for procedural instances without target CAD.

## 00:03:48.880–00:03:53.160

Both methods tie at eleven of twelve, with one shared slip.

## 00:03:53.160–00:04:00.040

In separate stronger-clutter trials, active sensing changes completion from five of six to three of six.

## 00:04:00.040–00:04:04.720

The candidate study contains one hundred eighty paired physical episodes.

## 00:04:04.720–00:04:10.960

With three neighbors, local alternatives change success from fifty-four to fifty-eight out of sixty.

## 00:04:10.960–00:04:16.160

With five neighbors, success changes from twenty-six to twenty-nine out of thirty.

## 00:04:16.160–00:04:22.680

The separate exploratory screening contains one hundred twenty-six episodes across fourteen conditions.

## 00:04:22.680–00:04:29.520

The intervals show substantial uncertainty; none of the comparisons passes its stated statistical threshold.

## 00:04:29.520–00:04:34.000

Initial scenes and physics are paired, with all failures retained.

## 00:04:34.000–00:04:39.200

Development demonstrations are excluded from both evaluation denominators.

## 00:04:39.200–00:04:44.760

The main finding is to diagnose geometry, sensing and contact retention together.

## 00:04:44.760–00:04:50.520

Source code, frozen records and the ten-page report provide reproduction instructions.

## 00:04:50.520–00:04:54.120

Forty-nine tests and both evidence audits pass.

## 00:04:54.120–00:05:00.000

Next steps target wedge stability, deformation-aware control and less ideal sensing.
