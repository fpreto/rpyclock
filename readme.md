# Raspberry PI Clock Daemon

This is a Python Daemon that allows to control a LED Dot Matrix display and display the time.


## Requirements

This is the hardware and software required to run this daemon:

* Raspberry PI Zero W
* LED Dot Matrix 4-cascaded controlled by MAX7219
* GNU/Linux Raspbian Streech
* Python 3.5


# Preparing software

Python:
```
sudo apt-get install python3
sudp apt-get install python3-rpi.gpio
```

PIP:
```
sudo apt-get install python3-pip
sudo pip3 install --upgrade pip
```

Enable SPI:
```
sudo raspi-config
Select 5 Interfacing Options
Select P4 SPI and yes
```

Install Python LED Controller:
```  
sudo pip3 install luma.led_matrix
sudo apt-get install libopenjp2-7
sudo apt-get install libtiff5
```



## Hardware wiring diagram

LED Matrix

| Pin | Name | Raspberry Pin | Raspberry Description | Details |
|-----|------|---------------|-----------------------|---------|
| 1 | VCC | 2 | 5V | 5V+ Power |
| 2 | GND | 6 | GND | Ground |
| 3 | DIN | 19 | GPIO 10 (MOSI) | Data In |
| 4 | CS | 24 | GPIO 8 (SP CE0) | Chip Select |
| 5| CLK | 23 | GPIO 11 (SPI SCLK) | Clock |


## References

* [Luma LED Matrix github](https://github.com/rm-hull/luma.led_matrix)