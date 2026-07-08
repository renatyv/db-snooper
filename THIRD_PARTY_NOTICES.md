# Third-Party Notices

DB Snooper source code is licensed under the MIT License. This notice summarizes licenses for declared Python dependencies and bundled datasets.

This file is informational and is not legal advice. Check each upstream project for the authoritative license text.

## Runtime Dependencies

| Package | Used by | License |
| --- | --- | --- |
| `datasketch` | Required | MIT |
| `numpy` | Transitive dependency of `datasketch` | BSD-3-Clause |
| `scipy` | Transitive dependency of `datasketch` | BSD-3-Clause, with bundled binary notices for some wheels |
| `sqlalchemy` | Required | MIT |
| `greenlet` | Transitive dependency of `sqlalchemy` on supported platforms | MIT |
| `typing-extensions` | Transitive dependency of `sqlalchemy` on some Python versions | PSF-2.0 |

## Optional Database Driver Dependencies

| Extra | Package | License |
| --- | --- | --- |
| `postgres` | `psycopg` | LGPL-3.0-only or later, as published by upstream metadata |
| `postgres` | `psycopg-binary` | LGPL-3.0-only or later, as published by upstream metadata |
| `postgres` | `tzdata` | Apache-2.0, when installed as a transitive dependency on some platforms |
| `mysql` | `pymysql` | MIT |
| `mariadb` | `mariadb` | LGPL-2.1-or-later |
| `duckdb` | `duckdb-engine` | MIT |
| `duckdb` | `duckdb` | MIT |
| `duckdb` | `packaging` | Apache-2.0 or BSD-2-Clause |

The LGPL-licensed database drivers are optional extras. They are not required to use the default SQLite functionality.

## Development And Build Dependencies

| Package | Used by | License |
| --- | --- | --- |
| `pytest` | `dev` extra | MIT |
| `colorama` | Transitive dependency of `pytest` on some platforms | BSD-3-Clause |
| `iniconfig` | Transitive dependency of `pytest` | MIT |
| `packaging` | Transitive dependency of `pytest` | Apache-2.0 or BSD-2-Clause |
| `pluggy` | Transitive dependency of `pytest` | MIT |
| `pygments` | Transitive dependency of `pytest` | BSD-2-Clause |
| `hatchling` | Build backend | MIT |

## Bundled Dataset Files

Files under `eval-dataset/` are derived from birdsql by The BIRD Team and are redistributed under the Creative Commons Attribution-ShareAlike 4.0 International License (CC BY-SA 4.0).

The `eval-dataset/` files are not covered by DB Snooper's MIT source-code license. Derivative works that include those dataset files must preserve the CC BY-SA 4.0 terms.

The source distribution configuration excludes `eval-dataset/` so published Python packages can be distributed separately from the bundled evaluation data.
