# Jury

A black box testing tool

# Install

```bash
pip install jury-test
```

# Usage

main.py:

```python
import jury

cases = [
    "cases/example",
    "cases/types/types",
    "cases/cluster/sync",
]


def main():
    j = jury.Jury(cases)
    j.run()


if __name__ == '__main__':
    main()
```

run test with:

```bash
python main.py
# or
python main.py --single cases/types/types --verbose
```

