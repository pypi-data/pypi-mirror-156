# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['sequal']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'sequal',
    'version': '1.0.1',
    'description': 'A Python package for working with protein sequence and PTM',
    'long_description': '# SEQUAL / seq=\n\nSequal is developed as a python package for in-silico generation of modified sequences from a sequence input and modifications.\n\n## Dependencies\n\n`None.`\n\n## Usage\nSequence comprehension\n```python\nfrom sequal.sequence import Sequence\n#Using Sequence object with unmodified protein sequence\n\nseq = Sequence("TESTEST")\nprint(seq.seq) #should print "TESTEST"\nprint(seq[0:2]) #should print "TE"\n```\n\n```python\nfrom sequal.sequence import Sequence\n#Using Sequence object with modified protein sequence. []{}() could all be used as modification annotation. \n\nseq = Sequence("TEN[HexNAc]ST")\nfor i in seq.seq:\n    print(i, i.mods) #should print N [HexNAc] on the 3rd amino acid\n\nseq = Sequence("TEN[HexNAc][HexNAc]ST")\nfor i in seq.seq:\n    print(i, i.mods) #should print N [HexNAc, HexNAc] on the 3rd amino acid   \n\n# .mods property provides an access to all amino acids at this amino acid\n\nseq = Sequence("TE[HexNAc]NST", mod_position="left") #mod_position left indicate that the modification should be on the left of the amino acid instead of default which is right\nfor i in seq.seq:\n    print(i, i.mods) #should print N [HexNAc] on the 3rd amino acid\n```\n\n```python\nfrom sequal.sequence import Sequence\n#Format sequence with custom annotation\nseq = Sequence("TENST")\na = {1:"tes", 2:["1", "200"]}\nprint(seq.to_string_customize(a, individual_annotation_enclose=False, individual_annotation_separator="."))\n# By supplying .to_string_customize with a dictionary of position on the sequence that you wish to annotate\n# The above would print out TE[tes]N[1.200]ST\n```',
    'author': 'Toan K. Phung',
    'author_email': 'toan.phungkhoiquoctoan@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
