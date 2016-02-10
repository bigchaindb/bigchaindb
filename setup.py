"""
BigchainDB: A Scalable Blockchain Database

For full docs visit https://bigchaindb.readthedocs.org

"""
from setuptools import setup

setup(
    name='BigchainDB',
    version='0.0.0',
    description='BigchainDB: A Scalable Blockchain Database',
    long_description=__doc__,
    url='https://github.com/BigchainDB/bigchaindb/',
    author='BigchainDB Contributors',
    author_email='dev@bigchaindb.com',
    license='AGPLv3',
    zip_safe=False,

    classifiers=[
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: GNU Affero General Public License v3',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ],

    packages=['bigchaindb', 'bigchaindb.commands', 'bigchaindb.db'],

    entry_points={
        'console_scripts': [
            'bigchaindb=bigchaindb.commands.bigchain:main',
            'bigchaindb-benchmark=bigchaindb.commands.bigchain_benchmark:main'
        ],
    },
    install_requires=[
        'rethinkdb==2.2.0.post1',
        'pysha3==0.3',
        'pytz==2015.7',
        'tornado==4.3',
        'cryptography==1.2.1',
        'statsd==3.2.1',
        'python-rapidjson==0.0.6',
        'logstats==0.2.1',
        'base58==0.2.2',
        'bitcoin==1.1.42',
    ],
    setup_requires=['pytest-runner'],
    tests_require=['pytest'],
)
