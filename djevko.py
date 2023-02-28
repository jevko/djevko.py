OPENER = "["
CLOSER = "]"
QUOTER = "`"
  
def isspace(c):
  return c == " " or c == "\t" or c == "\n" or c == "\r" or c == "\v" or c == "\f"

def trim_start(source, a, b):
  while (a < b and isspace(source[a])):
    a += 1
  return a
  
def trim_end(source, a, b):
  b -= 1
  while (b >= a and isspace(source[b])):
    b -= 1
  return b + 1
  
DELIM_CHAR = "="
def quote(s):
  length = len(s)
  
  is_padded = length > 0 and (isspace(s[0]) or isspace(s[length - 1]))
  m = 0 if is_padded else -1
  
  for i in range(0, length):
    c = s[i]
    if (m == -1 and (c == OPENER or c == CLOSER)): m = 0
    if (c == QUOTER):
      e = 0
      j = i + 1
      while (j < length and s[j] == DELIM_CHAR):
        e += 1
        j += 1
      i = j - 1
      # if (e > 5):
      #   return "%d%s%s" % (length, QUOTER, s)
      if (e > m): m = e
  if (m == -1): return s
  delim = DELIM_CHAR * m
  return "%s%s%s%s%s" % (delim, QUOTER, s, QUOTER, delim)

class Slice:
  def __init__(self, source, a, b):
    self.source = s
    self.a = a
    self.b = b

  def __str__(self):
    return self.source[self.a:self.b]

class Djevko:
  def __init__(self):
    self.subs = []
    self.suffix = ""
    self.delim = None
    
  def pretty_print_indent(self, pindent, indent):
    size = len(self.subs)
    ret: PoolStringArray = []
    if (size > 0):
      indent_str = " " * indent
      ret.append("\n")
      for i in range(0, size):
        p = self.subs[i].prefix
        ret.append(indent_str)
        if (len(p) > 0):
          ret.append("%s " % quote(p))
        ret.append(OPENER)
        ret.append(self.subs[i].djevko.pretty_print_indent(indent, indent + 2))
        ret.append("%s\n" % CLOSER)
      if (len(self.suffix) > 0):
        ret.append(indent_str)
        ret.append("%s\n" % quote(self.suffix))
      ret.append(" " * pindent)
    else:
      ret.append(quote(self.suffix))
    return "".join(ret)
  
  # todo: perhaps recover delims
  def pretty_print(self):
    ret: PoolStringArray = []
    for i in range(0, len(self.subs)):
      p = self.subs[i].prefix
      if (len(p) > 0):
        ret.append("%s " % quote(p))
      ret.append(OPENER)
      ret.append(self.subs[i].djevko.pretty_print_indent(0, 2))
      ret.append("%s\n" % CLOSER)
    ret.append(quote(self.suffix))
    return "".join(ret)

  def __str__(self):
    ret: PoolStringArray = []
    for i in range(0, len(self.subs)):
      ret.append(quote(self.subs[i].prefix))
      ret.append(OPENER)
      ret.append(str(self.subs[i].djevko))
      ret.append(CLOSER)
    ret.append(quote(self.suffix))
    return "".join(ret)

class Subdjevko:
  def __init__(self, prefix, djevko):
    self.prefix = prefix
    self.djevko = djevko
  
# a -- start index; b -- end index
def is_cd_found(
  source, 
  od_a, od_b, # od -- opening delimiter
  cd_a, cd_b, # cd -- closing delimiter
):
  # alt: cd_a = trim_start(source, cd_a, cd_b)
  while (od_a < od_b):
    if (source[cd_a] != source[od_a]): return False
    cd_a += 1
    od_a += 1
  while (cd_a < cd_b):
    if (isspace(source[cd_a]) == False): return False
    cd_a += 1
  return True
  
def open(source, a, b, parent, parents):
  d = Djevko()
  parent.subs.append(Subdjevko(source[a:b], d))
  parents.append(parent)
  return d

def close(source, a, b, parent, parents):
  if (len(parents) == 0): raise Exception("ERROR: unexpected closer at %d" % b)
  parent.suffix = source[a:b]
  return parents.pop()

def parse(source):
  # current index
  i = 0
  # current character
  c = ""
  # start index
  a = 0
  # opening delimiter start index
  od_a = 0
  # opening delimiter end index
  od_b = 0
  # closing delimiter start index
  cd_a = -1
  parent = Djevko()
  parents = []
  length = len(source)
  
  while (True):
    # get affix (prefix or suffix, either quote/heredoc or regular)
    while (i < length):
      c = source[i]
      # found opening delimiter: getting quote/heredoc
      if (c == QUOTER):
        # od -- opening delimiter; a -- start index; b -- end index
        od_a = trim_start(source, a, i)
        od_b = i # alt: trim_end(source, od_a, i)
        # cd -- closing delimiter; no candidate found yet
        cd_a = -1
        # quote/heredoc start index
        a = i + 1
        # go get quote/heredoc
        break
      # found opener: got prefix
      elif (c == OPENER):
        a = trim_start(source, a, i)
        parent = open(source, a, trim_end(source, a, i), parent, parents)
        a = i + 1
      # found closer: got suffix
      elif (c == CLOSER):
        a = trim_start(source, a, i)
        parent = close(source, a, trim_end(source, a, i), parent, parents)
        a = i + 1
      # next character
      i += 1
    # reached the end: got suffix
    else:
      a = trim_start(source, a, i)
      parent.suffix = source[a:trim_end(source, a, i)]
      break

    # skip quoter
    i += 1
    # get quote/heredoc
    while (i < length):
      c = source[i]
      # found closing delimiter candidate: set its start index
      if (c == QUOTER): cd_a = i + 1
      elif (cd_a != -1):
        # found opener after matching closing delimiter: got prefix
        if (c == OPENER and is_cd_found(source, od_a, od_b, cd_a, i)):
          parent = open(source, a, cd_a - 1, parent, parents)
          a = i + 1
          break
        # found closer after matching closing delimiter: got prefix
        elif (c == CLOSER and is_cd_found(source, od_a, od_b, cd_a, i)):
          parent = close(source, a, cd_a - 1, parent, parents)
          a = i + 1
          break
      # next character
      i += 1
    # reached the end 
    else:
      # end after matching closing delimiter: got suffix
      if (cd_a != -1 and is_cd_found(source, od_a, od_b, cd_a, i)): 
        parent.delim = source[od_a:od_b]
        parent.suffix = source[a:cd_a - 1]
        break
      else:
        raise Exception("ERROR: unexpected end while parsing quote with delimiter %s" % source[od_a:od_b])
    # skip opener/closer
    i += 1
  if (len(parents) > 0): 
    raise Exception("ERROR: unexpected end! Missing %d closers" % len(parents))
  return parent
  
def test():
  print(parse("a [b] xyz` c `xyz [d[3`exp`3  ]   `ho ho ho`   ]  ff    ").pretty_print())

test()