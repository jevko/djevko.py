# Heredocs

Say we have a djevko such as:

```
allowed characters [0123456789]
```

And we would want to add `[` and `]` to `allowed characters` without them being interpreted as special. We can do this simply by surrounding the characters with `` ` ``:

```
allowed characters [`0123456789[]`]
```

We could even include the `` ` `` character itself, provided that we don't put it immediately before the quoted `]`:

```
allowed characters [`0123456789[]``]
```

What if we had to put it before the `]` though? Simply precede the opening `` ` `` with a [tag of your choice](#rules-for-tags) and put a matching tag after the closing `` ` ``:

```
allowed characters [=`0123456789[`]`=]
```

Here we chose `=` as the tag. Now if we wanted to put a `=` before the `]` as well, we simply adjust the tag:

```
allowed characters [==`0123456789[`=]`==]
```

Here we chose `==` as the tag.

## Rules for tags

We can pick any tag we like, provided it doesn't contain the special characters `[`, `]`, or `` ` ``.

Tags which are integers (e.g. `10`) are exceptional -- they indicate [length-prefixed strings](#length-prefixed-strings) which work differently than heredocs described above.

## Notes about whitespace in tags

Note that whitespace that precedes the opening tag is not counted as part of it, so this:

```
allowed characters [  ==`0123456789[`=]`==]
```

is equivalent to the above. Similarly, whitespace that follows the closing tag does not count:

```
allowed characters [==`0123456789[`=]`==  ]
```

Also, whitespace inbetween the tag and the `` ` `` on either side is [not allowed](#why-not-allow-whitespace-inbetween-tag-and). 

❌ So the following won't work:

```
allowed characters [==  `0123456789[`=]`==]
```

❌ Neither will this:

```
allowed characters [==`0123456789[`=]`  ==]
```

Finally, whitespace inside the tag is allowed and considered part of the tag. So all of the below are correct and equivalent:

```
allowed characters [= =`0123456789[`=]`= =]

allowed characters [  = =`0123456789[`=]`= =]

allowed characters [= =`0123456789[`=]`= =  ]

allowed characters [  = =`0123456789[`=]`= =  ]
```

The tag here is `= =`.

## Characters that are considered whitespace

Whether a byte qualifies as whitespace is determined by [isspace](https://cplusplus.com/reference/cctype/isspace/). Therefore the following characters are considered whitespace:

```
' ' 	(0x20)	space (SPC)
'\t'	(0x09)	horizontal tab (TAB)
'\n'	(0x0a)	newline (LF)
'\v'	(0x0b)	vertical tab (VT)
'\f'	(0x0c)	feed (FF)
'\r'	(0x0d)	carriage return (CR)
```

## Why not allow whitespace inbetween tag and `` ` ``?

As mentioned above, whitespace inbetween the opening tag and the `` ` `` as well as inbetween the `` ` `` and the closing tag is not allowed.

❌ So the following won't work:

```
allowed characters [==  `0123456789[`=]`==]
allowed characters [==`0123456789[`=]`  ==]
allowed characters [==  `0123456789[`=]`  ==]
```

The reasons for that are the following:

* it is easier to visually spot opening and closing tags this way: opening tag is always *immediately* followed by `` ` ``, closing tag is always *immediately* preceded by `` ` `` -- they become mirrored, kind of like `[` and `]`
* it makes the probability of an accidental match of a closing tag slightly lower than if the whitespace was allowed
* it makes the design more minimal (a guiding principle that underlies Jevko as well as Djevko)
* it requires less information and is simpler to recover the boundary and the whitespace than in the case of allowing whitespace on both sides



<!-- The first 2 cases make it possible to format [heredocs](HEREDOCS.md) to be more human-readable and writable, so you are not required to smoosh everything together:

```
[...]tag`heredoc`tag[...]
```

but can format it nicely instead:

```
[...]
tag`heredoc`tag
[...]
``` -->



<!-- If the newlines before the opening tag and the after the closing tag were significant, the tags wouldn't match -- opening would be `"\ntag"`, closing would be `"tag\n"`. -->