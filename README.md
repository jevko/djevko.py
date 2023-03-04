[EXPERIMENTAL]

# djevko.py

A variant of Jevko implemented in Python which differs from the original in that:

* it uses [heredocs/quoting](HEREDOCS.md) instead of digraphs to "escape" special characters
* it automatically [trims whitespace](WHITESPACE.md) in unquoted text

## Rationale

The major advantage of Djevko over Jevko is that prefixes and suffixes can be represented as simple (index + length) slices -- a parser can get by without copying and splicing source text. This is thanks to using heredocs instead of digraph-based escaping -- it is also why Djevko can't be backwards-compatible with Jevko (this advantage would be nullified by support for digraphs).

Thanks to heredocs it is also possible to paste fragments of text into Djevko nodes without the need of escaping them -- the only requirement is using a unique delimiter.

## See also

This implementation is a simplified version of [djevko.h](https://github.com/jevko/djevko.h). It does not support length-prefixed strings and is defined over Python characters (~ Unicode code points, like vanilla Jevko) rather than bytes.