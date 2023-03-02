from djevko import parse

parsed = parse("a [b] xyz` c `xyz [d[3`exp`3  ]   `ho ho ho`   ]  ff    ")

print(parsed.pretty_print())
print(parsed.original_str())
print(parsed.source())
print("|%s|" % parsed.subs[1].prefix.tag())
print("|%s|" % parsed.subs[1].djevko.suffix.tag())
print(parse("b`[`]`b"))