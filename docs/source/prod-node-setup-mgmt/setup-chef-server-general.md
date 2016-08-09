# Set Up Chef Server (General)

Chef Software, Inc., the company behind Chef, offers managed hosting of Chef Server ("Hosted Chef"), but we advise against using that. A BigchainDB cluster is supposed to be decentralized, and it wouldn't be very decentralized if all the nodes used Hosted Chef.

Below are some ways to set up Chef Server, starting with the easiest.

* If you intend to host your node on AWS, then see [the page about setting up Chef Server on AWS](setup-chef-server-aws.html).

* If your hosting provider has a marketplace of images/snapshots (akin to AWS Marketplace), then search for "Chef" there.

* Do a web search for "Chef Server \<name of your hosting provider\>" and see what comes up.

* Bootstrap the installation of Chef Server using Chef-Solo and the chef-server cookbook. The instructions are in the "Install Methods" section of [the chef-server cookbook page in Chef Supermarket](https://supermarket.chef.io/cookbooks/chef-server).

* Follow the official Chef tutorial: [Install and configure Chef server using your hardware or cloud provider](https://learn.chef.io/install-and-manage-your-own-chef-server/linux/install-chef-server/install-chef-server-using-your-hardware/).


When done, make sure your installation of Chef Server is consistent with the official Chef documentation titled [Install Chef Server](https://docs.chef.io/install_server.html).
