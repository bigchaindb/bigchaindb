# Tips

## Tendermint Tips

* [Configure Tendermint to create no empty blocks](https://tendermint.com/docs/tendermint-core/using-tendermint.html#no-empty-blocks).
* Store the Tendermint data on a fast drive. You can do that by changing [the location of TMHOME](https://tendermint.com/docs/tendermint-core/using-tendermint.html#directory-root) to be on the fast drive.

## Refreshing Your Node

If you want to refresh your node back to a fresh empty state, then your best bet is to terminate it and deploy a new machine, but if that's not an option, then you can:

* drop the `bigchain` database in MongoDB using `bigchaindb drop` (but that only works if MongoDB is running)
* reset Tendermint using `tendermint unsafe_reset_all`
* delete the directory `$HOME/.tendermint`

## Shutting Down BigchainDB

If you want to stop/kill BigchainDB, you can do so by sending `SIGINT`, `SIGQUIT` or `SIGTERM` to the running BigchainDB
process(es). Depending on how you started BigchainDB i.e. foreground or background. e.g. you started BigchainDB in the background as mentioned above in the guide:

```bash
$ nohup bigchaindb start 2>&1 > bigchaindb.log &

$ # Check the PID of the main BigchainDB process
$ ps -ef | grep bigchaindb
<user>    *<pid> <ppid>   <C> <STIME> <tty>        <time> bigchaindb
<user>     <pid> <ppid>*  <C> <STIME> <tty>        <time> gunicorn: master [bigchaindb_gunicorn]
<user>     <pid> <ppid>*  <C> <STIME> <tty>        <time> bigchaindb_ws
<user>     <pid> <ppid>*  <C> <STIME> <tty>        <time> bigchaindb_ws_to_tendermint
<user>     <pid> <ppid>*  <C> <STIME> <tty>        <time> bigchaindb_exchange
<user>     <pid> <ppid>   <C> <STIME> <tty>        <time> gunicorn: worker [bigchaindb_gunicorn]
<user>     <pid> <ppid>   <C> <STIME> <tty>        <time> gunicorn: worker [bigchaindb_gunicorn]
<user>     <pid> <ppid>   <C> <STIME> <tty>        <time> gunicorn: worker [bigchaindb_gunicorn]
<user>     <pid> <ppid>   <C> <STIME> <tty>        <time> gunicorn: worker [bigchaindb_gunicorn]
<user>     <pid> <ppid>   <C> <STIME> <tty>        <time> gunicorn: worker [bigchaindb_gunicorn]
...

$ # Send any of the above mentioned signals to the parent/root process(marked with `*` for clarity)
# Sending SIGINT
$ kill -2 <bigchaindb_parent_pid>

$ # OR

# Sending SIGTERM
$ kill -15 <bigchaindb_parent_pid>

$ # OR

# Sending SIGQUIT
$ kill -3 <bigchaindb_parent_pid>

# If you want to kill all the processes by name yourself
$ pgrep bigchaindb | xargs kill -9
```

If you started BigchainDB in the foreground, a `Ctrl + C` or `Ctrl + Z` would shut down BigchainDB.

## Member: Dynamically Add or Remove Validators

One member can make a proposal to call an election to add a validator, remove a validator, or change the voting power of a validator. They then share the election/proposal ID with all the other members. Once more than 2/3 of the voting power votes yes, the proposed change comes into effect. The commands to create a new election/proposal, to approve an election/proposal, and to get the current status of an election/proposal can be found in the documentation about the [bigchaindb election](../server-reference/bigchaindb-cli#bigchaindb-election) subcommands.

## Logging and Log Rotation

See the page in the Appendices about [logging and log rotation](../appendices/log-rotation).