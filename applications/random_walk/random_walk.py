import argparse
import time
import numpy as np
import estim2b


def do_random_step(e2b, channel, step_size, mini, maxi):
    delta = np.random.choice([-step_size, step_size])
    new = e2b.status[channel] + delta
    if new > maxi or new < mini:
        new = mini
    return new


if __name__ == "__main__":

    '''Read the command line arguments. Note that --devices supports multiple devices'''
    parser = argparse.ArgumentParser()
    parser.add_argument("--power", default="L", type=str, help="Power level of 2B, H or L.")
    parser.add_argument("--A_min_max", default=[10, 75], type=int, nargs="+")
    parser.add_argument("--B_min_max", default=[10, 75], type=int, nargs="+")
    parser.add_argument("--C_min_max", default=[2, 100], type=int, nargs="+")
    parser.add_argument("--D_min_max", default=[2, 100], type=int, nargs="+")
    parser.add_argument("--devices", default=["auto"], type=str, nargs="+")
    parser.add_argument("--time_step", default=1, type=float)
    parser.add_argument("--step_size", default=3, type=int)
    parser.add_argument("--reset_at_max", default=True, action="store_true")
    parser.add_argument("--dryrun", action="store_true")
    parser.add_argument("--verbose", type=int, default=1)
    parser.add_argument("--mode", type=str)
    args = parser.parse_args()

    '''Initialise the devices'''
    e2bs = []
    for dev in args.devices:
        e2b = estim2b.Estim(device=dev, verbose=args.verbose, dryrun=args.dryrun, recv_responses=True)
        e2b.start()

        if args.mode is not None:
            e2b.set_mode(args.mode, block=True)

        if args.power == "H":
            e2b.set_high(block=True)
        else:
            e2b.set_low(block=True)

        e2b.set_output("A", args.A_min_max[0])
        e2b.set_output("B", args.B_min_max[0])
        e2bs += [e2b]

    try:

        '''Enter the main loop, at each time step the devices are updated'''
        new_as, new_bs = np.zeros(len(e2bs), dtype=int), np.zeros(len(e2bs), dtype=int)
        while True:
            time.sleep(args.time_step)
            for i, e2b in enumerate(e2bs):
                new_as[i] = do_random_step(e2b, channel="A", step_size=args.step_size,
                                       mini=args.A_min_max[0], maxi=args.A_min_max[1])
                new_bs[i] = do_random_step(e2b, channel="B", step_size=args.step_size,
                                       mini=args.B_min_max[0], maxi=args.B_min_max[1])


                print(i, new_as[i], new_bs[i])

                e2b.set_output("A", new_as[i])
                e2b.set_output("B", new_bs[i])

    except KeyboardInterrupt:
        for e2b in e2bs:
            print("Ctrl+C received, zeroing outputs and stopping.")
            e2b.stop()
