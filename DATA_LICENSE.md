# Source data and rights

The MIT license covers original project code and original explanatory content. It does not grant rights to third-party issuer filings, earnings releases, logos or other source documents.

The repository includes selected numerical factual observations, field definitions, calculations and source citations. Full issuer documents and logos are not redistributed. Public access on SEC or issuer websites is not treated as a blanket open-content license. Users are responsible for any additional redistribution and for source access terms.

`data/source_manifest.csv` records retrieval timestamps and available SHA-256 hashes of the downloaded SEC HTML used during preparation. Hashes identify the retrieved bytes; a later download can differ due to delivery changes. The issuer release was read through web retrieval and has no byte-level snapshot hash. Its provenance is recorded explicitly.

No licensed price feed, analyst estimate, invented API response or scraped personal data is included. Hypothetical assumptions are in `config/assumptions.toml`; synthetic test inputs appear only in tests and are not represented as market observations.
