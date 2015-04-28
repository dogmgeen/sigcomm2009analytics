import numpy as np

# Columns of interest for my application are:
#  0 - Timestamp
#  1 - User ID
#  2 - Seen User ID
USE_COLUMNS = (0, 1, 2)
FILE_DATA_TYPE = np.dtype('u4') 

def load(url):
  return np.loadtxt(
    url, dtype=FILE_DATA_TYPE, delimiter=";", usecols=USE_COLUMNS
  )
