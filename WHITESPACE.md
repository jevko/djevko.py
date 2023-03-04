# Whitespace

For unqouted prefixes and suffixes, the parser outputs slices of text that make it easy to recover both the original and the trimmed versions of it.

Having access to the trimmed text makes it convenient to define data-interchange and configuration formats on top of Djevko whereas having access to the untrimmed text makes it convenient to define markup formats.

Having parser do the trimming on-the-fly also makes everything a bit faster.

In the rare cases where we need untrimmed (padded) text in non-markup formats, we can also use explicit quoting with heredocs:

```
` padded prefix ` [` padded suffix `]
```
