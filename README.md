# Microscopy Control And Image Processing

This project creates a framework for high level automation by using an **Acquire-Process-Decide** mechanism. These mechanisms can be used to create different **acquisition** tickets which aquire data, easy to implement **image processors** that create data from images, and **decisions** which create data and propose new acuisitions.

This repository can also use multiple machines to accelerate compute times and use image emulators to mimic the behavior of a microscope.

![alt text](https://github.com/MunskyGroup/MicroscopyControlAndProcessing/blob/main/docs/apd.png)
> *Acquire-Process-Decide Pipelines create a framework for high level automation by builing up on automations created by ```MicroManager``` and ```PycroManager```.*

### Requirements:
...

[**Overview**](docs/content/overview.md)

[**Installation**](docs/content/installation.md)

[**Configure the Demo System or Real System**](docs/content/config.md)

[**Configure Software Settings (Distributed Computing, Remote Storage, User Credentials, Logging Verbosity, Device Management)**](docs/configure.md)

[**Example One: Simple Test Acquisition of the MicroManager Demo System**](docs/content/example1.md)

[**Example Two: Acquire-Process-Decide using Microscopy Emulation**](docs/content/example2.md)

[**Application 1: Finding twenty-five cells in a real system**](docs/content/example3.md)

[**Application 2: Identifying ten puncta and making ten movies in a real system**](docs/content/example4.md)

## The rest of the page will discuss a real application of the automation

A three color HiLo microscope with a galvo controlled laser was developed and used for the development of this code. This microscope can acquire 2D images in three colors using inclined light to increase the signal to noise ratio. Device drivers were managed using ```MicroManager```, but interfaces for the control of outside devices (like lasers and custom ```FilterWheels``` and ```GalvoSystems```) were developed. 

![alt text](https://github.com/MunskyGroup/MicroscopyControlAndProcessing/blob/main/docs/files/cartoon.png)
> *The schematic of the system shows a three laser HiLo microscope with a galvo laser*

A library of image acquisition can be found [**here**](docs/content/modeling.md), which describes an ```AcquisitionTicket```, that describes all variables and callback functions needed to perform an automated acquisition. This library contains pre-writted tickets that describe a variety of common acquisitions (including loose grids, tight grids, XY position sequences, and  XYZ position sequences).

The Acquire-Process-Decide Pipeline was developed to find 25 cells within a region. 

Similarly libraries were written for common ```ImageProcessPipeline```(s), and ```Decisions```, which take images and create and data, and take take data to propose new acquisitions.

![alt text](https://github.com/MunskyGroup/MicroscopyControlAndProcessing/blob/main/docs/files/emulated.png)
> *Automated data acquisitions using the image emulator. An eight by eight grid of images
was acquired using the ‘grid search’ procedure using an image emulator that replaces acquired images with
emulated ones. (A). Images which were believed to contain three or more nuclei using Cellpose were
highlighted in green boxes, and an acceptance ratio was measured to be twenty-three out of sixty-four total
images. (B) Images of Cellpose nuclei masks show good match with expectation, but missing a dim nuclei
in the bottom right edge. (C) Correlations (R2 = 0:822) and sensitivity ( eps = 0:870) suggest accurate
determination of the number of nuclei.*

The loose grid image searching pipeline was run on the real microscope to analyze its performance.

![alt text](https://github.com/MunskyGroup/MicroscopyControlAndProcessing/blob/main/docs/files/real.png)
> *Automated data acquisitions of fluorescently labeled mRNA. An eight by eight grid of
images was acquired using the ‘grid search’ procedure using smFISH stained cytoplasmic GAPDH exons.
(A) Images which were believed to contain three or more cells using the Cellpose cytoplasm model were
labeled in green. Image acceptance ratios (42/64) and acquisition times are shown in the bottom. (B)
Correlations (R2 = 0:550) and sensitivity ( eps = 0:757) of the Cellpose detection method can be seen. (C)
Correlations (R2 = 0:631) and sensitivity ( eps = 0:804) of the mean intensity detection method show similar
accuracy and sensitivity to Cellpose for this set of images.*

A puncta detection method was developed to idenfity images with bright spots to create a framework for identifying phenotypes in images and using an ```ImageDetection``` method to accept or reject images. In this example a detection method was created for identifying cells with puncta using the Laplacian of Gaussians and re-imaging positions which were estimated to have at least one puncta. 

![alt text](https://github.com/MunskyGroup/MicroscopyControlAndProcessing/blob/main/docs/files/puncta.png)
>  *Median image processing on two slides. The mean intensity method and the Cellpose identification
method were compared using grid searches on two different slides with the same imaging conditions.
(A) The mean intensity method was used to determine which regions of interest (ROIs) to keep for re-imaging.
Images were predicted to have three or more cells if the median intensity was greater than 2500.
Scatter plots of slide one data and slide two data show large discrepancy between the two slides. (B) The
same images were then analyzed using Cellpose. Scatter plots of slide one and slide took look much more
uniform.*
