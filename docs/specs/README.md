# Guidelines for Feature Request(s)

This document covers, how to contribute new feature(s) or significant design changes to BigchainDB. Since, contribution
of such functionality involves design discussion and might take multiple releases to complete,
we expect the contributors to follow certain guidelines before proceeding with the implementation.


## Classification
How to classify your contribution as a feature and determine if it needs design discussion. 

Here are some baseline criterion that can help you classify your idea, as a feature:

- Requires significant effort/changes to the current BigchainDB implementation and it is not self
 contained (e.g. API changes,  introducing a new component, takes more than 20 Wrigleys
 (Wrigley is a `dev day` @ BigchainDB))
- Impacts the clients and drivers.
- Can we write a blog post about it?
- Requires collaboration with multiple teams in terms of development, operations and testing.
- Impacts documentation significantly.

It is not a feature if:

- It is straightforward enough and might not need a design discussion.
  - Test case fixes
  - Fixing typos/grammar in documentation.
  - Refactoring code

## Classified as a Feature?
Create a new issue on our [GitHub repository](https://github.com/bigchaindb/bigchaindb/issues/new) with a
`Feature-Request` label, once you have classified your proposal as a feature and:

- Scratched the surface.
  - Discussed the proposal in the community e.g. on [our Gitter channel](https://gitter.im/bigchaindb/bigchaindb),
  Or [Twitter](https://twitter.com/BigchainDB) and saw interest.
- *Optional:* Have a working prototype.
- Worked out the resources and people, who can contribute towards this feature.

## Submit Spec
Submit a design specification document (Pull Request) of your feature. The spec needs to be submitted at:

```text
/path/to/repo/bigchaindb/docs/specs/features/release-<latest-release>/
``` 

The PR for the specification document should be
[linked](https://help.github.com/articles/autolinked-references-and-urls/) to the GitHub issue you created and
marked with `Spec` label.

**Note:** Feature(s) cannot be backported. Hence, only commit your proposal to the latest release.

[How do I write a design specification document?](examples/example-feature-x-spec.rst)

## Almost there
Once, you have submitted the design specification document:

- Get it reviewed.
- Discuss.
- Address comments(if any).
- Get it merged.

Once, your specification document is merged, it will be tracked for an upcoming release.

