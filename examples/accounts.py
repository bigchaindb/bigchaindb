

class User:
    def __init__(self, ledger):
        self.ledger = ledger
        self.private, self.public = ledger.generate_keys()
        self.assets = []

    def create_asset(self):
        tx = self.ledger.create_transaction(self.ledger.me, self.public, None, 'CREATE')
        tx_signed = self.ledger.sign_transaction(tx, self.ledger.me_private)
        self.ledger.validate_transaction(tx_signed)
        self.ledger.write_transaction(tx_signed)
        self.assets.append(tx_signed)

    def create_assets(self, amount=1):
        for i in range(amount):
            self.create_asset()


class Escrow(User):
    def __init__(self, ledger=None, current_owner=None, new_owner=None,
                 asset_id=None, condition_func=None, payload=None):
        User.__init__(self, ledger)
        self.condition_func = condition_func if condition_func else lambda proof: True
        self.new_owner = new_owner
        tx = self.ledger.create_transaction(current_owner,
                                            [current_owner, self.public],
                                            asset_id,
                                            'TRANSFER',
                                            payload)
        self.assets = tx

    def release(self, receipt=None):
        if not self.validate(receipt):
            raise Exception
        tx = self.ledger.create_transaction(self.assets['transaction']['new_owners'],
                                            self.new_owner,
                                            self.assets['id'],
                                            'TRANSFER',
                                            self.assets['transaction']['data']['payload'])
        return self.ledger.sign_transaction(tx, self.private, self.public)

    def validate(self, receipt):
        return self.condition_func(receipt)
