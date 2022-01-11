# Orgnode

Orgnode is a simple Python package for reading Org-mode files, originally created by [Charles Cave](http://members.optusnet.com.au/~charles57/GTD/orgnode.html).

Modifications to original script:
- Parsed main `orgnode.py` to Python 3
- Simple installation via pip, see below
- Several updates to Org-mode file parsing (see commits)
- Modified interface for `makelist` method:
  - Before: `nodelist = Orgnode.makelist(filename)`
  - Now: `root, nodelist = Orgnode.makelist(filename)` where `root` is a string containing everything before the first node

# Install

1. `$ git clone git@github.com:cmower/Orgnode.git`
1. `$ cd Orgnode`
1. `$ pip install .`
