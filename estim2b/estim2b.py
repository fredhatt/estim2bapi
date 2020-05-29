#! env python
from pathlib import Path

import serial
from serial.tools import list_ports
import time
import sys
import platform
from queue import Queue
from threading import Thread
import yaml
import logging


def _read_status_value(value):
    try:
        v = int(value)
    except ValueError:
        v = str(value)
    return v


def wait_for_command(command):
    while True:
        if command.has_run: break


def get_comm_ports():
    return list_ports.comports()

def get_ftdi_ports():
    all_ports = get_comm_ports()
    return [a.device for a in all_ports if a.manufacturer == "FTDI"]


class Command:

    def __init__(self, command):
        self.created_at = time.time()
        self._command = command
        self.ran_at = None
        self.response = None

    def __call__(self):
        # self.ran_at = time.time()
        return self._command

    def finished(self):
        self.ran_at = time.time()

    @property
    def has_run(self):
        if self.ran_at is None:
            return False
        return True
    

class Estim(Thread):
    def __init__(self, device="auto", baudrate=9600, timeout=0, verbose=1, dryrun=False,
                 delay=0.05, recv_responses=True):
        Thread.__init__(self)
        level = logging.INFO
        if verbose <= 0 or verbose == "quiet":
            level = logging.ERROR
        elif verbose == 1 or verbose == "info":
            level = logging.INFO
        elif verbose >= 2 or verbose == "debug":
            level = logging.DEBUG
        logging.basicConfig(
            level=level, format='%(asctime)s | %(threadName)s: [%(module)s:%(funcName)s] %(levelname)s: %(message)s')
        self.dryrun = dryrun
        self.delay = delay
        self.serialconn = None
        self.recv_responses = recv_responses
        self.queue = Queue()
        self.stopped = False
        self.pause = True # start paused, until start is run.
        self.channel_ranges = {"A": [0, 100], "B": [0, 100], "C": [2, 100], "D": [2, 100]}
        self.command_history = []
        self.modes = {}

        if not self.dryrun and device == "auto":
            ftdi_ports = get_ftdi_ports()
            if len(ftdi_ports) == 0:
                logging.error("No 2B compatible device connected: check the USB cable.")
                sys.exit(1)
            if len(ftdi_ports) > 1:
                logging.warn(f"Found {len(ftdi_ports)} 2B devices. Using the first detected. "
                             f"If you intend to use multipe 2B devices at once set device when calling this class.")
            device = ftdi_ports[0]
            logging.info(f"Detected 2B at {device}.")

        self.status = {"battery": None,
                       "A": None, "B": None, "C": None, "D": None,
                       "mode": None, "power": None, "joined": None, "firmware": None}

        if not dryrun:
            self.serialconn = self._connect(device, baudrate, timeout)
            if self._check_conection():
                logging.info(f"Successfully open serial device {device}")
        else:
            logging.info("Running in dryrun mode, commands not sent to device.")


        self.get_status(force_update=True)
        config_path = f"{str(Path(__file__).parent)}/config/"
        specific_config = config_path + f"config_{self.status['firmware']}.yaml"
        if Path(specific_config).is_file():
            self._read_modes(specific_config)
        else:
            self._read_modes(config_path + "config.yaml")

    def _read_modes(self, fn):
        logging.debug(f"Reading modes from {fn}")
        with open(fn, "r") as f:
            self.modes = yaml.safe_load(f)

    def print_available_modes(self):
        print("Available modes:")
        for k, v in self.modes.items():
            print(f"mode(string):  {k:12s}  mode(id):  {v}")

    @property
    def available_modes(self):
        return list(self.modes.keys())

    def get_status(self, force_update=False):
        if force_update:
            logging.debug("Forcing update of device status.")
            self._send(" ")
            r = self._recv()
            self._parse_reply(r)
        return self.status

    def _recv(self):
        time.sleep(self.delay)
        if self.dryrun:
            reply_string = "512:66:00:50:50:1:L:0:0"
        else:
            reply_string = self.serialconn.readline()
        logging.debug(f"Received: {reply_string}")
        return reply_string.decode().strip()

    def _parse_reply(self, reply_string):
        if not ":" in reply_string: #check, if reply isn't empty
                logging.error("invalid (empty) response string from 2B.")
                return False
        else:
                r = reply_string.split(":")
                for i, key in enumerate(self.status.keys()):
                    self.status[key] = _read_status_value(r[i])
                return self.status

    def _connect(self, device, baudrate, timeout):
        try:
            serialconn= serial.Serial(
                device,
                baudrate,
                timeout=timeout,
                bytesize=serial.EIGHTBITS,
                parity=serial.PARITY_NONE,
                stopbits=serial.STOPBITS_ONE)
        except Exception as e:
            logging.error(f"Error opening serial device: {device} with baud rate {baudrate}")
            raise(e)
        return serialconn

    def _check_conection(self):
        return self.serialconn.isOpen()

    def _flush(self):
        if not self.dryrun:
            self.serialconn.flushInput()

    def _send(self, send_string):
        logging.debug(f"{send_string}")
        if self.dryrun:
            print(f"_send:{send_string}")
        else:
            command = send_string + "\n\r"
            self.serialconn.write(command.encode())

    def run(self):
        self.pause = False
        while True:
            time.sleep(self.delay)

            if self.stopped:
                break
            if not self.pause:
                command = self.queue.get()
                cmd = command()
                if len(cmd) > 0 and cmd[0] == "t":
                    time.sleep(float(cmd[1:]))

                if cmd == "stop":
                    break

                self._send(cmd)
                logging.debug(f"running command {cmd}")

                if self.recv_responses:
                    logging.debug(f"receiving response from 2B")
                    command.response = self._recv()
                    self._parse_reply(command.response)
                self.command_history += [command]
                command.finished()

    def wait(self, time_seconds, block=False):
        return self._queue_command(f"t{time_seconds}", block)

    def _queue_command(self, command, block=False):
        if self.pause and block:
            logging.error("Cannot queue a blocking command while paused. Have you run start()?")
            return False
        this_command = Command(command)
        self.queue.put(this_command)
        if block:
            logging.debug("Blocking main thread until command has run")
            wait_for_command(this_command)
        return this_command

    def link_channels(self, block=False):
        return self._queue_command("J1", block)

    def unlink_channels(self, block=False):
        return self._queue_command("J0", block)

    def set_high(self, block=False):
        return self._queue_command("H", block)

    def set_low(self, block=False):
        return self._queue_command("L", block)

    def kill(self, instant=False, block=False):
        if instant:
            # remove all existing commands from the queue
            self.pause = True
            self.queue.queue.clear()
            self.pause = False
        return self._queue_command("K", block)

    def reset(self, block=False):
        return self._queue_command("R", block)

    def stop(self, instant=False, kill=True):
        if instant:
            self.stopped = True
        if kill:
            self.kill(block=True)
        self._queue_command("stop")

    def set_output(self, channel, value, block=False):
        # check the channel is valid
        if not channel in self.channel_ranges.keys():
            logging.error(f"{channel} is not a valid channel.")
            return False
        # check the value is valid
        min_channel_value = self.channel_ranges[channel][0]
        max_channel_value = self.channel_ranges[channel][1]
        if value < min_channel_value or value > max_channel_value:
            logging.error(f"channel {channel} value must be in range [{min_channel_value}, {max_channel_value}].")
            return False
        return self._queue_command(f"{channel}{value}", block)

    def set_mode(self, mode_str, block=False):
        if not mode_str in self.modes.keys():
            logging.error(f"{mode_str} is not a valid mode.")
            return False
        mode_id = self.modes[mode_str]
        return self._queue_command(f"M{mode_id}", block)




if __name__ == "__main__":
    e2b = Estim(dryrun=True, verbose=2, delay=1)
    e2b.print_available_modes()
    e2b.start()
    status = e2b.get_status(force_update=True)
    print("status:", status)
    e2b.set_output("A", 50)
    e2b.wait(5)
    e2b.set_output("A", 0, block=True)
    e2b.set_mode("spam")
    # e2b.link_channels()
    # e2b.unlink_channels()
    # e2b.set_high()
    # e2b.set_output("A", 50)
    # e2b.set_mode("bounce")
    # e2b.wait(3.1)
    # cmd = e2b.kill(instant=False)
    # print(cmd.has_run)
    # time.sleep(10)
    # print(cmd.has_run)
    # e2b.stop()




