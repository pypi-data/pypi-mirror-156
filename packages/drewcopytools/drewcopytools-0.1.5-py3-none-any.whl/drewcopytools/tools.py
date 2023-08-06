# General tool type functions.


# -----------------------------------------------------------------------------
# This function is meant to take a command line as a single string, and split it
# into an array so that it can be used in subprocess.call.
def split_cmdline_args(input:str):
  res = []
  parts = input.split(' ')

  buffer = ''
  inQuotes = False

  for p in parts:
    bufferComplete = False

    if inQuotes:
      buffer += " " + p
      if buffer.endswith("\""):
        buffer = buffer[:-1]
        inQuotes = False
        bufferComplete = True
    else:
      buffer += p
      if buffer.startswith("\""):
        if buffer.endswith("\""):
          buffer = buffer[1:-1]
          bufferComplete = True
        else:
          inQuotes = True
          buffer = buffer[1:]
      else:
        bufferComplete = True

    if bufferComplete:
      res.append(buffer)
      buffer = ''

  return res

# ------------------------------------------------------------------------------------------------------------------------
# Calls a subprocess from a string in a cross-platform way.
# No more guessing what the right approach is.
def subprocess_really(exe:str):
  print(f'CALL:{exe}')

  if isinstance(exe, str):
    exe = split_cmdline_args(exe)

  callres = subprocess.call(exe)
  if callres != 0:
    print("CALL FAILED!")
    return False
  return True
