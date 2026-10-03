# Patch Plan

Grouping rules (from prompt `22`): every finding lands in exactly one patch
set; the P0-only immediate set carries no dependencies; a fix spanning 3+
files gets its own set even when small; dependencies between sets are noted
explicitly. One section per set, ordered by landing sequence.

## PS-001 - Immediate (P0 only, no dependencies)

| Finding ID | Files | Dependencies | Effort | Verification command |
|---|---|---|---|---|

## PS-002 - <name> (severity focus)

| Finding ID | Files | Dependencies | Effort | Verification command |
|---|---|---|---|---|

(repeat one section per patch set)

## Validation Plan

Commands that prove each set landed (tests, typechecks, migration checks).
Every set needs at least one verification command; a set with none is not
done.

## Definition of Done
