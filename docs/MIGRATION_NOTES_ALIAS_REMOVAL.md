# Migration note: alias cleanup (packages A-D)

## Scope
This note covers the alias-cleanup work for:
- Package A (helpers/value objects),
- Package B (scraper schemas/builders),
- Package C (base/validation/infrastructure),
- Package D (executor and residual quality violations).

## API impact

### Breaking changes
- `validation.rules` no longer exposes helper alias functions:
  - `required_field_rule(...)`
  - `type_rule(...)`
  - `range_rule(...)`

Use concrete rule classes directly (`RequiredFieldRule`, `TypeRule`, `RangeRule`) or `build_common_rules(...)`.

### Non-breaking changes
- `LapRecord.from_dict(...)` now performs explicit input validation (`Mapping` required) before construction.
- Validation and HTTP helper methods were refactored to remove pass-through alias patterns while preserving external behavior.
- `LayerOneExecutor` execution flow was decomposed into smaller private methods; public `run(...)` contract remains unchanged.

## Re-exports and integration checks
- Internal call sites in validation/infrastructure were updated to use canonical implementations.
- Public behavior is preserved except where explicitly noted in breaking changes above.
