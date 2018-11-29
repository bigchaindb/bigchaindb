
.. Copyright BigchainDB GmbH and BigchainDB contributors
   SPDX-License-Identifier: (Apache-2.0 AND CC-BY-4.0)
   Code is Apache-2.0 and docs are CC-BY-4.0

BigchainDB Documentation
========================

Meet BigchainDB. The blockchain database.

It has some database characteristics and some blockchain characteristics,
including `decentralization <decentralized.html>`_, 
`immutability <immutable.html>`_ 
and `native support for assets <assets.html>`_.

At a high level, one can communicate with a BigchainDB network (set of nodes) using the BigchainDB HTTP API, or a wrapper for that API, such as the BigchainDB Python Driver. Each BigchainDB node runs BigchainDB Server and various other software. The `terminology page <terminology.html>`_ explains some of those terms in more detail.

.. raw:: html

   <style media="screen" type="text/css">
   .button {
     border-top: 1px solid #96d1f8;
     background: #65a9d7;
     background: -webkit-gradient(linear, left top, left bottom, from(#3e779d), to(#65a9d7));
     background: -webkit-linear-gradient(top, #3e779d, #65a9d7);
     background: -moz-linear-gradient(top, #3e779d, #65a9d7);
     background: -ms-linear-gradient(top, #3e779d, #65a9d7);
     background: -o-linear-gradient(top, #3e779d, #65a9d7);
     padding: 8.5px 17px;
     -webkit-border-radius: 3px;
     -moz-border-radius: 3px;
     border-radius: 3px;
     -webkit-box-shadow: rgba(0,0,0,1) 0 1px 0;
     -moz-box-shadow: rgba(0,0,0,1) 0 1px 0;
     box-shadow: rgba(0,0,0,1) 0 1px 0;
     text-shadow: rgba(0,0,0,.4) 0 1px 0;
     color: white;
     font-size: 16px;
     font-family: Arial, Sans-Serif;
     text-decoration: none;
     vertical-align: middle;
   }
   .button:hover {
     border-top-color: #28597a;
     background: #28597a;
     color: #ccc;
   }
   .button:active {
     border-top-color: #1b435e;
     background: #1b435e;
   }
   a.button:visited {
     color: white
   }
   .buttondiv {
     margin-bottom: 1.5em;
   }
   </style>

   <div class="buttondiv">
     <a class="button" href="http://bigchaindb.com/http-api">HTTP API Docs</a>
   </div>
   <div class="buttondiv">
     <a class="button" href="http://docs.bigchaindb.com/projects/contributing/en/latest/index.html">Contributing to BigchainDB</a>
   </div>
   <div class="buttondiv">
     <a class="button" href="http://docs.bigchaindb.com/projects/py-driver/en/latest/index.html">Python Driver Docs</a>
   </div>
   <div class="buttondiv">
     <a class="button" href="https://docs.bigchaindb.com/projects/js-driver/en/latest/index.html">JavaScript Driver Docs</a>
   </div>
   <div class="buttondiv">
     <a class="button" href="http://docs.bigchaindb.com/projects/server/en/latest/index.html">Server Docs</a>
   </div>
   <div class="buttondiv">
     <a class="button" href="http://docs.bigchaindb.com/projects/server/en/latest/quickstart.html">Server Quickstart</a>
   </div>


More About BigchainDB
---------------------

.. toctree::
   :maxdepth: 1

   BigchainDB Docs Home <self>
   production-ready
   terminology
   decentralized
   diversity
   immutable
   bft
   query
   assets
   smart-contracts
   transaction-concepts
   store-files
   permissions
   private-data
   Data Models <https://docs.bigchaindb.com/projects/server/en/latest/data-models/index.html>
   korean/index
