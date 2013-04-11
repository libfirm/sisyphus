from distutils.core import setup
from sisyphus import VERSION

setup(name='sisyphus',
		description="regression test runner",
		version=VERSION,
		url="http://pp.info.uni-karlsruhe.de/git/sisyphus/",
		author="Andreas Zwinkau",
		author_email="zwinkau@kit.edu",
		packages=['sisyphus'],
		scripts=['sis'],
	  )
