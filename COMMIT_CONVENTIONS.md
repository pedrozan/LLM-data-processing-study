# Conventional Commits Setup

This repository uses **Conventional Commits** for commit messages to maintain clean git history and enable automated versioning.

## Initial Setup

When you clone this repository, install the git hooks by running:

```bash
bash scripts/setup-hooks.sh
```

This will install a `commit-msg` hook that validates your commit messages before they're committed.

## Commit Hook

A `commit-msg` hook is stored in `scripts/hooks/` and installed to `.git/hooks/` during setup. This will validate your commit messages before they're committed.

## Commit Message Format

```
<type>[optional scope]: <description>

[optional body]

[optional footer(s)]
```

## Valid Types

- **feat**: A new feature
- **fix**: A bug fix
- **docs**: Documentation changes
- **style**: Code style changes (formatting, missing semicolons, etc.)
- **refactor**: Code refactoring without feature changes
- **perf**: Performance improvements
- **test**: Adding or updating tests
- **chore**: Build process, dependencies, tooling changes
- **ci**: CI/CD configuration changes
- **revert**: Revert a previous commit

## Examples

### Simple commit
```bash
git commit -m "feat: add user authentication module"
```

### With scope
```bash
git commit -m "fix(api): handle null responses in endpoint"
```

### With body and footer
```bash
git commit -m "feat(auth): implement JWT token validation" -m "Add JWT token validation to protect API routes. Tokens are verified against the secret key stored in env." -m "Closes #123"
```

## What Happens If You Violate the Format

If you try to commit a message that doesn't follow the format, the hook will reject it with:

```
❌ Commit message does not follow Conventional Commits format

Valid format:
  <type>[optional scope]: <description>

Types: feat, fix, docs, style, refactor, perf, test, chore, ci, revert
```

Simply adjust your message and try again!

## Bypassing the Hook (Not Recommended)

If you absolutely need to bypass the hook in an emergency:

```bash
git commit --no-verify -m "your message"
```

However, this should be avoided to maintain consistency in your git history.
