"""
BigchainDB: A Scalable Blockchain Database

For full docs visit https://docs.bigchaindb.com

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

dev_require = [
    'ipdb',
    'ipython',
    'watchdog',
    'logging_tree',
]

docs_require = [
    'Sphinx>=1.4.8',
    'recommonmark>=0.4.0',
    'sphinx-rtd-theme>=0.1.9',
    'sphinxcontrib-httpdomain>=1.5.0',
    'sphinxcontrib-napoleon>=0.4.4',
]

tests_require = [
    'coverage',
    'pep8',
    'flake8',
    'flake8-quotes==0.8.1',
    'hypothesis~=3.18.5',
    'hypothesis-regex',
    'pylint',
    'pytest>=3.0.0',
    'pytest-catchlog>=1.2.2',
    'pytest-cov>=2.2.1',
    'pytest-mock',
    'pytest-xdist',
    'pytest-flask',
    'pytest-aiohttp',
    'tox',
] + docs_require

benchmarks_require = [
    'line-profiler==1.0',
]

install_requires = [
    # TODO Consider not installing the db drivers, or putting them in extras.
    'rethinkdb~=2.3',  # i.e. a version between 2.3 and 3.0
    'pymongo~=3.4',
    'pysha3~=1.0.2',
    'cryptoconditions~=0.6.0.dev',
    'python-rapidjson==0.0.11',
    'logstats~=0.2.1',
    'flask>=0.10.1',
    'flask-cors~=3.0.0',
    'flask-restful~=0.3.0',
    'requests~=2.9',
    'gunicorn~=19.0',
    'multipipes~=0.1.0',
    'jsonschema~=2.5.1',
    'pyyaml~=3.12',
    'aiohttp~=2.0',
    'python-rapidjson-schema==0.1.1',
    'statsd==3.2.1',
]

setup(
    name='BigchainDB',
    version=version['__version__'],
    description='BigchainDB: A Scalable Blockchain Database',
    long_description=(
        "BigchainDB allows developers and enterprises to deploy blockchain "
        "proof-of-concepts, platforms and applications with a scalable blockchain "
        "database. BigchainDB supports a wide range of industries and use cases "
        "from identity and intellectual property to supply chains, energy, IoT "
        "and financial ecosystems. With high throughput, sub-second latency and "
        "powerful functionality to automate business processes, BigchainDB looks, "
        "acts and feels like a database but has the core blockchain "
        "characteristics that enterprises want."
        ),
    url='https://github.com/BigchainDB/bigchaindb/',
    author='BigchainDB Contributors',
    author_email='dev@bigchaindb.com',
    license='AGPLv3',
    zip_safe=False,

    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Topic :: Database',
        'Topic :: Database :: Database Engines/Servers',
        'Topic :: Software Development',
        'Natural Language :: English',
        'License :: OSI Approved :: GNU Affero General Public License v3',
        'Programming Language :: Python :: 3 :: Only',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Operating System :: MacOS :: MacOS X',
        'Operating System :: POSIX :: Linux',
    ],

    packages=find_packages(exclude=['tests*']),

    entry_points={
        'console_scripts': [
            'bigchaindb=bigchaindb.commands.bigchaindb:main'
        ],
    },
    install_requires=install_requires,
    setup_requires=['pytest-runner'],
    tests_require=tests_require,
    extras_require={
        'test': tests_require,
        'dev': dev_require + tests_require + docs_require + benchmarks_require,
        'docs': docs_require,
    },
    package_data={'bigchaindb.common.schema': ['*.yaml']},
)
