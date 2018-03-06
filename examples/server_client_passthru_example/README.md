# Simple remote control of E-stim 2B using TCP sockets

This demonstrates the EstimSocket module. If you just want to try it out first start the server
on the computer that's physically connected to your E-stim 2B:

    python ./start_estim2b_server.py

And then on another computer on the same network run the client:

    python ./client.py

The client script will ask you for commands (which are documented in the E-stim 2B developers manual), 
the commands are sent to to the server using TCP sockets.

# Doing custom things

If you want create a custom client/server application, you shouldn't need to modify anything
in the `EstimSocket` module. 
The `start_server` function takes two arguments, `callbacks` and `on_close`.

- `callbacks`: a Python-list of functions that are run (in order) whenever the server received
data from a client. Callback functions must take two arguments, the data sent (`buf`) and the address
of the client that sent it (`address`)

- `on_close`: a function that is run if the client disconnects for any reason. In most cases running
the `kill()` function from `Estim` is a good idea to turn all outputs to zero.
    

