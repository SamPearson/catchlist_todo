# ⚠️ LEGACY CONFIG MODULE - DEPRECATED ⚠️

**WARNING: This module contains legacy configuration code that is scheduled for refactoring.**

Do not add new functionality to this module. Instead, refer to the new configuration patterns in the project.

## Current Usage

This module is still referenced by various parts of the codebase for:

- Database connection via `db_setup.py`
- Model definitions in `models.py`
- Environment configuration in `environments/`

## Migration Plan

All functionality in this module is being gradually migrated to more appropriate locations:

- Database models → `src/database/models/`
- Configuration → `src/core/config/`
- External clients → `src/integrations/`

## Guidelines

1. Do NOT add new code to this module
2. When modifying existing code, consider migrating it
3. Reference the new modules when possible
4. Update imports gradually to use new module paths

## Timeline

Complete migration target: Q3 2025

For questions about the migration process or where to place new code, contact the architecture team.
