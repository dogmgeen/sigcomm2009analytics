import logging
logger = logging.getLogger("sigcomm09.node")
import collections
from contact import ContactsWithUniqueNode
from contact import Contact

def createFromRecords(records):
  # Since a new node may occur at any time, the node's object must already
  #  be present in the dictionary.
  nodes = collections.defaultdict(Node)
  for r in records:
    nodes[r[1]].add_contact(r)

  print("#"*80)
  logger.info("Created {0} unique nodes".format(len(nodes)))
  return nodes.values()


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

  def get_contact_events(self, timeout):
    # This needs to return a list of ContactEvent objects.
    events = []
    for k in self.contacts:
      contacts_with_v = self.contacts[k]
      events.extend(contacts_with_v.get_contact_events(timeout))

    return events


