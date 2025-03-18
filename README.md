# DoYouSeeMe



<div style="display: flex; justify-content: space-between;">
  <img src="https://github.com/adi-msr/DoYouSeeMe/blob/main/img/main_fig.png" width="100%" alt="Results on Do You See Me">
</div>


## Overview

The DoYouSeeMe benchmark is a comprehensive evaluation framework designed to assess visual perception capabilities in Machine Learning Language Models (MLLMs). This fully automated test suite dynamically generates both visual stimuli and perception-focused questions (VPQA) with incremental difficulty levels, enabling a graded evaluation of MLLM performance across multiple perceptual dimensions.

## Theoretical Foundation

The dataset's structure is grounded in established human psychological frameworks that categorize visual perception into core abilities (Chalfant and Scheffelin, 1969). Drawing inspiration from standardized assessments like the Test of Visual Perception Skills (TVPS) (Gardner, 1988) and Motor-Free Visual Perception Test (MVPT) (Colarusso, 2003), DoYouSeeMe adapts these principles to create a systematic evaluation methodology for machine vision systems.

## Perceptual Dimensions

The benchmark focuses on seven key dimensions of visual perception:

1. **Shape Discrimination**: Evaluates the ability to recognize shapes.

2. **Joint Shape-Color Discrimination**: Evaluates the ability to jointly recognize shapes and color.

3. **Visual Form Constancy**: Tests MLLM ability to identify a test shape configuration from similarly placed disctractors.

4. **Letter Disambiguation**: Tests the recognition of letters.

5. **Visual Figure-Ground**: Evaluates the ability to distinguish the main object from its background under varying conditions.

6. **Visual Closure**: Assesses the ability to complete partially obscured shapes by mentally filling in missing information.

7. **Visual Spatial**: Examines the ability to perceive positions of objects relative to oneself and to other objects.


Note: While human visual perception also includes Visual Memory (the ability to remember sequences of presented images), this dimension is omitted from the benchmark as current MLLMs lack short-term visual memory capabilities beyond textual descriptions.

## Technical Implementation

The entire dataset generation framework is implemented in Python and uses SVG representations to create visual stimuli with precisely controlled parameters. This approach allows for:

- Dynamic generation of test images with systematic variations
- Controlled difficulty progression across perception dimensions
- Reproducible evaluation conditions
- Fine-grained assessment of model performance

### Control Parameters

<div style="display: flex; justify-content: space-between;">
  <img src="https://github.com/adi-msr/DoYouSeeMe/blob/main/img/control_param_syn_dataset.png" width="100%" alt="Results on Do You See Me">
</div>

The code and dataset are open-sourced to facilitate further research and advancement in the field of visual perception for artificial intelligence systems.


This repository contains a synthetic dataset exploring seven distinct dimensions of visual perception and processing. Each dimension examines a specific aspect of how we interpret visual information.

## Dataset Structure

The repository is organized into 7 dimension-specific directories:
- dataset/visual_spatial
- dataset/visual_figure_ground
- dataset/visual_form_constancy
- dataset/shape_disambiguation
- dataset/shape_color_discrimination
- dataset/letter_disambiguation
- dataset/visual_closure

In order to use our synthetic data generation for the visual-perception dimensions, simply run any of the 7 python files in the main repo named as: *\<dimension-name\>.py*. Each python file has a control towards the end, where sweeps are defined for each control parameter listed in **Table 1**, these can be changed to increase data. For 1) visual_spatial, 2) shape_disambiguation, and 3) shape_color_discrimination a *dataset_dump.csv* is created in related directory, this dump file captures all the details for each generated image, we then use a *dataset_creator.py* file (added in all the three dirs) to generate the actual dataset (dataset_info.csv), where multiple perception questions are formulated per image (refer the dataset_creator.py to change number of questions per image). Each visual-perception dim has a dataset_info.csv containing filename, question, answer, and sweep column. 

We have created a dataset of around 2.1k images used and benchmarked multiple open and closed source MLLMs, performance of MLLMs is presented in the **Results** section. This benchmark dataset is released as a zip file named *dataset.zip* in the main folder.

## Data Format

Each dimension directory contains:
- Images(`<xx>.png`): Images with controlled variations
- dataset_info.csv: Metadata file containing control parameters and ground truth answers for each image

## Results

<div style="display: flex; justify-content: space-between;">
  <img src="https://github.com/adi-msr/DoYouSeeMe/blob/main/img/results_syn_dataset.png" width="100%" alt="Results on Do You See Me">
</div>


## Samples

### Visual Spatial

Tests the ability to perceive and understand spatial relationships between objects. Evaluates orientation discrimination and positional awareness.

<div style="display: flex; justify-content: space-between;">
  <img src="https://github.com/adi-msr/DoYouSeeMe/blob/main/dataset/visual_spatial/1.png" width="30%" alt="Visual Spatial Example 1">
  <img src="https://github.com/adi-msr/DoYouSeeMe/blob/main/dataset/visual_spatial/50.png" width="30%" alt="Visual Spatial Example 2">
  <img src="https://github.com/adi-msr/DoYouSeeMe/blob/main/dataset/visual_spatial/100.png" width="30%" alt="Visual Spatial Example 3">
</div>

*Sample Question: Starting from the black circle at position (row 1, column 3), how many triangles are there bottom of it in the same row?*


### Visual Figure-Ground

Examines the ability to distinguish an object from its background. Challenges perception by varying contrast, noise, and complexity.

<div style="display: flex; justify-content: space-between;">
  <img src="https://github.com/adi-msr/DoYouSeeMe/blob/main/dataset/visual_figure_ground/1.png" width="30%" alt="Figure-Ground Example 1">
  <img src="https://github.com/adi-msr/DoYouSeeMe/blob/main/dataset/visual_figure_ground/50.png" width="30%" alt="Figure-Ground Example 2">
  <img src="https://github.com/adi-msr/DoYouSeeMe/blob/main/dataset/visual_figure_ground/89.png" width="30%" alt="Figure-Ground Example 3">
</div>

*Sample Question: The figure consists of a Target image, which is embedded in some background noise. Out of the four given options, your task is to pick the option which has the same figure as the target image. Respond as follows: Option <your answer (choose between 1, 2, 3, or 4)>.*

### Visual Form Constancy

Assesses recognition of shapes despite changes in size, orientation, or context. Tests invariance in visual perception.

<div style="display: flex; justify-content: space-between;">
  <img src="https://github.com/adi-msr/DoYouSeeMe/blob/main/dataset/visual_form_constancy/1.png" width="30%" alt="Form Constancy Example 1">
  <img src="https://github.com/adi-msr/DoYouSeeMe/blob/main/dataset/visual_form_constancy/50.png" width="30%" alt="Form Constancy Example 2">
  <img src="https://github.com/adi-msr/DoYouSeeMe/blob/main/dataset/visual_form_constancy/100.png" width="30%" alt="Form Constancy Example 3">
</div>

*Sample Question: The figure consists of a Target image. Out of the four given options, your task is to pick the option which has the same figure as the target image. Respond as follows: Option <your answer (choose between 1, 2, 3, or 4)>.*


### Shape Disambiguation

Challenges the ability to identify ambiguous shapes that can be interpreted in multiple ways. Explores perceptual flexibility.

<div style="display: flex; justify-content: space-between;">
  <img src="https://github.com/adi-msr/DoYouSeeMe/blob/main/dataset/geometric_dataset/sweep_0_0.png" width="30%" alt="Shape Disambiguation Example 1">
  <img src="https://github.com/adi-msr/DoYouSeeMe/blob/main/dataset/geometric_dataset/sweep_10_0.png" width="30%" alt="Shape Disambiguation Example 2">
  <img src="https://github.com/adi-msr/DoYouSeeMe/blob/main/dataset/geometric_dataset/sweep_20_2.png" width="30%" alt="Shape Disambiguation Example 3">
</div>

*Sample Question: Count the total number of triangles in the image, including each concentric triangle separately. For example, if there is one triangle with 2 inner concentric rings, that counts as 3 triangles. Respond with only a number.*


### Shape Color Discrimination

Tests the ability to differentiate shapes based on color properties while controlling for other visual features.

<div style="display: flex; justify-content: space-between;">
  <img src="https://github.com/adi-msr/DoYouSeeMe/blob/main/dataset/color_and_shape_disambiguation/1.png" width="30%" alt="Shape Color Example 1">
  <img src="https://github.com/adi-msr/DoYouSeeMe/blob/main/dataset/color_and_shape_disambiguation/50.png" width="30%" alt="Shape Color Example 2">
  <img src="https://github.com/adi-msr/DoYouSeeMe/blob/main/dataset/color_and_shape_disambiguation/89.png" width="30%" alt="Shape Color Example 3">
</div>

*Sample Question: Count the number of star's that are red.*



### Letter Disambiguation

Examines recognition of letters under various transformations and distortions. Evaluates robustness of character recognition.

<div style="display: flex; justify-content: space-between;">
  <img src="https://github.com/adi-msr/DoYouSeeMe/blob/main/dataset/letter_disambiguation/1.png" width="30%" alt="Letter Disambiguation Example 1">
  <img src="https://github.com/adi-msr/DoYouSeeMe/blob/main/dataset/letter_disambiguation/50.png" width="30%" alt="Letter Disambiguation Example 2">
  <img src="https://github.com/adi-msr/DoYouSeeMe/blob/main/dataset/letter_disambiguation/100.png" width="30%" alt="Letter Disambiguation Example 3">
</div>

*Sample Question: The image shows one or more letters formed by a grid of small squares. What letter(s) can you identify in this image? Please respond with only the letter(s) you see.*




### Visual Closure

Tests the ability to recognize incomplete figures by mentally filling in missing information. Evaluates gestalt processing.

<div style="display: flex; justify-content: space-between;">
  <img src="https://github.com/adi-msr/DoYouSeeMe/blob/main/dataset/visual_closure/1.png" width="30%" alt="Visual Closure Example 1">
  <img src="https://github.com/adi-msr/DoYouSeeMe/blob/main/dataset/visual_closure/50.png" width="30%" alt="Visual Closure Example 2">
  <img src="https://github.com/adi-msr/DoYouSeeMe/blob/main/dataset/visual_closure/100.png" width="30%" alt="Visual Closure Example 3">
</div>

*Sample Question: The figure consists of a target image which is complete, Out of the four given options (which are partially complete), your task is to pick the option which when completed matches the target image. Respond as follows: Option <your answer (choose between 1, 2, 3, or 4)>.*

## Contributing

This project welcomes contributions and suggestions.  Most contributions require you to agree to a
Contributor License Agreement (CLA) declaring that you have the right to, and actually do, grant us
the rights to use your contribution. For details, visit https://cla.opensource.microsoft.com.

When you submit a pull request, a CLA bot will automatically determine whether you need to provide
a CLA and decorate the PR appropriately (e.g., status check, comment). Simply follow the instructions
provided by the bot. You will only need to do this once across all repos using our CLA.

This project has adopted the [Microsoft Open Source Code of Conduct](https://opensource.microsoft.com/codeofconduct/).
For more information see the [Code of Conduct FAQ](https://opensource.microsoft.com/codeofconduct/faq/) or
contact [opencode@microsoft.com](mailto:opencode@microsoft.com) with any additional questions or comments.

## Trademarks

This project may contain trademarks or logos for projects, products, or services. Authorized use of Microsoft 
trademarks or logos is subject to and must follow 
[Microsoft's Trademark & Brand Guidelines](https://www.microsoft.com/en-us/legal/intellectualproperty/trademarks/usage/general).
Use of Microsoft trademarks or logos in modified versions of this project must not cause confusion or imply Microsoft sponsorship.
Any use of third-party trademarks or logos are subject to those third-party's policies.
