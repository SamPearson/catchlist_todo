# Project Codewalk Notes

At the top level, the project has folders for:

- `api`
- `webapp`
- `database`
- `config`
- `common` (utils)

---

## Common Utils

- Contains a `date_utils` file.
- `date_utils` implements business logic related to dates.

---

## Config

- Contains an `environments` folder with:
  - `dev`
  - `staging`
  - `production`
  environment configuration files.
- Includes a CalDAV client.
- Contains several database-related modules:
  - `db_setup`
  - `db_config`
  - `models` (with a `models` subdirectory)

### `db_setup`

- Very small (two lines).
- Imports SQLAlchemy and initializes it into a `db` variable.
- Likely used as a shared/singleton database handle via imports.

### `db_config`

- Holds database configuration details such as:
  - Base path
  - Database path
  - SQLAlchemy database URI
  - JWT secret key
- Provides an `initialize_database` function (or similar).

### Config Models

- There is a `models` subdirectory.
- Appears to contain database models, though there may be overlap with the `database` directory models.

---

## Database

- Contains additional models.
- May be a newer or cleaner set of models replacing those in `config`.
- Overall pattern suggests something like:
  - Service / Model / Repository
- The better naming and pattern adherence here suggests:
  - `database` is the newer, preferred implementation.
  - `config` still contains older or “junk” database-related code.

---

## API

- Contains a `routes` directory that appears reasonably structured.
- Contains a `utils` directory with helper functions related to:
  - The `commitment` domain object.
  - Getting the current JWT user ID.

---

## Webapp

- Contains template files:
  - Organized into `components` and higher-level HTML templates.
- UI history suggests:
  - Use of Semantic UI
  - Then Bulma
  - Eventually a very basic, “developer’s special” type of UI framework.
- Other directories:
  - `routes` directory
  - `services` directory with:
    - API client services
    - Auth services
  - An `init_db` script (somewhat unexpectedly located in the webapp).

---

## Testing

- There is testing for both:
  - `api`
  - `webapp`
- Overall, this is a large project with extensive test coverage.

---

## Overall Assessment

- The project exhibits good architectural ideas:
  - Separation into API, webapp, database, config, and common utils.
  - Presence of routes, services, and model patterns.
- However, the organization is somewhat inconsistent:
  - Database-related concerns are split between `config` and `database`.
  - Some older/junk structures coexist with newer, better-organized code.
- All major architectural pieces exist, but they need reorganization and consolidation to reduce duplication and ambiguity.