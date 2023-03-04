[EXPERIMENTAL]

# djevko.py

A variant of Jevko implemented in Python which differs from the original in that:

* it uses heredocs/quoting instead of digraphs to "escape" special characters
* it automatically [trims whitespace](https://github.com/jevko/djevko.h/blob/master/WHITESPACE.md) in unquoted text

## See also

This implementation is a simplified version of [djevko.h](https://github.com/jevko/djevko.h). It does not support length-prefixed strings and is defined over Python characters (~ Unicode code points, like vanilla Jevko) rather than bytes.

Some details about heredocs with examples are [here](https://github.com/jevko/djevko.h/blob/master/HEREDOCS.md) -- note: the sections about "length-prefixed strings" don't apply here.