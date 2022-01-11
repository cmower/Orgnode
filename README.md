# Orgnode

Orgnode is a simple Python package for reading Org-mode files, originally created by [Charles Cave](http://members.optusnet.com.au/~charles57/GTD/orgnode.html).

Load an Org-mode file using
```python
root, nodelist = Orgnode.makelist(filename)
```
where
- `root` is a string containing everything up until the first node
- `nodelist` is a list of `Orgnode` objects, see [Module documentation](http://members.optusnet.com.au/~charles57/GTD/orgnode.html)
- `filename` is the filename for the Org-mode file you want to load


# Install

1. `$ git clone git@github.com:cmower/Orgnode.git`
1. `$ cd Orgnode`
1. `$ pip install .`
