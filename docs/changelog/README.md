# Changelog Directory

This directory contains rotated changelog files to track changes over time.

## File Format

- **Naming Convention:** `CHANGELOG-YYYY-MM-DD.md`
- **Example:** `CHANGELOG-2026-01-25.md`

## Organization

Each changelog file is created with the current date and contains all releases documented during that period. This rotation strategy:

- Prevents any single changelog file from becoming too large
- Makes it easy to find changes from a specific time period
- Maintains a clear chronological organization

## Style Guide

All changelog files follow the style guide defined in:
`.claude/skills/changelog-generator/references/CHANGELOG_STYLE.md`

Key principles:
- Write for users, not machines
- Use imperative mood (e.g., "Add feature" not "Added feature")
- Include references to PRs/issues/commits
- Order changes by importance
- Filter out noise and internal changes

## Generating Changelogs

Use the `/changelog-generator` skill to automatically create changelogs from git commits:

```
Create a changelog for commits from the past 7 days
```

The skill will analyze git history, categorize changes, and transform technical commits into user-friendly release notes.
