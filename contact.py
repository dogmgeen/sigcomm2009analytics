
class Contact:
  def __init__(self, contact_record):
    # A node u sees a node v.
    self.u = contact_record[1]
    self.v = contact_record[2]
    self.time = contact_record[0]


  def time_delta(self, another_contact):
    if self.time < another_contact.time:
      return another_contact.time - self.time

    else:
      return self.time - another_contact.time

  def summary(self):
    print("  Time {0}".format(self.time))

  def __lt__(self, other):
    return self.time < other.time


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


