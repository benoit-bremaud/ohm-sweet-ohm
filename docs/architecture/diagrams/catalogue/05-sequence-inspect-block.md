# Sequence diagram — catalogue — inspect a block (UC3)

> **Feature**: issue #17 — public read API (milestone M1)
> **Use case**: UC3 Inspect a block, [01-use-case.md](01-use-case.md)
> **Source specs**: [04-class.md](04-class.md),
> [02-sequence-publish-blocks.md](02-sequence-publish-blocks.md)
> **Related ADRs**: [ADR-0001 in-memory search](../../decisions/0001-in-memory-search.md)
> **Decisions captured**: catalogue kept in memory and its version checked at most every 5 s;
> the cached catalogue keeps being served when the database is unreachable; lowercase values and
> SI units with their symbol in the API; schematics read one at a time, never kept in memory

## Context

How a client (the web page, or any API user) reads a block and its schematic. The catalogue is
loaded once into memory and only reloaded after an import changed it.

## Diagram

```mermaid
sequenceDiagram
  actor Client
  participant API as API (apps/api)
  participant Cache as CatalogueCache
  participant Repo as BlockRepository (packages/db)
  participant DB as PostgreSQL

  Client->>API: GET /blocks/{slug}
  API->>Cache: get()
  alt checked less than 5 s ago
    Cache-->>API: catalogue in memory
  else check due
    Cache->>Repo: catalogueVersion()
    Repo->>DB: hash of every block's content hash
    alt database unreachable
      Cache-->>API: catalogue in memory, failure logged (first load: error)
    else version changed, or first load
      Cache->>Repo: loadCatalogue(BASE_CIRCUITS)
      Repo->>DB: one repeatable-read snapshot
      Cache-->>API: new catalogue
    else unchanged
      Cache-->>API: catalogue in memory
    end
  end
  API->>API: findBlock(slug)
  alt unknown block
    API-->>Client: 404 { error }
  else found
    API-->>Client: 200 block (lowercase values, SI units, path, formulas, schematicUrl)
  end

  Client->>API: GET /blocks/{slug}/schematic.svg (If-None-Match)
  API->>Repo: findSchematic(slug)
  Repo->>DB: SVG and block content hash
  alt ETag matches
    API-->>Client: 304
  else
    API-->>Client: 200 SVG, sandboxed CSP, nosniff, ETag
  end
```

## Notes

- **Freshness**: an import is visible within 5 seconds; the version check costs under a
  millisecond, a full reload about 2 ms for 25 blocks and 16 ms for 1,000 (measured).
- **Outage**: a failed check or reload is logged and the catalogue in memory keeps being served;
  a dropped database connection never crashes the process. Only the very first load can fail.
- **SVG safety**: schematics are served as images that cannot run code, whatever a contributed
  file contains (`Content-Security-Policy: sandbox`, no script, `nosniff`).
- **Errors**: every error answers `{ error }`; server errors never expose their cause.
