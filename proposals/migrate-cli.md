# Migrate Bigchaindb cli for Tendermint

## Problem Description
With Tendermint integration some of the cli sub-commands have been rendered obsolete. It would be only appropriate to white list sub-commands depending on the backend.

### Use cases
- Avoid confusing the user by not displaying irrelevant sub-commands.


## Proposed Change
Following sub-commands should be updated

- `bigchaindb --help`: list the relevant sub-commands depending on the configured backend. In case the backend is not configured then the default backend `mongodb` should be assumed.

Following sub-commands should be depreciated for `localmongodb` backend.

- `bigchaindb export-my-pubkey`
- `bigchaindb set-shards`
- `bigchaindb set-replicas`

**NOTE**: In case the user attempts to execute the above depreciated sub-commands an error message stating their in-compatibility with `localmongodb` should be displayed.

### Usage example
N/A

### Data model impact
N/A

### API impact
N/A

### Security impact
N/A

### Performance impact
N/A

### End user impact
N/A

### Deployment impact
N/A

### Documentation impact
The documentation for depreciated sub-commands should indicate that they are not compatible with `localmongodb` backend.


### Testing impact
Following test cases should be added
- Set `localmongodb` as backend, then executing the depreciated sub-commands should give an error.
- Set `localmongodb` as backend, then executing `bigchaindb --help`, `bigchaindb -h` should not list the deprecated sub-commands.


## Implementation

### Assignee(s)
Primary assignee(s): @kansi

### Targeted Release
BigchainDB 2.0


## Dependencies
N/A


## Reference(s)
* [Bigchaindb CLI](https://docs.bigchaindb.com/projects/server/en/latest/server-reference/bigchaindb-cli.html)
