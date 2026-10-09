# envdiff

Compare two env files by key. The report names keys that are missing or different. It does not print values.

```
python3 -m envdiff fixtures/example.env fixtures/local.env
```

```
ONLY example.env  SENTRY_DSN
ONLY local.env  DEBUG
DIFFER  DATABASE_URL
SAME  2
```

`SAME` is the count of keys present on both sides with the same value. A blank line and a `#` comment are ignored. `export KEY=value` is the same as `KEY=value`. A value wrapped in matching quotes is compared without the quotes, so `KEY="abc"` and `KEY=abc` are the same. A duplicate key in one file is an error. The same two files always print the same text.

## Will not do

- Print a value, a password, or a connection string
- Expand `$OTHER` variables
- Upload the files or store a diff
- Treat a missing key as an empty value

## Tests

```
python3 -m unittest discover -s tests -v
```

Python 3.11 or newer. The standard library is enough.

## License

MIT.
