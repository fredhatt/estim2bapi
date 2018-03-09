# Full working example of a motion sensor

This is a fully-working example using a motion sensor with 2B.
This uses two devices, a small client device which reads from an
accelerometer and a server that is connected to the E-stim 2B powerbox.

In my own set-up I have an ADXL345 attached to a Raspberry Pi Zero W.
This is glued down to a small Li-ion battery, so that it can be a fully-remote
sensor. On this device I run `client.py`, which just streams TCP packets to
my server.

The server may be a laptop, desktop or even another Raspberry Pi like device on the 
same network as the client. The server receives a stream of data from the client and
processes this to figure out if the angle of the accelerometer has changed, or if
there has been general movement. All the processing is done on the server, this makes 
it really easy to implement new clients (in fact your could use your mobile phone if 
you wrote an app to send TCP packets containing `"time:x:y:z"` to the server!

# Usage

First, on the server (the computer connected to the 2B) run,

    python ./start_estim2b_server.py

Include any command line arguments you wish, for details see `python ./start_estim2b_server.py -h`.

On the client (i.e. sensor) device run,

    client.py --address [IP address of the server]

By default there is a short (10s) calibration period, this can be configured if necessary.

