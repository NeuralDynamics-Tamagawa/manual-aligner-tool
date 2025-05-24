# 📖 manual-aligner-tool

manually align volumes of two channels obtained by light-sheet microscope

## 📚 Overview

This repository provides a graphical user interface (GUI) tool designed for manual inspection, alignment, and cropping of volumetric imaging datasets, primary for preprocessing light-sheet fluorescence microscopy images of biological tissue (e.g. cleared brain), for registration to the common reference coordinate (e.g. atlas).  
The manuscript for entire pipeline including tissue clearance, image acquisition and registration will be published SOON.


---

## ✨ Features

- Load one or two volumetric image stacks (e.g., `.tif` files)
- Visualize multi-channel images with adjustable colormaps and opacity
- Apply manual Z/Y/X translation to secondary images for alignment
- Dynamically adjust a Y-axis threshold to crop the image
- Save shifted or masked images directly from the GUI interface

---

## 📦 Installation

It is recommended to use a dedicated virtual environment, such as conda or venv. For example,

```bash
cd (yourfolderpath) # where you downloaded this folder e.g. Documents/github/manual-aligner-tool)
conda env create -f environment.yml
conda activate manual-aligner # enter the environment you created
```

## ▶️ Usage
1. Run below code in manual-aligner environment 
```bash
python manual_aligner.py
```

2. Select .tif files you want to align/crop.
- If you have two images, the first image is used as a reference (e.g. it is not moved) and the second image will be shifted to match the first one.
- If you have one image and only want to crop, leave 2nd file empty.
- After selecting files, press "Confirm and Exit".
  
![file select GUI](images/file_select.png)

3. Napari GUI will open with widgets at the right.
 
![napari widget](images/napari_widget.png)

Adjust y threshold to move the yellow horizontal bar, above which the image will be cropped (padded with background intensity). If you have two images, adjust xyz shift to match two images. After adjusting, close the window.

![y threshold example](images/y_threshould.png)

5. The new images will be saved as (ORIGINALFILENAME)_new.tif in the same directory. Napari will reopen with new images for final visual inspection. 



