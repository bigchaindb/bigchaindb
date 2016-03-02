import json
from time import sleep

from bigchaindb import Bigchain
from examples.accounts import User
from examples.interledger.connector import Connector

config_bigchain = json.load(open('bigchain.json', 'r'))
config_megachain = json.load(open('megachain.json', 'r'))

bigchain = Bigchain(dbname=config_bigchain['database']['name'],
                    public_key=config_bigchain['keypair']['public'],
                    private_key=config_bigchain['keypair']['private'])

megachain = Bigchain(dbname=config_megachain['database']['name'],
                     public_key=config_megachain['keypair']['public'],
                     private_key=config_megachain['keypair']['private'])

alice = User(bigchain)
bob = User(megachain)

connector = Connector(bigchain)
connector.add_ledger(megachain)

# create assets
alice.create_assets(amount=2)
connector.create_assets(amount=2, ledger=bigchain)
connector.create_assets(amount=2, ledger=megachain)

sleep(6)
# transfer asset to escrow
tx_alice = connector.connect(user_from=alice.public,
                             ledger_from=alice.ledger,
                             user_to=bob.public,
                             ledger_to=bob.ledger,
                             condition_func=lambda proof: True,
                             asset_id=alice.assets[0]['id'],
                             payload={'what': 'ever'})

tx_alice_signed = alice.ledger.sign_transaction(tx_alice, alice.private)
alice.ledger.validate_transaction(tx_alice_signed)
alice.ledger.write_transaction(tx_alice_signed)

sleep(6)
# release asset from escrow
tx_bob = connector.release(ledger=bob.ledger, receipt=None)
tx_bob_signed = bob.ledger.sign_transaction(tx_bob, connector.private(bob.ledger), connector.public(bob.ledger))
bob.ledger.validate_transaction(tx_bob_signed)
bob.ledger.write_transaction(tx_bob_signed)

tx_connector = connector.release(ledger=alice.ledger, receipt=None)
tx_connector_signed = alice.ledger.sign_transaction(tx_connector, alice.private, alice.public)
alice.ledger.validate_transaction(tx_connector_signed)
alice.ledger.write_transaction(tx_connector_signed)
