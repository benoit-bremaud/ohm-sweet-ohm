# ADR-0001 — Search by need runs in memory in the domain

- Status: accepted
- Date: 2026-10-09
- Deciders: Benoît Bremaud
- Related: [04-class.md](../diagrams/catalogue/04-class.md), UC4 in [01-use-case.md](../diagrams/catalogue/01-use-case.md)

## Context and problem statement

UC4 matches search criteria against typed specs with two match modes (`covers`, `within`) and
enumerations. The framing chose PostgreSQL partly for its range types, which could run these
comparisons in SQL. Running them both in SQL and in the domain classes would define the match
rules twice. Where should matching run in v1?

## Considered options

1. In memory: load the catalogue, let `SearchCriteria` and `Spec` match each block.
2. In SQL: translate criteria into range-type queries.
3. Both: SQL pre-filter, domain final check.

## Decision outcome

Chosen option: **1. in memory**, because the v1 catalogue holds about 25 blocks, and a single
implementation of the match rules, unit-tested without a database, is the simplest correct
design.

### Consequences

- Good: one source of truth for match semantics; fast, isolated unit tests; no SQL to keep in
  sync with the domain.
- Good: PostgreSQL stays a plain store; range types are no longer a requirement.
- Bad: every search reads the whole catalogue. Acceptable up to a few thousand blocks; the
  catalogue can be cached in the API process since it changes only on publication.

### Revisit when

The catalogue grows beyond a few thousand blocks, or search latency becomes noticeable. Option 3
then keeps the domain as the final authority.
