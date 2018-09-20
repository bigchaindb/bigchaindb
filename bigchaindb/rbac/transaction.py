# Copyright BigchainDB GmbH and BigchainDB contributors
# SPDX-License-Identifier: (Apache-2.0 AND CC-BY-4.0)
# Code is Apache-2.0 and docs are CC-BY-4.0

import logging

from bigchaindb.common.exceptions import (ValidationError)
from bigchaindb.models import Transaction

ASSET_RULE_LINK = 'link'
METADATA_RULE_CAN_LINK = 'can_link'

logger = logging.getLogger(__name__)

class LinkedTransaction(Transaction):

    def validate(self, bigchain, current_transactions=[]):
        super().validate(bigchain, current_transactions)
        self.validate_link(bigchain)
        return self

    def validate_link(self, bigchain):
        transaction = self
        logger.info('Validating link')
        public_key = transaction.inputs[0].owners_before[0]

        # Don't do anything when it's GENESIS or TRANSFER transaction
        if transaction.operation == 'GENESIS' or\
                transaction.operation == 'TRANSFER':
            return

        # Don't do anything when there is no asset.data
        if not hasattr(transaction.asset, 'data'):
            return

        # If link is not being used, don't do anything
        if transaction.asset['data'] and ASSET_RULE_LINK not in transaction.asset['data']:
            return

        link = transaction.asset['data']['link']
        logger.info('Link: %s', link)
        tx_to_link = bigchain.get_transaction(link)

        if not tx_to_link:
            raise ValidationError('Transaction not resolved to link: {}'
                                  .format(link))

        logger.info('Link Transaction: %s', tx_to_link.id)

        if tx_to_link and not hasattr(tx_to_link, 'metadata'):
            raise ValidationError('Metadata not found in transaction {}'
                                  .format(tx_to_link))

        if tx_to_link.metadata is None or METADATA_RULE_CAN_LINK not in tx_to_link.metadata:
            raise ValidationError('can_link not found in metadata of transaction {}'
                                  .format(tx_to_link))

        can_link = tx_to_link.metadata[METADATA_RULE_CAN_LINK]
        logger.info('Can link: %s', can_link)

        # can_link validation
        # if can_link is a list
        # check if can_link is a list of transaction ids or public keys
        # check if the public key of the user is a part of it or not
        # OR
        # check if the user has a premission asset linked to the can_link asset
        if isinstance(can_link, list):
            logger.info('can_link is a list')
            if self.check_if_transaction_id(bigchain, can_link[0]):
                self.validate_can_link(bigchain, can_link, public_key)
            else:
                if public_key in can_link:
                    logger.info('Link valid: public key in can_link')
                    return
                else:
                    raise ValidationError('Linking is not authorized for: {}'.format(
                        public_key))
        # backward compatibility - if can_link is string then convert it to a list
        elif isinstance(can_link, str):
            logger.info('can_link is a string')
            can_link_list = [can_link]
            self.validate_can_link(bigchain, can_link_list, public_key)
        else:
            raise ValidationError('can_link is not valid')
        return

    def validate_can_link(self, bigchain, can_link, public_key):
        logger.info('validating can_link, looking up assets in owner wallet')
        wallet_tx = bigchain.get_owned_ids(public_key)
        wallet_tx_ids = [tx.txid for tx in wallet_tx]
        logger.info('Wallet has %s assets', len(wallet_tx_ids))

        for asset_id in wallet_tx_ids:
            logger.info('Looking up asset: %s', asset_id)
            trans = bigchain.get_transaction(asset_id)
            if trans.operation == Transaction.TRANSFER:
                permission_asset = bigchain.get_transaction(
                    trans.asset['id']).asset
            else:
                permission_asset = trans.asset
            if permission_asset and permission_asset['data'] and\
                    ASSET_RULE_LINK in permission_asset['data']:
                if permission_asset['data']['link'] in can_link:
                    logger.info('Link valid: asset.link found in can_link')
                    break
            else:
                continue
        else:
            raise ValidationError('Linking is not authorized for: {}'.format(
                public_key))
        return

    def check_if_transaction_id(self, bigchain, transaction_id):
        logger.info('Checking if tx id: {}'.format(transaction_id))
        is_tx_id = True
        try:
            tx = bigchain.get_transaction(transaction_id)
            if tx:
                logger.info(
                    'Tx id check passed for: {}'.format(transaction_id))
            else:
                logger.info(
                    'Tx id check failed for: {}'.format(transaction_id))
                is_tx_id = False
        except:
            logger.info('Tx id check failed for: {}'.format(transaction_id))
            is_tx_id = False
        return is_tx_id
