import sys
from datetime import timedelta

from pyopendds import init_opendds, DomainParticipant, StatusKind, PyOpenDDS_Error
import pybasic.basic

if __name__ == "__main__":
    try:
        # Initialize OpenDDS and Create DDS Objects
        init_opendds(opendds_debug_level=1)
        part = DomainParticipant(34)
        topic = part.create_topic('Readings', pybasic.basic.Reading)
        sub = part.create_subscriber()
        dr = sub.create_datareader(topic)

        # Wait for Publisher to Connect
        print('Waiting for Publisher...')
        dr.wait_for(StatusKind.SUBSCRIPTION_MATCHED, timedelta(seconds=15))
        print('Found Publisher!')

        # Read and Print Sample
        print(dr.take_next_sample())

        print('Done!')

    except PyOpenDDS_Error as e:
        sys.exit(e)
