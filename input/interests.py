import numpy as np

# Columns of interest for my application are:
#  0 - User ID
#  1 - Facebook group ID
FILE_DATA_TYPE = np.dtype(np.uint16)

# Load all records from the specified participant file
def load(url):
  return np.loadtxt(
    url, dtype=FILE_DATA_TYPE, delimiter=";",
  )


# Identify the key-value space from the participants' Facebook account.
def getFacebookInterestSpace(url):
  d = load(url)
  return np.unique(d[:,1])


# Identify the key-value space from the participants' evolved interests
#  as the data collection was in progress.
def getEvolvedInterestSpace(url):
  d = load(url)
  return np.unique(d[:,1])

def getTotalInterestSpace(evolved_interest_url, facebook_interest_url):
  facebook_interests = getFacebookInterestSpace(facebook_interest_url)
  evolved_interests = getEvolvedInterestSpace(evolved_interest_url)
  return np.unique(np.concatenate(
    (facebook_interests, evolved_interests)
  ))


if __name__ == "__main__":
  import os
  fb_url = os.path.expanduser('~') + "/Downloads/sigcomm2009/interests1.csv"
  evolved_url = os.path.expanduser('~') + "/Downloads/sigcomm2009/interests2.csv"
  print(getEvolvedInterestSpace(evolved_url))
  print(getTotalInterestSpace(
    evolved_interest_url=evolved_url, facebook_interest_url=fb_url
  ))
