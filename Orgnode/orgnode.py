# Copyright (c) 2010 Charles Cave
#
#  Permission  is  hereby  granted,  free  of charge,  to  any  person
#  obtaining  a copy  of  this software  and associated  documentation
#  files   (the  "Software"),   to  deal   in  the   Software  without
#  restriction, including without limitation  the rights to use, copy,
#  modify, merge, publish,  distribute, sublicense, and/or sell copies
#  of  the Software, and  to permit  persons to  whom the  Software is
#  furnished to do so, subject to the following conditions:
#
#  The above copyright notice and this permission notice shall be
#  included in all copies or substantial portions of the Software.
#
#  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
#  EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
#  MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
#  NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS
#  BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN
#  ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
#  CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
#  SOFTWARE.

# Program written by Charles Cave   (charlesweb@optusnet.com.au)
# Program lightly maintained by Christopher E. Mower (c.mower@ed.ac.uk)
# February - March 2009
# Version 2 - June 2009
#   Added support for all tags, TODO priority and checking existence of a tag
# Version 3 - January 2022 (by C. E. Mower)
#   Parsed main `orgnode.py` to Python 3
#   Simple installation via pip, see below
#   Several updates to Org-mode file parsing (see commits)
#   Modified interface for `makelist` method:
#     Before: nodelist = Orgnode.makelist(filename)
#     Now: root, nodelist = Orgnode.makelist(filename) where root is a string containing everything before the first node
# More information at
#    http://members.optusnet.com.au/~charles57/GTD

"""
The Orgnode module consists of the Orgnode class for representing a
headline and associated text from an org-mode file, and routines for
constructing data structures of these classes.
"""

import re, sys
import datetime

def makelist(filename):
   """
   Read an org-mode file and return a list of Orgnode objects
   created from this file.
   """
   ctr = 0

   try:
      f = open(filename, 'r')
   except IOError:
      print("Unable to open file [%s] " % filename)
      print("Program terminating.")
      sys.exit(1)

   todos         = dict()  # populated from #+SEQ_TODO line
   todos['TODO'] = ''   # default values
   todos['DONE'] = ''   # default values
   level         = 0
   heading       = ""
   bodytext      = ""
   tag1          = ""      # The first tag enclosed in ::
   alltags       = []      # list of all tags in headline
   sched_date    = ''
   deadline_date = ''
   nodelist      = []
   propdict      = dict()

   in_src_block = False
   found_first_heading = False
   root = ""

   for line in f:
       ctr += 1
       hdng = re.search('^(\*+)\s(.*?)\s*$', line)
       if hdng:
          found_first_heading = True
          if heading:  # we are processing a heading line

             thisNode = Orgnode(level, heading, bodytext, tag1, alltags)
             if sched_date:
                thisNode.setScheduled(sched_date)
                sched_date = ""
             if deadline_date:
                thisNode.setDeadline(deadline_date)
                deadline_date = ''
             thisNode.setProperties(propdict)
             nodelist.append( thisNode )
             propdict = dict()
          level = hdng.group(1)
          heading =  hdng.group(2)
          bodytext = ""
          tag1 = ""
          alltags = []       # list of all tags in headline
          tagsrch = re.search('(.*?)\s*:(.*?):(.*?)$',heading)
          if tagsrch:
              heading = tagsrch.group(1)
              tag1 = tagsrch.group(2)
              alltags.append(tag1)
              tag2 = tagsrch.group(3)
              if tag2:
                 for t in tag2.split(':'):
                    if t != '': alltags.append(t)
       else:      # we are processing a non-heading line
           if line[:10] == '#+SEQ_TODO':
              kwlist = re.findall('([A-Z]+)\(', line)
              for kw in kwlist: todos[kw] = ""

           if line[:1] != '#':
               bodytext = bodytext + line
           elif line.startswith('#+'):
               bodytext = bodytext + line
               if line.startswith('#+begin_src'):
                  in_src_block = True
               if line.startswith('#+end_src'):
                  in_src_block = False

           if (in_src_block and (line[:1] == '#')) and not (line.startswith('#+begin_src') or line.startswith('#+end_src')):
               bodytext = bodytext + line


           if re.search(':PROPERTIES:', line): continue
           if re.search(':END:', line): continue
           prop_srch = re.search('^\s*:(.*?):\s*(.*?)\s*$', line)
           if prop_srch:
              propdict[prop_srch.group(1)] = prop_srch.group(2)
              continue
           sd_re = re.search('SCHEDULED:\s+<([0-9]+)\-([0-9]+)\-([0-9]+)', line)
           if sd_re:
              sched_date = datetime.date(int(sd_re.group(1)),
                                         int(sd_re.group(2)),
                                         int(sd_re.group(3)) )
           dd_re = re.search('DEADLINE:\s*<(\d+)\-(\d+)\-(\d+)', line)
           if dd_re:
              deadline_date = datetime.date(int(dd_re.group(1)),
                                            int(dd_re.group(2)),
                                            int(dd_re.group(3)) )
       if not found_first_heading:
          root += line

   # write out last node
   thisNode = Orgnode(level, heading, bodytext, tag1, alltags)
   thisNode.setProperties(propdict)
   if sched_date:
      thisNode.setScheduled(sched_date)
   if deadline_date:
      thisNode.setDeadline(deadline_date)
   nodelist.append( thisNode )

   # using the list of TODO keywords found in the file
   # process the headings searching for TODO keywords
   for n in nodelist:
       h = n.Heading()
       todoSrch = re.search('([A-Z]+)\s(.*?)$', h)
       if todoSrch:
           if todoSrch.group(1) in todos:
               n.setHeading( todoSrch.group(2) )
               n.setTodo ( todoSrch.group(1) )
       prtysrch = re.search('^\[\#(A|B|C)\] (.*?)$', n.Heading())
       if prtysrch:
          n.setPriority(prtysrch.group(1))
          n.setHeading(prtysrch.group(2))

   return root, nodelist

######################
class Orgnode(object):
    """
    Orgnode class represents a headline, tags and text associated
    with the headline.
    """
    def __init__(self, level, headline, body, tag, alltags):
        """
        Create an Orgnode object given the parameters of level (as the
        raw asterisks), headline text (including the TODO tag), and
        first tag. The makelist routine postprocesses the list to
        identify TODO tags and updates headline and todo fields.
        """
        self.level = len(level)
        self.headline = headline
        self.body = body
        self.tag = tag            # The first tag in the list
        self.tags = dict()        # All tags in the headline
        self.todo = ""
        self.prty = ""            # empty of A, B or C
        self.scheduled = ""       # Scheduled date
        self.deadline = ""        # Deadline date
        self.properties = dict()
        for t in alltags:
           self.tags[t] = ''

        # Look for priority in headline and transfer to prty field

    def Heading(self):
        """
        Return the Heading text of the node without the TODO tag
        """
        return self.headline

    def setHeading(self, newhdng):
        """
        Change the heading to the supplied string
        """
        self.headline = newhdng.lstrip(' ').rstrip(' ')  # remove preceding and trailing whitespace

    def Body(self):
        """
        Returns all lines of text of the body of this node except the
        Property Drawer
        """
        return self.body

    def Level(self):
        """
        Returns an integer corresponding to the level of the node.
        Top level (one asterisk) has a level of 1.
        """
        return self.level

    def Priority(self):
        """
        Returns the priority of this headline: 'A', 'B', 'C' or empty
        string if priority has not been set.
        """
        return self.prty

    def setPriority(self, newprty):
        """
        Change the value of the priority of this headline.
        Values values are '', 'A', 'B', 'C'
        """
        self.prty = newprty

    def Tag(self):
        """
        Returns the value of the first tag.
        For example, :HOME:COMPUTER: would return HOME
        """
        return self.tag

    def Tags(self):
        """
        Returns a list of all tags
        For example, :HOME:COMPUTER: would return ['HOME', 'COMPUTER']
        """
        return list(self.tags.keys())

    def hasTag(self, srch):
        """
        Returns True if the supplied tag is present in this headline
        For example, hasTag('COMPUTER') on headling containing
        :HOME:COMPUTER: would return True.
        """
        return srch in self.tags

    def setTag(self, newtag):
        """
        Change the value of the first tag to the supplied string
        """
        self.tag = newtag

    def setTags(self, taglist):
        """
        Store all the tags found in the headline. The first tag will
        also be stored as if the setTag method was called.
        """
        for t in taglist:
           self.tags[t] = ''

    def Todo(self):
        """
        Return the value of the TODO tag
        """
        return self.todo

    def setTodo(self, value):
        """
        Set the value of the TODO tag to the supplied string
        """
        self.todo = value.lstrip(' ').rstrip(' ')  # remove preceding and trailing whitespace

    def setProperties(self, dictval):
        """
        Sets all properties using the supplied dictionary of
        name/value pairs
        """
        self.properties = dictval

    def Property(self, keyval):
        """
        Returns the value of the requested property or null if the
        property does not exist.
        """
        return self.properties.get(keyval, "")

    def setScheduled(self, dateval):
        """
        Set the scheduled date using the supplied date object
        """
        self.scheduled = dateval
        dateval_str = dateval.strftime('%Y-%m-%d %a')
        if 'SCHEDULED: <' in self.body:
           idx_start = self.body.find('SCHEDULED: <')
           idx_end = idx_start + self.body[idx_start:].find('>')
           body_old = self.body
           body_new = body_old[:idx_start+12] + dateval_str + body_old[idx_end:]
           self.body = body_new
        else:
           self.body = 'SCHEDULED: <%s>\n' % dateval_str + self.body

    def Scheduled(self):
        """
        Return the scheduled date object or null if nonexistent
        """
        return self.scheduled

    def setDeadline(self, dateval):
        """
        Set the deadline (due) date using the supplied date object
        """
        self.deadline = dateval
        dateval_str = dateval.strftime('%Y-%m-%d %a')
        if 'DEADLINE: <' in self.body:
           idx_start = self.body.find('DEADLINE: <')
           idx_end = idx_start + self.body[idx_start:].find('>')
           body_old = self.body
           body_new = body_old[:idx_start+11] + dateval_str + body_old[idx_end:]
           self.body = body_new
        else:
           self.body = 'DEADLINE: <%s>\n' % dateval_str + self.body


    def Deadline(self):
        """
        Return the deadline date object or null if nonexistent
        """
        return self.deadline

    def __repr__(self):
        """
        Print the level, heading text and tag of a node and the body
        text as used to construct the node.
        """
        out = ''
        out += '*'*self.level + ' '
        if self.todo != '':
           out += self.todo + ' '
        if self.prty != '':
           out += '[#'  + self.prty + '] '
        out += self.headline
        if len(self.tags) > 0:
           out += ' :' + ':'.join(self.tags.keys()) + ':'
        out += '\n' + self.body
        return out
