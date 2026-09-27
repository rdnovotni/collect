# Contributing to Collect

Thanks for helping. Collect is early, so the most valuable contributions are real-world evidence: items that don't fit the format, fields that are missing, and hobby knowledge.

## Ways to help

- **Report a record that doesn't fit.** Describe a real item and what you couldn't express. Use the "Spec change" issue template.
- **Propose a profile** for a hobby you know. Use the "Profile proposal" template.
- **Add vocabulary terms** (roles, identifier schemes, condition scales, profile values). Small pull requests are welcome.
- **Improve the tools** in `src/`, or write importers and exporters for other formats.

## Making changes

1. Fork the repository and create a branch.
2. Install the tools: `pip install -e ".[dev]"`.
3. Make your change. If you touch the format, update `spec/`, `schema/`, and at least one example together.
4. Run the checks:
   ```bash
   collect check-standard
   collect validate examples/postcard examples/package
   pytest
   ```
5. Add a line to `CHANGELOG.md` under "Unreleased" and open a pull request.

## How the format changes

- Discuss format changes in an issue before opening a pull request.
- The spec uses semantic versioning. Before 1.0, minor versions may break compatibility; each break is listed in the changelog.
- Profiles are versioned separately from the core.
- Prefer adding to vocabularies and profiles over changing the core. The core should stay small.

## Licensing of contributions

By contributing, you agree that your contributions are licensed under the repository's licenses: CC BY 4.0 for specification text, MIT for code, and CC0 for vocabularies and examples. Only contribute images you have the right to share, and give each image an accurate rights status.
