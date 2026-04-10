# Scraper inheritance and composition rules

## Goal
This document defines **hard architectural constraints** for scraper inheritance.
Primary objective: keep base scrapers as **template-method orchestrators** and move cross-cutting concerns (validation/export/reporting) to composed services.

## Capability interfaces
Each scraper family must implement capability contracts from `scrapers/contracts/protocols/capabilities.py`:

- `FetchCapability`
- `ParseCapability`
- `ValidateCapability`
- `ExportCapability`

The contracts are intentionally small and represent pipeline phases.

## Allowed inheritance patterns

### 1) Thin base scraper + composition (preferred)

- Base class defines pipeline flow (`fetch()`, `parse()`, orchestration hooks).
- Cross-cutting logic is delegated to services:
  - `ValidationCapabilityService`
  - `ExportCapabilityService`
  - `ReportingCapabilityService`
- Concrete scraper subclasses override only parsing/domain hooks.

### 2) Stateless utility mixins (allowed)

Mixins are allowed only when:

1. They **do not store business state** (no domain lifecycle ownership).
2. They **do not require MRO order tricks** (behavior must be explicit, deterministic).
3. They expose helper behavior, not end-to-end business orchestration.

## Hard mixin rules

Mixins are **forbidden** from:

- holding mutable business state (`self._records`, `self._domain_payload`, etc.);
- coordinating fetch/validate/export lifecycle transitions;
- relying on `super()` call-chain order to work correctly;
- introducing hidden coupling between unrelated domains.

## Anti-patterns (not allowed)

### Anti-pattern A: deep inheritance tree for cross-cutting concerns

```text
BaseScraper <- RetryMixin <- ValidationMixin <- ExportMixin <- DomainScraper
```

Why forbidden:

- fragile MRO coupling,
- low discoverability of behavior,
- difficult selective replacement during refactors.

### Anti-pattern B: stateful mixin controlling pipeline

```python
class ValidationMixin:
    self._invalid_records = []  # business state in mixin
```

Why forbidden:

- hidden lifecycle ownership outside explicit service.

### Anti-pattern C: mixin ordering dependency

```python
class A(MixinOne, MixinTwo, Base):
    ...  # works
class B(MixinTwo, MixinOne, Base):
    ...  # breaks
```

Why forbidden:

- violates deterministic architecture and makes refactoring unsafe.

## Migration guidance

When modernizing a scraper hierarchy:

1. Add/align capability interfaces.
2. Keep template-method hooks in base scraper.
3. Move validation/export/reporting to dedicated services.
4. Reduce mixins to stateless helpers only.
5. Remove MRO-sensitive behavior.
