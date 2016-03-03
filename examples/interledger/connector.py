from examples.accounts import User, Escrow


class LedgerConnection(User):
    def __init__(self, ledger):
        self._escrow = None
        User.__init__(self, ledger)

    def escrow(self, current_owner=None, new_owner=None, condition_func=None, asset_id=None, payload=None):
        self._escrow = Escrow(ledger=self.ledger,
                              current_owner=current_owner if current_owner else self.public,
                              new_owner=new_owner if new_owner else self.public,
                              asset_id=asset_id if asset_id else self.assets[0]['id'],
                              condition_func=condition_func,
                              payload=payload)
        if not current_owner:
            tx_connector_signed = self.ledger.sign_transaction(self._escrow.assets, self.private)
            self.ledger.validate_transaction(tx_connector_signed)
            self._escrow.assets = tx_connector_signed
            self.ledger.write_transaction(tx_connector_signed)

    def release(self, condition):
        return self._escrow.release(condition)


class Connector:
    def __init__(self, ledger=None):
        self.ledger_connections = []
        if ledger:
            self.add_ledger(ledger)

    def public(self, ledger=None):
        return self.get_ledger_connection(ledger).public if self.get_ledger_connection(ledger) else None

    def private(self, ledger=None):
        return self.get_ledger_connection(ledger).private if self.get_ledger_connection(ledger) else None

    def get_assets(self, ledger=None):
        ledger_connection = self.get_ledger_connection(ledger)
        return ledger_connection.assets if ledger_connection else None

    def create_assets(self, amount=1, ledger=None):
        ledger_connection = self.get_ledger_connection(ledger)
        if ledger_connection:
            ledger_connection.create_assets(amount)

    def get_ledger_connection(self, ledger=None):
        if not ledger:
            return self.ledger_connections[0]
        # TODO: yield
        ledger_connection = [l for l in self.ledger_connections if l.ledger == ledger]
        return ledger_connection[0] if ledger_connection else None

    def add_ledger(self, ledger):
        if self.can_add_ledger_connection(ledger):
            self.ledger_connections.append(LedgerConnection(ledger))

    def can_add_ledger_connection(self, ledger):
        return False if self.get_ledger_connection(ledger) else True

    def connect(self, user_from=None, ledger_from=None, user_to=None, ledger_to=None,
                condition_func=None, asset_id=None, payload=None):
        connection_from = self.get_ledger_connection(ledger_from)
        connection_to = self.get_ledger_connection(ledger_to)
        connection_from.escrow(current_owner=user_from,
                               condition_func=condition_func,
                               asset_id=asset_id,
                               payload=payload)
        connection_to.escrow(new_owner=user_to,
                             condition_func=condition_func,
                             payload=payload)
        return connection_from._escrow.assets

    def release(self, ledger=None, receipt=None):
        connection = self.get_ledger_connection(ledger)
        return connection.release(receipt)