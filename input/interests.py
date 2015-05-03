import numpy as np
import os

# Columns of interest for my application are:
#  0 - User ID
#  1 - Facebook group ID
FILE_DATA_TYPE = np.dtype(np.uint16)

# Load all records from the specified participant file
def load(url):
  return np.loadtxt(
    url, dtype=FILE_DATA_TYPE, delimiter=";", usecols=(0,1)
  )


# Identify the key-value space from the participants' Facebook account.
def getFacebookInterestSpace(url):
  d = load(os.path.join(url, "interests1.csv"))
  return np.unique(d[:,1])


# Identify the key-value space from the participants' evolved interests
#  as the data collection was in progress.
def getEvolvedInterestSpace(url):
  d = load(os.path.join(url, "interests2.csv"))
  return np.unique(d[:,1])


def getTotalInterestSpace(dataset_url):
  facebook_interests = getFacebookInterestSpace(dataset_url)
  evolved_interests = getEvolvedInterestSpace(dataset_url)
  return np.unique(np.concatenate(
    (facebook_interests, evolved_interests)
  ))


def loadInterests(dataset_url):
  facebook_interests = load(os.path.join(dataset_url, "interests1.csv"))
  evolved_interests = load(os.path.join(dataset_url, "interests2.csv"))
  all_interests = np.concatenate((facebook_interests, evolved_interests))
  for i in all_interests:
    yield "{0};{1}".format(i[0]-1, i[1])


if __name__ == "__main__":
  dataset_url = os.path.expanduser('~') + "/Downloads/sigcomm2009"
  d = loadInterests(
    dataset_url=dataset_url
  )
  print(d[d[:,1] >= 1000])
