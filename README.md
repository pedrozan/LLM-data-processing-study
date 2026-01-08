# LLM-data-processing-study
A study on the use of LLMs to process customer support tickets
## Setup

### Install Git Hooks

This repository uses git hooks to enforce Conventional Commits for commit messages. After cloning the repository, run the setup script:

```bash
bash scripts/setup-hooks.sh
```

This will install the `commit-msg` hook that validates your commits. For more details, see [COMMIT_CONVENTIONS.md](COMMIT_CONVENTIONS.md).