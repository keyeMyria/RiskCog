import os,sys,subprocess,time
import sector

ISOTIMEFORMAT = '%Y%m%d%H%M%S'
tag = str(time.strftime(ISOTIMEFORMAT))
sector.sector('arya' , 5  , 'selflist','otherlist')



