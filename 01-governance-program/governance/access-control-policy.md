# Access Control Policy: moved to Confluence

This file used to hold a repo draft (v0.1, 2026-11-24) of the warehouse access policy. It has been
replaced by the approved **POL-02 Access Control Policy** in Confluence, which is the only copy of the
policy text (STD-01 v2.0, single-source rule; GOV-78):

**[POL-02 Access Control Policy](https://empire-city-taxi.atlassian.net/wiki/spaces/ECTG/pages/557061)**,
with the access matrix in its Appendix A.

What stays in the repository is data the pipeline reads, not policy text:

- [`data-platform/dbt/seeds/governance/access_policy.csv`](../../data-platform/dbt/seeds/governance/access_policy.csv):
  the machine-readable access matrix. The generator issues grants from it, and the ACC checks test
  grants against it.
- [`data-platform/dbt/seeds/governance/role_service_accounts.csv`](../../data-platform/dbt/seeds/governance/role_service_accounts.csv):
  the role accounts used by the daily access check.

The earlier draft is in the git history (`git log -- 01-governance-program/governance/access-control-policy.md`).
