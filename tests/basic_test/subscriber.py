import sys

from pyopendds import *
import pybasic

debug = False

if __name__ == "__main__":
  try:
    # Initialize OpenDDS and Create DDS Objects
    args = ['-DCPSConfigFile', 'rtps.ini']
    if debug:
      args.extend(['-DCPSDebugLevel', '10'])
    init_opendds(*args)
    part = DomainParticipant(34)
    topic = part.create_topic('Readings', pybasic.basic.Reading)
    sub = part.create_subscriber()
    dr = sub.create_datareader(topic)

    # Wait for Publisher to Connect
    print('Waiting for Publisher...')
    dr.wait_for(StatusKind.SUBSCRIPTION_MATCHED, 15)
    print('Found Publisher!')

    print('Done!')

  except PyOpenDDS_Error as e:
    sys.exit(e)
