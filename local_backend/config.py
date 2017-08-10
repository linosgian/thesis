import os
DEBUG = True

SQLALCHEMY_TRACK_MODIFICATIONS 	= True

DEFAULT_REP = 50
AGING_DECAY = 2
MIN_REP_VALUE = 30
LOCAL_DISTRICT = 'netmode'

TTP_HOST = '147.102.13.154'
TTP_PORT = '58080'
TTP_REP_INDEX = 'reputations'
TTP_AGGR_INDEX_PREFIX = 'ttp-aggregations-'

# Path to the local latest aggregation. Should be under ESclient/source/latest_aggr.json
LOCAL_LATEST_AGGR = os.environ['LATEST_AGGR_PATH']
