import numpy as np
import os
import random

# Columns of interest for my application are:
#  0 - User ID
#  1 - Affiliation key (Institute, City, Country)
#  2 - Affiliation value
FILE_DATA_TYPE = np.dtype([
  ('id', np.uint8),
  ('key', 'S8'),
  ('val', np.uint8)
])

# Load all records from the specified participant file
def load(url):
  return np.loadtxt(
    url, dtype=FILE_DATA_TYPE, delimiter=";",
  )


# Create a set of participants of a given size.
def loadSubset(url, num_participants_to_load, randomize=False):
  f = os.path.join(url, "participants.csv")
  d = np.unique(
    np.loadtxt(
      f, dtype=np.dtype('u4'), delimiter=";", usecols=(0,),
    )
  )
  if num_participants_to_load is None:
    return d

  if randomize:
    return random.sample(d, num_participants_to_load)

  else:
    return d[:num_participants_to_load]


# Identify the key-value space.
concat_record_elements = lambda r: "{1}{2}".format(*r)
def getAffiliationSpace(url):
  d = load(os.path.join(url, "participants.csv"))
  return set(map(concat_record_elements, d))


# User IDs need to start at 0. Thus, each user ID is offset by -1.
user_and_concat_record_elements = lambda r: "{0};{1}{2}".format(r[0]-1, r[1], r[2])
def loadMergedAffiliations(url):
  d = load(os.path.join(url, "participants.csv"))
  return map(user_and_concat_record_elements, d)


if __name__ == "__main__":
  url = os.path.expanduser('~') + "/Downloads/sigcomm2009"
  print(loadMergedAffiliations(url))
