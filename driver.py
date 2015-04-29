# Author: Doug McGeehan (djmvfb@mst.edu)
#
# The purpose of this script is to perform an analysis on the contact durations
#  of the SIGCOMM 2009 dataset. Since this dataset does not have location
#  information, it is difficult to determine how long two nodes are in within
#  contact range of each other to determine if forwarding of data is
#  successful.
# I first use the proximity.csv dataset to detect when one node is aware of
#  another. Then, for each unique node u, I build a Node object that records
#  the contact instances for each node v. For this object, I can perform some
#  analyses on the time delta between two nodes.

import logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger("sigcomm09")
import argparse
import os
import csv
import collections
from input import proximity
import node
import datetime

SORT_BY_TIMESTAMP = lambda r: r.time


def draw_histogram_of_time_deltas(nodes):
  raw_deltas = []
  for n in nodes:
    raw_deltas.extend(n.get_all_time_deltas())

  # Eliminate all deltas greater than some threshold.
  def draw(raw_deltas, max_delta, step):
    deltas = [d for d in raw_deltas if d <= max_delta]

    max_delta = max(deltas)
    min_delta = min(deltas)

    print("Max delta: {0}".format(max_delta))
    print("Min delta: {0}".format(min_delta))
  
    bin_width = range(0, max_delta, step)

    n, bins, patches = pyplot.hist(x=deltas, bins=bin_width, log=True)
    for i in range(len(n)):
      print("[{0}, {1}) \t=> {2}".format(bins[i], bins[i+1], n[i]))

    min_x, max_x = min_delta, max_delta
    min_y, max_y = 0, max(n)*1.1

    pyplot.axis([min_x, max_x, min_y, max_y])
    pyplot.ylabel("Number of consecutive contacts (log base 10)")
    pyplot.xlabel("Waiting time between consecutive contacts from all pairs (u, v)")
    pyplot.savefig("hist_max{0}_step{1}.png".format(max_delta, step))
    pyplot.clf()

  draw(raw_deltas, 5000, 10)
  draw(raw_deltas, 20000, 10)
  draw(raw_deltas, 2000, 1)


def get_arguments():
  parser = argparse.ArgumentParser(
    description='SIGCOMM 2009 Contact Trace Analysis'
  )
  parser.add_argument(
    '-i', '--input-file',
    dest="proximity_url",
    help='path/to/proximity.csv',
    required=True,
  )

  args = parser.parse_args()
  return args


def write_out_to_file(output, output_file_url):
  with open(output_file_url, "w") as f:
    writer = csv.DictWriter(f, fieldnames=OUTPUT_FIELD_NAMES, delimiter=" ")
    for r in output:
      # Each record is an associated contact/handshake. To fit the format of
      #  the ONE simulator's StandardEventsReader, each handshake needs to
      #  specify when the connection initiated and when disconnection occurred.
      #  We assume disconnection occurs immediately after connection.
      writer.writerow(r)


if __name__ == "__main__":
  print("SIGCOMM 2009 Contact Trace Analysis")
  print("Written by Doug McGeehan (djmvfb@mst.edu)")
  print("Released into the Public Domain")  # it's a simple script, after all
  print("")
  args = get_arguments()

  # Load raw records from file, converting to integer types
  contact_records = proximity.loadParticipants(args.proximity_url)

  # Construct the nodes and the unique underlying contact times.  
  nodes = node.createFromRecords(contact_records)
  logger.info("Number of unique nodes: {0}".format(len(nodes)))

  contact_events = []
  for n in nodes:
    contact_events.extend(n.get_contact_events(timeout=250))
  contact_events.sort(key=SORT_BY_TIMESTAMP)

  logger.info("Duration of contacts: {0} ({1} seconds)".format(
    datetime.timedelta(seconds=int(contact_events[0].MAX_TIME)),
    contact_events[0].MAX_TIME
  ))

  with open('sessions_for_ONE.txt', 'w') as f:
    for c in contact_events:
      f.write("{0}\n".format(c))
