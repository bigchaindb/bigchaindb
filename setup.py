"""
BigchainDB: A Scalable Blockchain Database

For full docs visit https://bigchaindb.readthedocs.org

"""
from setuptools import setup, find_packages

tests_require = [
    'pytest',
    'coverage',
    'pep8',
    'pyflakes',
    'pylint',
    'pytest',
    'pytest-cov',
    'pytest-xdist',
    'pytest-flask',
]

dev_require = [
    'ipdb',
    'ipython',
]

docs_require = [
    'recommonmark>=0.4.0',
    'Sphinx>=1.3.5',
    'sphinxcontrib-napoleon>=0.4.4',
    'sphinx-rtd-theme>=0.1.9',
]

setup(
    name='BigchainDB',
    version='0.1.4',
    description='BigchainDB: A Scalable Blockchain Database',
    long_description=__doc__,
    url='https://github.com/BigchainDB/bigchaindb/',
    author='BigchainDB Contributors',
    author_email='dev@bigchaindb.com',
    license='AGPLv3',
    zip_safe=False,

    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Topic :: Database',
        'Topic :: Database :: Database Engines/Servers',
        'Topic :: Software Development',
        'Natural Language :: English',
        'License :: OSI Approved :: GNU Affero General Public License v3',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Operating System :: MacOS :: MacOS X',
        'Operating System :: POSIX :: Linux',
    ],

    packages=find_packages(exclude=['tests*']),

    entry_points={
        'console_scripts': [
            'bigchaindb=bigchaindb.commands.bigchain:main',
            'bigchaindb-benchmark=bigchaindb.commands.bigchain_benchmark:main'
        ],
        'bigchaindb.consensus': [
            'default=bigchaindb.consensus:BaseConsensusRules'
        ]
    },
    install_requires=[
        'rethinkdb==2.2.0.post4',
        'pysha3==0.3',
        'pytz==2015.7',
        'cryptography==1.2.3',
        'statsd==3.2.1',
        'python-rapidjson==0.0.6',
        'logstats==0.2.1',
        'base58==0.2.2',
        'bitcoin==1.1.42',
        'flask==0.10.1',
        'requests==2.9',
    ],
    setup_requires=['pytest-runner'],
    tests_require=tests_require,
    extras_require={
        'test': tests_require,
        'dev':  dev_require + tests_require + docs_require,
        'docs':  docs_require,
    },
)
