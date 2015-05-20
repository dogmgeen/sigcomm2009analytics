import numpy as np
import os
import random

# Columns of interest for my application are:
#  0 - Timestamp
#  1 - User ID
#  2 - Seen User ID
USE_COLUMNS = (0, 1, 2)
FILE_DATA_TYPE = np.dtype('u4') 

# Load all records from the specified proximity file
def load(url):
  return np.loadtxt(
    url, dtype=FILE_DATA_TYPE, delimiter=";", usecols=USE_COLUMNS
  )


# Load only proximity records for participating members.
#  i.e. Remove any row that has a value >100 in the third column.
def loadParticipants(url):
  d = load(os.path.join(url, "proximity.csv"))
  return d[d[:,2] < 100]


# Create a set of participants of a given size.
#  This script loads the participants from the proximity file because
#  the participants file does not include user number 73.
def loadSubsetOfParticipants(url, num_participants_to_load, randomize=False):
  # Get only the active participants from the proximity file.
  d = np.unique(loadParticipants(url)[:,1])
  if num_participants_to_load is None:
    return d

  if randomize:
    return random.sample(d, num_participants_to_load)

  else:
    return d[:num_participants_to_load]


if __name__ == "__main__":
  records = loadParticipants(
    os.path.expanduser('~') + "/Downloads/sigcomm2009"
  )
  for r in records:
    print(r[1])
