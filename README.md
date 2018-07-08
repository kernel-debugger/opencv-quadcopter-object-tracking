# Opencv based quadcopter object tracking 
This repository contains code to auto-follow objects using opencv and a quadcopter
Quadcopter can be manually controlled using Remote.jar, you can use wifi/3g/4g with the RPI

## Demo video  

https://www.youtube.com/watch?v=6CbXLP3D_yo

## Project sketch:

<img src="https://raw.githubusercontent.com/kernel-debugger/opencv-quadcopter-object-tracking/master/Untitled%20Sketch_bb.jpg">


I used a Syma X8HW quadcopter, Raspberry Pi , Arduino Nano and an NRF24L01+ Transceiver

## Files include.

- An Arduino sketch to read commands from RPI via Serial port and forward them to the quadcopter using an NRF24L01+,(syma_python_cv_udp_controller.ino)

- A Java based UDP client to send commands to the Raspberry Pi,(symaUdp.java),{ Remote.jar is compiled version }

- Python script to handle object tracking based on color (colortracker.py)

- Python class "QuadController" for quadcopter navigation operations and to send commands via serial to Arduino (kali.py)
