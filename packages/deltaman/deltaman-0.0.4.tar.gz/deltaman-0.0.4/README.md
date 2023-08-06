# Deltaman - Parsing human time intervals

```shell
pip install deltaman
```

## Getting Started

```python
from deltaman import delta_parser

for delta in ("15s", "3min", "1h15m", "1 day 12 hours", "1m-15s"):
    parsed = delta_parser.parse(delta)
    print(f'{delta!r:20s} {parsed!r:20s}')
```

That outputs

```
'15s'                datetime.timedelta(seconds=15)
'3min'               datetime.timedelta(seconds=180)
'1h15m'              datetime.timedelta(seconds=4500)
'1 day 12 hours'     datetime.timedelta(days=1, seconds=43200)
'1m-15s'             datetime.timedelta(seconds=45)
```

Note you can get more examples from the testing files.

## Testing

```shell
$ pytest
```

Or

```shell
$ tox
```
