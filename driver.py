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
import sys
import os
import csv
import collections
from matplotlib import pyplot
import pylab
import numpy
from input import proximity
from contact import Contact
from contact import ContactsWithUniqueNode

SORT_BY_TIMESTAMP = lambda r: r.time

class ContactsWithUniqueNode:
  def __init__(self):
    self.u = None
    self.v = None
    self.contacts = []
    self.is_sorted = False


  def add_contact(self, record):
    if self.u is None:
      self.u = record.u
    if self.v is None:
      self.v = record.v

    assert self.u == record.u, "The seeing node of this record is not equal to my seeing node!"
    assert self.v == record.v, "The seen node of this record is not equal to my seen node!"

    self.contacts.append(record)


  def summary(self):
    print("  {0} => {1}".format(self.u, self.v))
    print("  {0} contact instances recorded".format(len(self.contacts)))
    if not self.is_sorted:
      self.contacts.sort(key=SORT_BY_TIMESTAMP)
      self.is_sorted = True

    self.contacts[0].summary()
    for delta, next_contact in self.get_next_time_delta(True):
      print("    {0} seconds apart".format(delta))
      next_contact.summary()


  def draw(self):
    fig, ax = pyplot.subplots()
    deltas = [d for d in self.get_next_time_delta()]
    num_items = range(len(deltas))
    width = 0.35
    bars = ax.bar(left=num_items, height=deltas, width=width, color='r')

    ax.set_ylabel('Time between consecutive contacts')
    ax.set_title('Time deltas between Node {0} to Node {1}'.format(
      self.u,
      self.v
    ))
    ax.set_xticks([i+width for i in num_items])
    ax.set_xticklabels([i for i in num_items])

    for rect in bars:
        height = rect.get_height()
        ax.text(rect.get_x()+rect.get_width()/2., 1.05*height, '%d'%int(height),
                ha='center', va='bottom')

    pyplot.savefig("{0}_to_{1}.png".format(self.u, self.v))
    pyplot.clf()
    pyplot.close(fig)


  def get_next_time_delta(self, include_contact=False):
    iterator = range(0, len(self.contacts)-1)
    for i in iterator:
      next_contact = self.contacts[i+1]
      if include_contact:
        yield self.contacts[i].time_delta(next_contact), next_contact
      else:
        yield self.contacts[i].time_delta(next_contact)


  def get_contact_events(self):
    # If u only contacted v once, then create only one contact event.
    if len(self.contacts) == 1:
      return [
        ContactEvent(
          u=self.u, v=self.v, is_up=True, time=self.contacts[0].time
        ),
        ContactEvent(
          u=self.u, v=self.v, is_up=False, time=self.contacts[0].time+120
        )
      ]

    else:
      # Consecutive contacts that are within 180 seconds of each other are
      #  considered part of the same contact duration. Thus count them all up.
      previous_contact_event = self.contacts[0]
      contact_events = [ContactEvent(
        u=self.u, v=self.v, is_up=True, time=previous_contact_event.time
      )]
      for d, contact in self.get_next_time_delta(include_contact=True):
        if d > 180:
          contact_events.append(ContactEvent(
            u=self.u, v=self.v, is_up=False, time=previous_contact_event.time+120
          ))
          contact_events.append(ContactEvent(
            u=self.u, v=self.v, is_up=True, time=contact.time
          ))
        previous_contact_event = contact
      return contact_events


class ContactEvent:
  def __init__(self, u, v, is_up, time):
    self.u = u
    self.v = v
    self.is_up = is_up
    if is_up:
      self.time = time-5
    else:
      self.time = time


  def __str__(self):
    return "{time} CONN {u} {v} {up_or_down}".format(
      u=self.u,
      v=self.v,
      time=self.time,
      up_or_down="up" if self.is_up else "down"
    )


class Node:
  def __init__(self):
    self.id = None
    self.contacts = collections.defaultdict(ContactsWithUniqueNode)

  def add_contact(self, record):
    if self.id is None:
      self.id = record[1]
    self.contacts[record[2]].add_contact(Contact(record))

  def summary(self):
    print("-"*40)
    print("Node #{0} made contact with {1} unique nodes".format(
      self.id,
      len(self.contacts)
    ))
    print("")

    for k in self.contacts:
      v = self.contacts[k]
      v.summary()


  def get_all_time_deltas(self):
    deltas = []
    for k in self.contacts:
      v = self.contacts[k]
      deltas.extend([d for d in v.get_next_time_delta()])
    return deltas


  def get_contact_events(self):
    # This needs to return a list of ContactEvent objects.
    events = []
    for k in self.contacts:
      contacts_with_v = self.contacts[k]
      events.extend(contacts_with_v.get_contact_events())

    return events


def create_nodes(records):
  # Since a new node may occur at any time, the node's object must already
  #  be present in the dictionary.
  nodes = collections.defaultdict(Node)
  for r in records:
    nodes[r[1]].add_contact(r)

  print("#"*80)
  print("Created {0} unique nodes".format(len(nodes)))
  return nodes.values()


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


def print_usage(script_name):
  print("#"*80)
  print("Usage:")
  print(
  " $ python3 {script_name} path/to/input_file.csv".format(
    script_name=script_name
  ))
  print("#"*80)
  sys.exit(1)


def main(args):
  print("SIGCOMM 2009 Contact Trace Analysis")
  print("Written by Doug McGeehan (djmvfb@mst.edu)")
  print("Released into the Public Domain")  # it's a simple script, after all
  print("")
  if len(args) < 2:
    print_usage(script_name=args[0])

  input_file = args[1]
  contact_records = proximity.loadParticipants(input_file)
  nodes = create_nodes(contact_records)
  node_ids = [n.id for n in nodes]

  contact_pairs = []
  for u in list(node_ids):
    for v in node_ids:
      if u != v:
        contact_pairs.append((u, v))

  contact_events = []
  for n in nodes:
    contact_events.extend(n.get_contact_events())
  max_contact_event = max(contact_events, key=SORT_BY_TIMESTAMP)

  with open('all_contacts.txt', 'w') as f:
    for start in contact_pairs:
      f.write("1 CONN {u} {v} up\n".format(u=start[0], v=start[1]))

    for end in contact_pairs:
      f.write("{ending_time} CONN {u} {v} down\n".format(
        u=end[0], v=end[1], ending_time=max_contact_event.time
      ))


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
  main(sys.argv)
