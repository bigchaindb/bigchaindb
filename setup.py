"""
BigchainDB: A Scalable Blockchain Database

For full docs visit https://bigchaindb.readthedocs.org

"""
from setuptools import setup, find_packages


# get the version
version = {}
with open('bigchaindb/version.py') as fp:
    exec(fp.read(), version)


# check if setuptools is up to date
def check_setuptools_features():
    import pkg_resources
    try:
        list(pkg_resources.parse_requirements('foo~=1.0'))
    except ValueError:
        exit('Your Python distribution comes with an incompatible version '
             'of `setuptools`. Please run:\n'
             ' $ pip3 install --upgrade setuptools\n'
             'and then run this command again')


check_setuptools_features()


tests_require = [
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

benchmarks_require = [
    'line-profiler==1.0',
]

setup(
    name='BigchainDB',
    version=version['__version__'],
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
            'bigchaindb=bigchaindb.commands.bigchain:main'
        ],
        'bigchaindb.consensus': [
            'default=bigchaindb.consensus:BaseConsensusRules'
        ]
    },
    install_requires=[
        'rethinkdb~=2.3',
        'pysha3==0.3',
        'pytz==2015.7',
        'cryptoconditions==0.4.1',
        'statsd==3.2.1',
        'python-rapidjson==0.0.6',
        'logstats==0.2.1',
        'base58==0.2.2',
        'flask==0.10.1',
        'requests==2.9',
        'gunicorn~=19.0',
    ],
    setup_requires=['pytest-runner'],
    tests_require=tests_require,
    extras_require={
        'test': tests_require,
        'dev': dev_require + tests_require + docs_require + benchmarks_require,
        'docs': docs_require,
    },
)
