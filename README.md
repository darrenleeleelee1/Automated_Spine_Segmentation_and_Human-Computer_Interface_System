# Automated Spine Segmentation and Human-Computer Interface System
The code was written by [Chein Chang](https://github.com/pchien0415), [Darren Lee](https://github.com/darrenleeleelee1), [Jamie Wang](https://github.com/jamie212) and [Yoyo Zheng](https://github.com/yo-yo97).

## Outline
1. [Introduction](#Introduction)
2. [Set up](#Set-up)
3. [Qt technique](#Qt-technique)
4. [Reference](#Reference)

## Introduction
### Motivation
Design an artificial intelligence algorithm that can predict the probability of a patient who has undergone spinal fusion surgery experiencing a vertebral fracture within one year, and provide a simple and clear interface system (GUI) for medical staff to create a visualized prediction model for the convenience of researchers to use and optimize.

### Demonstrations
A DICOM contain an advanced function - Spine Segmentation. 
![](https://i.imgur.com/xz1sovX.png)

[More Detailed](https://docs.google.com/presentation/d/1Vd_tQBE5Ut5m4bTp5vuH_ZFHBKwUkGDB1o-B7ACBkuY/edit?usp=sharing)

## Set up
1. Create a new enviroment
```
conda create -n qt_env python=3.8
```
2. Activate the new enviroment
```
activate qt_env
```
3. Install PyQt5
```
pip install pyqt5
pip install pyqt5-tools
```
4. Check
```
import PyQt5
```

## Qt technique
### Qt Designer to Python Code
[link](https://realpython.com/qt-designer-python/)

* Shell
```
pyuic5 -o ____.py ____.ui
```

### qrc file to py file
* Shell
```
pyrcc5 ____.qrc -o ____.py
```

## Reference
1. [zhixuhao, Unet using Tensorflow](https://github.com/zhixuhao/unet) 
2. [DICOM影像格式影像格式標籤](https://b8807053.pixnet.net/blog/post/10116283)
3. [PyQt API](https://doc.qt.io/qtforpython/api.html)
4. [Find vertices in image of convex polygon](https://www.mathworks.com/matlabcentral/fileexchange/74181-find-vertices-in-image-of-convex-polygon)
5. Kim YJ, Ganbold B, Kim KG. Web-based spine segmentation using deep learning in computed tomography images. Healthc Inform Res 2020;26:61-7.
6. Asian Spine Journal 2020 - Review of the use of AI in spinal Diseases
7. Computer Methods and Programs in Biomedicine 2020 - Automatic detection and segmentation of lumbar vertebra
8. Global Spine Journal 2020 - Automated Measurement of Lumbar Lordosis
9. Osteoporosis International 2019 - Prediction Of Lumbar Vertebral Strength
10. Better Height Restoration, Greater Kyphosis Correction, and Fewer Refractures of
