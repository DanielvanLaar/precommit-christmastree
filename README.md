# precommit-christmastree

Custom Christmas-themed pre-commit hook that:
- sorts Python imports to Christmas tree shape
- Adds tree topper
- requires explicit staging to accept changes

To Install in your repo:

1. add .pre-commit-config.yaml

```yaml
repos:
  - repo: https://github.com/DanielvanLaar/precommit-christmastree
    rev: v1.0.3
    hooks:
      - id: import-length-order-with-stars
        args: ["--fix"]
```

2 Install the pre-commit hook

```bash
    pip install pre-commit
    pre-commit install
```

3 (optional) Run pre-commit once 

```bash
    pre-commit run --all-files
```

