![Contributions welcome](https://img.shields.io/badge/contributions-welcome-brightgreen.svg)
[![License](https://img.shields.io/badge/license-MIT%20License-brightgreen.svg)](https://opensource.org/licenses/MIT)

# About estim2bapi
This is an (unofficial) Python API for the E-Stim 2B. Note that this is alpha software, and 
thus comes with absolutely no warranty whatsoever. Use at your own risk.

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
    # import the module and connect to 2B connected to ttyUSB0 (Linux)...
    import estim2b
    e2b = estim2b.Estim('/dev/ttyUSB0')
    # get status from 2B...
    e2b.status()

For a simple usage example see example.py.
