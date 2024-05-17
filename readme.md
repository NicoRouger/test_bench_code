Sure, here's the updated `README.md` file for you to copy:

LAAS-LAPLACE Hackathon Test Bench
==================================

This repository contains the code for the LAAS-LAPLACE Hackathon Test Bench. The test bench is composed of digital multimeters, an oscilloscope, a power supply and a device under test (DUT).

The `main.py` script creates all the objects of each instrument of the test bench and provides multiple code functions for later developing the appropriate algorithm.

Requirements
------------

* Python 3.x
* PyVISA
* pandas
* matplotlib

Getting Started
---------------

1. Clone the repository to your local machine:
```bash
git clone https://github.com/your_username/laas-laplace-hackathon.git
```
2. Install the required packages:
```bash
pip install -r requirements.txt
```
3. Connect your instruments to your computer and make sure they are recognized by PyVISA:
```bash
python -m pyvisa.info
```
4. Run the `main.py` script:
```bash
python main.py
```
Instruments
------------

### Digital Multimeters

The digital multimeters are used to measure the voltage, current and temperature of the DUT. The `measure_devices_init()` function initializes the multimeters and checks their identity.

### Power Supply

The power supply is used to provide power to the DUT. The `supply_init()` function initializes the power supply and sets up the channels.

### Oscilloscope

The oscilloscope is used to visualize the waveforms of the DUT. The `Oscilloscope` class provides methods to configure the scope, acquire data and save it to a CSV file.

### Device Under Test (DUT)

The DUT is the device being tested in the LAAS-LAPLACE Hackathon. The `Twist_Device` class provides methods to control the DUT and acquire data.

Contributing
------------

Any contribution is welcome through PRs.

License
-------

All the code is in GPLV3.