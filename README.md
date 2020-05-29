![Contributions welcome](https://img.shields.io/badge/contributions-welcome-brightgreen.svg)
[![License](https://img.shields.io/badge/license-MIT%20License-brightgreen.svg)](https://opensource.org/licenses/MIT)

# About estim2bapi
This is an (unofficial) API for the E-Stim 2B, written for Python 3.6+. 

## Features
* Threaded design: Estim class doesn't block the main thread, making it simple to write complicated code involving multiple sensors.
* Supports simultaneous control of multiple 2Bs!
* Autodetects the correct COM port.
* estim2b.play module for command routines (currently "jolt" and "ramp").
* Informative warning/error messages (using Estim(..., verbose=2))

## To-do
* Create a PyPi package for easier installation.
* More examples.
* More applications.

# Installation

## For users
You can install using the pip command:

    pip install git+https://github.com/fredhatt/estim2bapi.git

If you don't have pip in your Python distribution you can install it using,

    easy_install pip

or (on Debian-based systems like Raspbian):

    apt-get install python-pip

After installing, try the examples to check everything is working properly.

## For developers
Clone this repository and append its path to your PYTHONPATH variable. In Linux you would do this:

    git clone https://github.com/fredhatt/estim2bapi
    echo "export PYTHONPATH=$PYTHONPATH:$(pwd)/estim2bapi" >> ~/.bashrc
    source ~/.bashrc

# Usage
    import estim2b
    e2b = estim2b.Estim()
    # start processing commands  
    e2b.start()
    # set channel at to 50, wait for 5 seconds and set back to 0 again.   
    e2b.set_output("A", 50)
    e2b.wait(5)
    e2b.set_output("A", 0, block=True)
    
    
## Using multiple 2Bs
    import estim2b
    e2b_dev = []
    e2b_dev += [estim2b.Estim(device=/dev/ttyUSB0)]
    e2b_dev += [estim2b.Estim(device=/dev/ttyUSB1)]
    for e2b in e2b_dev:
        e2b.start()
        
    for e2b in e2b_dev:
        e2b.set_mode("milk)
        e2b.set_output("A", 20)
        e2b.set_output("B", 20)
        e2b.wait(10)
        e2b.wait(10)
        e2b.kill()
        
    for e2b in e2b_dev:
        e2b.stop() # stop threads before closing

For a more advanced (and useful) example see 
[applications/random_walk/random_walk.py](applications/random_walk/random_walk.py).