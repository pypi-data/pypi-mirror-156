"""
Created on Fri Jun 24 10:40:13 2022

@author: jtm

Demonstrates how to use the .light_stamper(...) and pupil_grabber(...) methods
to measure and plot a simple PLR relative to the onset of any light source
detectable by the Pupil Core World Camera, such as a light switch in a dark
room.
"""

import sys
from time import sleep

from pyplr.pupil import PupilCore
from pyplr.utils import unpack_data_pandas


def main():
    try:
        # Connect to Pupil Core
        p = PupilCore()

        # Start a new recording called "my_recording"
        p.command('R my_recording')

        # Wait a few seconds
        sleep(2)

        # Make an annotation for when the light comes on
        annotation = p.new_annotation('LIGHT_ON')

        # Start the .light_stamper(...) and .pupil_grabber(...)
        lst_future = p.light_stamper(annotation=annotation, timeout=10)
        pgr_future = p.pupil_grabber(topic='pupil.1.3d', seconds=10)

        ##################################
        # Administer light stimulus here #
        ##################################

        # Wait for the futures
        while lst_future.running() or pgr_future.running():
            print('Waiting for futures...')
            sleep(1)

        # End recording
        p.command('r')

        # Get the timestamp and pupil data
        timestamp = lst_future.result()[1]
        data = unpack_data_pandas(pgr_future.result())

        # Plot the PLR
        ax = data['diameter_3d'].plot()
        ax.axvline(x=timestamp, color='k')

    except KeyboardInterrupt:
        print('> Experiment terminated by user.')
        sys.exit(0)


if __name__ == '__main__':
    main()
