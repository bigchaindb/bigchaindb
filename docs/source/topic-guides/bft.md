# BigchainDB and Byzantine Fault Tolerance

We have Byzantine fault tolerance (BFT) in our roadmap, as a switch that people can turn on. We anticipate that turning it on will cause a severe dropoff in performance (to gain a little extra security). See [Issue #293](https://github.com/bigchaindb/bigchaindb/issues/293).

Among the big, industry-used distributed databases in production today (e.g. DynamoDB, Bigtable, MongoDB, Cassandra, Elasticsearch), none of them are BFT. Indeed, almost all wide-area distributed systems in production are not BFT, including military, banking, healthcare, and other security-sensitive systems.

The are many more practical things that nodes can do to increase security (e.g. firewalls, key management, access controls).

From a [recent essay by Ken Birman](http://sigops.org/sosp/sosp15/history/05-birman.pdf) (of Cornell):

> Oh, and with respect to the BFT point: Jim [Gray] felt that real systems fail by crashing [54]. Others have since done studies reinforcing this view, or finding that even crash-failure solutions can sometimes defend against application corruption. One interesting study, reported during a SOSP WIPS session by Ben Reed (one of the co-developers of Zookeeper), found that at Yahoo, Zookeeper itself had never experienced Byzantine faults in a one-year period that they studied closely.

> [54] Jim Gray. Why Do Computers Stop and What Can Be Done About It? SOSP, 1985.

Ben Reed never published those results, but Birman wrote more about them in the book *Guide to Reliable Distributed Systems: Building High-Assurance Applications*. From page 358 of that book:

> But the cloud community, led by Ben Reed and Flavio Junqueira at Yahoo, sees things differently (these are the two inventor’s [sic] of Yahoo’s ZooKeeper service). **They have described informal studies of how applications and machines at Yahoo failed, concluding that the frequency of Byzantine failures was extremely small relative to the frequency of crash failures** [emphasis added]. Sometimes they did see data corruption, but then they often saw it occur in a correlated way that impacted many replicas all at once. And very often they saw failures occur in the client layer, then propagate into the service. BFT techniques tend to be used only within a service, not in the client layer that talks to that service, hence offer no protection against malfunctioning clients. **All of this, Reed and Junqueira conclude, lead to the realization that BFT just does not match the real needs of a cloud computing company like Yahoo, even if the data being managed by a service really is of very high importance** [emphasis added]. Unfortunately, they have not published this study; it was reported at an “outrageous opinions” session at the ACM Symposium on Operating Systems Principles, in 2009.

> The practical use of the Byzantine protocol raises another concern: The timing assumptions built into the model [i.e. synchronous or partially-synchronous nodes] are not realizable in most computing environments…
