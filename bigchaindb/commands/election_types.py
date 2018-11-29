elections = {
    'upsert-validator': {
        'help': 'Propose a change to the validator set',
        'args': {
            'public_key': {
                'help': 'Public key of the validator to be added/updated/removed.'
            },
            'power': {
                'type': int,
                'help': 'The proposed power for the validator. Setting to 0 will remove the validator.'},
            'node_id': {
                'help': 'The node_id of the validator.'
            },
            '--private-key': {
                'dest': 'sk',
                'required': True,
                'help': 'Path to the private key of the election initiator.'
            }
        }
    },
    'chain-migration': {
        'help': 'Call for a halt to block production to allow for a version change across breaking changes.',
        'args': {
            '--private-key': {
                'dest': 'sk',
                'required': True,
                'help': 'Path to the private key of the election initiator.'
            }
        }
    }
}
