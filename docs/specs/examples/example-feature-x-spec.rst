Example
=======

Feature X: Design specification document
----------------------------------------

Introduction paragraph - A simple explanation of what are we trying to accomplish with this feature.
Should be simple enough that even novice users/developers can understand. Ideally, this paragraph
should be made part of the feature PR(Pull Request).

  * If you want to provide a diagram with your specification document, please use
    ascii diagrams (plain text).
    
    * `asciiflow <http://asciiflow.com/>`_ is a good tool to get started.

  * **TODO:** We will add more guidelines on the formatting later.

.. note::

    If any of the sections mentioned in this example is not applicable to your feature.
    Please add **None** under that section, instead of removing the heading/section.

Problem Description
-------------------

A detailed description of the problem that we are trying to solve.

Use Cases
^^^^^^^^^

What use cases does this feature address? Impact on actors i.e. Developer, Consumer/User, Deployer etc.

Proposed Change
---------------

A detailed description of how you are proposing to solve the problem statement and the scope of this effort.

* You can also include the architecture diagram in this section.

    .. code:: text

        Sample architecture diagram

        +------------+                 +----------------------+
        |            |                 | +-----------+        |
        |            |                 | |Feature|X  |        |
        |            |                 | +-----------+        |
        |            |                 |                      |
        |            |                 |                      |
        |            |                 |                      |
        +------------+                 +----------------------+

        Old Architecture               New Architecture

  


Alternatives
^^^^^^^^^^^^

  * Are there any other ways in which you can address this problem statement? 
  * What are they?
  * Why aren't we using them?

Try to keep this short and precise, no need for a deep comparative analysis.

Data model impact
^^^^^^^^^^^^^^^^^

Will the feature modify the data model? If yes, how? Please cover all the details regarding the impact.

  * New data objects that will be introduced?
  * Existing database schema changes?
  * Database migrations? i.e. if there are existing deployments/instances, how will be modify/update
    them?

API impact
^^^^^^^^^^

Details about the impacted APIs and covering each API method.

Following details about each method should be covered:
  * Method Type(PUT/POST/GET/DELETE)
  * Expected response code(s)
  * Expected error response code(s)
  * URL
  * Parameters which can be passed via url.
  * Schema definition for body (JSON and if body data is allowed).
  * Schema definition for response (if any).
  * Accessibility of API(Does it introduce any policy? or policy changes?)
  * Example

Sample request/reponses:

Create Request:

    .. code:: text

      POST /api/v1/newfeature/
      {
        "newfeature": {
            "key-1": "value",
            "key-2": "value",
          }
      }

      Response:
      {
        "newfeature": {
            "key-1": "value",
            "key-2": "value",
            "key-2": "value",
        }
      }


Security impact
^^^^^^^^^^^^^^^

Does the feature have an impact on the existing system?

  * Does this feature touch sensitive information e.g. keys, user data?
  * Does this feature, introduce or alter an API in a way that sensitive information can be accessed?
  * Does this change required use of sudo? or root priviliges?
  * Crypto changes?


Performance impact
^^^^^^^^^^^^^^^^^^

Does this feature have an impact on the performance of the existing system?

Things to consider:

  * Changes in a commonly used utility function or decorator? Can cause performance degradation.
  * Database queries. 
  * Locking? Concurrency? Change in the existing behavior?

End user impact
^^^^^^^^^^^^^^^

Besides the API, does this change impact any of the drivers? How?

Deployment impact
^^^^^^^^^^^^^^^^^

Does this feature affect how we deploy BigchainDB/IPDB clusters? 

Things to consider:

  * Configuration changes?
  * New components introduced by the feature?
  * How to deploy?(working samples/documentation)
  * Will this impact CI, once this is merged? 

Documentation impact
^^^^^^^^^^^^^^^^^^^^

What is the impact of this feature on documentation? 

Testing impact
^^^^^^^^^^^^^^

Please, discuss the impact on existing testing framework and how this feature should be tested.

Things to consider:

  * Will this feature change existing behavior of tests?
  * Any specific scenarios that need to be tested?
  * Any limitations in the current test infrastructure to test this feature?

Implementation
--------------

Assignee(s)
^^^^^^^^^^^
Resource(s) working on this feature and there roles e.g.

Primary assignee(s):
  <github-profile OR Name>

Other contributor(s):
  <github-profile OR Name>

Action Items
^^^^^^^^^^^^

Action items or tasks - breaking the feature into sprints or smaller tickets if possible.
Add links to tickets if possible. Update the design specification if something pops up later
in the development cycle.

Targeted Release
^^^^^^^^^^^^^^^^

Targeted release version, if known. 

e.g. **3.0**

Dependencies
------------

  * If any project(s)/effort(s) depend on this change or related to.
  * If this feature depends on functionality from another change/feature.
  * Any library dependencies? Or versioning?

Reference(s)
------------

Please add useful reference(s) here.

  * URL of the GitHub issue containing the proposal/feature request.
  * Links to reference material.
  * Links to tickets/discussions.
  * Related specifications.
  * Anything that you feel is useful.

