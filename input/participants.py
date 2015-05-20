import numpy as np
import os

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


# Identify the key-value space.
concat_record_elements = lambda r: "{1}{2}".format(*r)
def getAffiliationSpace(url):
  d = load(os.path.join(url, "participants.csv"))
  return set(map(concat_record_elements, d))


# User IDs need to start at 0. Thus, each user ID is offset by -1.
def loadMergedAffiliations(url, username_mapping):
  d = load(os.path.join(url, "participants.csv"))
  affiliationsFromSelectedUsers = []
  for r in d:
    if r[0] in username_mapping.keys():
      affiliationsFromSelectedUsers.append((
        username_mapping[r[0]], r[1], r[2]
      ))

  user_and_concat_record_elements = lambda r: "{0};{1}{2}".format(*r)
  return map(user_and_concat_record_elements, affiliationsFromSelectedUsers)


if __name__ == "__main__":
  url = os.path.expanduser('~') + "/Downloads/sigcomm2009"
  print(loadMergedAffiliations(url))
