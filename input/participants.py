import numpy as np

# Columns of interest for my application are:
#  0 - User ID
#  1 - Affiliation key (Institute, City, Country)
#  2 - Affiliation value
FILE_DATA_TYPE = np.dtype({
  'names': ['userID', 'key', 'val'],
  'formats': [np.uint8, 'S8', np.uint8],
})

# Load all records from the specified participant file
def load(url):
  return np.loadtxt(
    url, dtype=FILE_DATA_TYPE, delimiter=";",
  )


# Identify the key-value space.
concat_record_elements = lambda r: "{1}{2}".format(*r)
def getAffiliationSpace(url):
  d = load(url)
  return set(map(concat_record_elements, d))


if __name__ == "__main__":
  import os
  url = os.path.expanduser('~') + "/Downloads/sigcomm2009/participants.csv"
  print(getAffiliationSpace(url))
