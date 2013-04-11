from distutils.core import setup
from sisyphus import VERSION

setup(name='sisyphus',
		description="regression test runner",
		version=VERSION,
		url="http://pp.info.uni-karlsruhe.de/git/sisyphus/",
		author="Andreas Zwinkau",
		author_email="zwinkau@kit.edu",
		packages=[
                    'sisyphus',
                    'sisyphus.test',
                    'sisyphus.util',
                    'sisyphus.util.concurrent',
                    'sisyphus.util.concurrent.futures',
                ],
		scripts=['sis'],
		classifiers=[
		'Development Status :: 4 - Beta',
		'Environment :: Console',
		'Intended Audience :: Developers',
		'Operating System :: Unix',
		'Programming Language :: Python',
		'Topic :: Software Development :: Testing',
		],
		platforms=['any'],
	  )
