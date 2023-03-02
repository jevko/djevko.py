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

def find_tag(ss, tag, t):
  for s in ss:
    if (s == tag): return find_tag(ss, tag + t, t)
  return tag

DELIM_CHAR = "="
def quote(s, t = DELIM_CHAR):
  # todo: error message
  if (t == " "): raise Exception("oops")
  length = len(s)
  is_padded = length > 0 and (isspace(s[0]) or isspace(s[length - 1]))
  mode = 1 if is_padded else 0
  ss = []
  index = 0
  for i in range(0, length):
    c = s[i]
    if (c == QUOTER):
      mode = 2
      index = i + 1
    elif (c == OPENER or c == CLOSER):
      if (mode == 2):
        ss.append(s[index:trim_end(s, index, i)])
      mode = 1
  if (mode == 0): return s
  if (len(ss) == 0): return "%s%s%s" % (QUOTER, s, QUOTER)
  tag = find_tag(ss, "", t)
  return "%s%s%s%s%s" % (tag, QUOTER, s, QUOTER, tag)

class Slice:
  def __init__(self, source = "", a = 0, b = 0, pa = 0, pb = 0):
    self.source = source
    self.a = a
    self.b = b
    self.pa = pa
    self.pb = pb
    self.cached_tag = []

  def tag(self):
    if (len(self.cached_tag) == 1):
      return self.cached_tag[0]
    i = self.a - 1
    ret = None
    if (i > 0 and self.source[i] == QUOTER):
      ta = trim_start(self.source, self.pa, i)
      ret = self.source[ta:i]
    self.cached_tag.append(ret)
    return ret

  def __str__(self):
    return self.source[self.a:self.b]

  def full(self):
    return self.source[self.pa:self.pb]

class Djevko:
  def __init__(self):
    self.subs = []
    self.suffix = ""
    
  def pretty_print_indent(self, pindent, indent):
    size = len(self.subs)
    ret: PoolStringArray = []
    if (size > 0):
      indent_str = " " * indent
      ret.append("\n")
      for i in range(0, size):
        p = str(self.subs[i].prefix)
        ret.append(indent_str)
        if (len(p) > 0):
          ret.append("%s " % quote(p))
        ret.append(OPENER)
        ret.append(self.subs[i].djevko.pretty_print_indent(indent, indent + 2))
        ret.append("%s\n" % CLOSER)
      suffix = str(self.suffix)
      if (len(suffix) > 0):
        ret.append(indent_str)
        ret.append("%s\n" % quote(suffix))
      ret.append(" " * pindent)
    else:
      ret.append(quote(str(self.suffix)))
    return "".join(ret)
  
  # todo: perhaps a variant which recovers original tags
  def pretty_print(self):
    ret: PoolStringArray = []
    for i in range(0, len(self.subs)):
      p = str(self.subs[i].prefix)
      if (len(p) > 0):
        ret.append("%s " % quote(p))
      ret.append(OPENER)
      ret.append(self.subs[i].djevko.pretty_print_indent(0, 2))
      ret.append("%s\n" % CLOSER)
    ret.append(quote(str(self.suffix)))
    return "".join(ret)

  def __str__(self):
    ret: PoolStringArray = []
    for i in range(0, len(self.subs)):
      ret.append(quote(str(self.subs[i].prefix)))
      ret.append(OPENER)
      ret.append(str(self.subs[i].djevko))
      ret.append(CLOSER)
    ret.append(quote(str(self.suffix)))
    return "".join(ret)

  # perhaps this should be __str__:
  def original_str(self):
    ret: PoolStringArray = []
    for i in range(0, len(self.subs)):
      ret.append(self.subs[i].prefix.full())
      ret.append(OPENER)
      ret.append(self.subs[i].djevko.original_str())
      ret.append(CLOSER)
    ret.append(self.suffix.full())
    return "".join(ret)

  def source(self):
    return self.suffix.source

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
  
def open(source, a, b, pa, pb, parent, parents):
  d = Djevko()
  parent.subs.append(Subdjevko(Slice(source, a, b, pa, pb), d))
  parents.append(parent)
  return d

def close(source, a, b, pa, pb, parent, parents):
  if (len(parents) == 0): raise Exception("ERROR: unexpected closer at %d" % pb)
  parent.suffix = Slice(source, a, b, pa, pb)
  return parents.pop()

def parse(source):
  length = len(source)
  # index of current character
  i = 0
  # current character
  c = ""
  # start index of current slice
  a = 0
  # start index of current opening delimiter (aka delimiting identifier/boundary/nonce/tag) 
  od_a = 0
  # start index of whitespace before opening delimiter (will = od_a if none)
  pod_a = 0
  # end index of current opening delimiter 
  od_b = 0
  # closing delimiter start index; -1 means no candidate found yet
  cd_a = -1
  # pointer to current djevko -- initially the top-level one
  parent = Djevko()
  # stack of djevkos with parent of the current djevko at the top; its size is the current depth
  parents = []
  
  while (True):
    # get affix (prefix or suffix, either quoted/heredoc or unquoted)
    while (i < length):
      c = source[i]
      # found opening delimiter: getting quote/heredoc
      if (c == QUOTER):
        pod_a = a
        # od -- opening delimiter; a -- start index; b -- end index
        od_a = trim_start(source, a, i)
        od_b = i # alt: trim_end(source, od_a, i)
        # cd -- closing delimiter; -1 means no candidate found yet
        cd_a = -1
        # quote/heredoc start index
        a = i + 1
        # go get quote/heredoc
        break
      # found opener: got prefix
      elif (c == OPENER):
        parent = open(
          source, 
          trim_start(source, a, i), trim_end(source, a, i), 
          a, i, 
          parent, parents
        )
        a = i + 1
      # found closer: got suffix
      elif (c == CLOSER):
        parent = close(
          source, 
          trim_start(source, a, i), trim_end(source, a, i), 
          a, i, 
          parent, parents
        )
        a = i + 1
      # next character
      i += 1
    # reached the end: got suffix
    else:
      parent.suffix = Slice(source, trim_start(source, a, i), trim_end(source, a, i), a, i)
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
          parent = open(source, a, cd_a - 1, pod_a, i, parent, parents)
          a = i + 1
          break
        # found closer after matching closing delimiter: got suffix
        elif (c == CLOSER and is_cd_found(source, od_a, od_b, cd_a, i)):
          parent = close(source, a, cd_a - 1, pod_a, i, parent, parents)
          a = i + 1
          break
      # next character
      i += 1
    # reached the end 
    else:
      # end after matching closing delimiter: got suffix
      if (cd_a != -1 and is_cd_found(source, od_a, od_b, cd_a, i)):
        parent.suffix = Slice(source, a, cd_a - 1, pod_a, i)
        break
      else:
        raise Exception("ERROR: unexpected end while parsing quote with delimiter %s" % source[od_a:od_b])
    # skip opener/closer
    i += 1
  if (len(parents) > 0): 
    raise Exception("ERROR: unexpected end! Missing %d closers" % len(parents))
  return parent
