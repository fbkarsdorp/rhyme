
import os

# the server address
HOST = 'localhost'

# the port used for the timblserver
PORT = 50202

# Default string encoding used
ENCODING = 'utf-8'

#////////////////////////////////////////////////////////////////////////////
# Configuration for the different classifiers
#////////////////////////////////////////////////////////////////////////////

MBPT_CONFIG = dict(
    # the number of connections allowed by the TimblServer
    C = '10',
    # weighting meassure
    w = '1', # default Gain Ratio (See timbl for options)
    # The algorithm used
    a = '0', # default IB1 (original MBMA uses IGTree -a1)
    # the number of k's used in the classification
    k = '1',
    # We use inverse distance weighting
    #d = 'ID',
    # instancebase used by MBMA
    i = os.path.join(DATA, 'phonology.instancebase'))

MBSP_CONFIG = dict(
    # the number of connections allowed by the TimblServer
    C = '10',
    # weighting meassure
    w = '1', # default Gain Ratio (See timbl for options)
    # The algorithm used
    a = '0', # default IB1 (original MBMA uses IGTree -a1)
    # the number of k's used in the classification
    k = '1',
    # We use inverse distance weighting
    #d = 'ID',
    # instancebase used by MBMA
    i = os.path.join(DATA, 'stress.instancebase'))