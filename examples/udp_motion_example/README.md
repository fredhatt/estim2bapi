# Full working example of a motion sensor using UDP

If you want to get up and running quickly use the [Wireless IMU](https://play.google.com/store/apps/details?id=org.zwiener.wimu&hl=en_GB) Android app from the Google Play store.

This is a fully-working example using a motion sensor with 2B.
This uses two devices, a small client device which reads from an
accelerometer and a server that is connected to the E-stim 2B powerbox.

This has been tested using the Wireless IMU Android app.

The server may be a laptop, desktop or even a Raspberry Pi device on the 
same network as the client. The server receives a stream of data from the client and
processes this to figure out if the angle of the accelerometer has changed, or if
there has been general movement. All the processing is done on the server, this makes 
it really easy to implement new clients.

# Usage

First, on the server (the computer connected to the 2B) run,

    python ./start_estim2b_server.py

Include any command line arguments you wish, for details see `python ./start_estim2b_server.py -h`.

On your Android mobile phone start the Wireless IMU app, point it to the IP address of your server device
and set the port to 8089 (by default). You probably want to set the update rate to "medium".
When you're ready press "Activate Wireless Stream" in the app.

