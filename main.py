import os
from glob import glob
import shutil
import traceback
from pathlib import Path
import re
from urllib.parse import unquote

# -------------------------------
# Settings
# -------------------------------

source = "C:/Users/lumer/Documents/LumeRaw"
dest = "C:/Users/lumer/Documents/Lume"

useSubfolderForAttachments = True
# If true, attachments will be stored in a subfolder where the document is.
# Otherwise, they'll be stored in a folder at root of the vault.

attachmentFolderName = "attachments"
# Folder name where attachments will be stored.

ignoreEmptyDocument = True
# If the content of a document after content modification contains only whitespaces or is empty, the document will be ignored.


# -------------------------------
# Content Modification Options 
# -------------------------------

stripFinalContent = True
# Strip new lines and white spaces at start and end of a note

normalizeMarginOfQuoteBlock = True
# Add a quoted new line at before the start of a quoted section if there's none present.

removeCreatedUpdatedLine = True
# Remove lines starting with "Updated: " and "Created: "

removeEmptyLineAfterHeading = True
# Remove an empty line followed by any heading.

removeEmptyLines = False
# Remove empty lines from notes


# -------------------------------
# Advanced
# -------------------------------

logEachProcessedFile = False
# Print a log for each processed file. This does not affect error logs.

replacedCharactersInPath = (
  ('/', '.'),
)
# Replaced characters in file/directory names.
# An entry of ('/', '.') is equivalent to replacing all instances of '/' to '.' in file/dir names.

allowedCharactersInPath = "!@#$%^&()_+[]{};'`~, .-"
# Allowed characters in file/directory names. This is used when sanitizing file names.
# Any character that are not alphanum and also not included here will be removed.


idToSanitizedName = {}
linkRegex = re.compile("\[(?:(?!\]\()(?:.|\n))*\]\((?:(?!\))(?:.|\n))*\)")

def getIdFromPath(path):
  path = os.path.basename(path)
  return getIdFromName(path)

def getIdFromName(name):
  try:
    id = name.rsplit(".", 1)[0]
    id = name.rsplit(" ", 1)[1]
    return id
  except:
    return name

def getSanitizedNameFromName(name):
  if name == ".": return "."
  id = getIdFromName(name)
  if id in idToSanitizedName:
    return idToSanitizedName[id]
  else:
    print("Failed to get sanitized name from name:", name)
    return name

def resolveUri(uri):
  return uri

def sanitize(string):
  for entry in replacedCharactersInPath:
    string = string.replace(entry[0], entry[1])
  string = "".join( x for x in string if (x.isalnum() or x in allowedCharactersInPath))
  return string

def process():
  try:
    shutil.rmtree(dest, ignore_errors=True)
  except:
    pass

  everything = [y for x in os.walk(source) for y in glob(os.path.join(x[0], '*'))]

  files = list(filter(os.path.isfile, everything))
  folders = list(filter(os.path.isdir, everything))

  for filePath in files:
    if not filePath.lower().endswith(".md"): continue

    f = open(filePath, encoding="utf-8")
    firstLine = f.readline()
    if firstLine.startswith("# "):
      sanitized = firstLine[1:].strip() + ".md"
      sanitized = sanitize(sanitized)
    else:
      sanitized = sanitize(os.path.basename(filePath))
    sanitized = os.path.splitext(sanitized)[0]
    idToSanitizedName[getIdFromPath(filePath)] = sanitized
    f.close()

  for folderPath in folders:
    id = getIdFromPath(folderPath)
    if id not in idToSanitizedName:
      idToSanitizedName[id] = os.path.basename(folderPath).rsplit(" ", 1)[0]

  for filePath in files:
    if filePath.lower().endswith(".md"):
      handleMarkdownFile(filePath)
    else:
      handleAttachmentFile(filePath)


def handleMarkdownFile(filePath):
  if logEachProcessedFile: print("Processing .md document at", filePath)
  sourceDirectory = os.path.dirname(filePath)
  sourceRelDirectory = os.path.relpath(sourceDirectory, source)

  f = open(filePath, encoding="utf-8")
  firstLine = f.readline()
  if firstLine.startswith("# "):
    newName = firstLine[1:].strip() + ".md"
    newName = sanitize(newName)
  else:
    f.seek(0)
    newName = os.path.basename(filePath)
  
  pathParts = Path(sourceRelDirectory).parts
  if pathParts == (): pathParts = (".",)
  newRelDirectory = os.path.join(*list(map(getSanitizedNameFromName, pathParts)));
  
  newPath = os.path.join(dest, newRelDirectory, newName)
  try:
    os.makedirs(os.path.join(dest, newRelDirectory))
  except:
    pass
  newF = open(newPath, mode="w", encoding="utf-8")

  finalContent = ""
  prevLine = ""
  for currentLine in f:
    currentLine = currentLine.rstrip('\n')

    if removeEmptyLines and currentLine == "":
      prevLine = currentLine
      continue

    if removeCreatedUpdatedLine and (currentLine.startswith("Created: ") or currentLine.startswith("Updated: ")):
      prevLine = currentLine
      continue

    if removeEmptyLineAfterHeading and prevLine.startswith("#") and currentLine == "":
      prevLine = currentLine
      continue

    if normalizeMarginOfQuoteBlock and currentLine.startswith(">") and not currentLine.strip() == ">" and not prevLine.strip() == ">":
      finalContent += ">\n"
      finalContent += currentLine + "\n"
      prevLine = currentLine
      continue
    
    matches = linkRegex.findall(currentLine)
    if len(matches) > 0:
      replacements = {}

      for match in matches:
        embName, embUri = match[1:-1].split("](")
        if embUri.lower().endswith(".md"):
          parts = Path(unquote(embUri)).parts
          parts = list(map(getSanitizedNameFromName, parts))
          finalUri = "/".join(parts)
          replacements[match] = f"[[{finalUri}|{embName}]]"
        else:
          resolvedUri = resolveUri(embUri)
          replacements[embUri] = resolvedUri

      resultLine = currentLine
      for repl in replacements:
        resultLine = resultLine.replace(repl, replacements[repl])
      finalContent += resultLine + "\n"
      continue

    finalContent += currentLine + "\n"
    prevLine = currentLine

  if stripFinalContent:
    finalContent = finalContent.strip()
  if ignoreEmptyDocument and finalContent.strip() == "":
    newF.close()
    os.remove(newPath)
  else:  
    newF.write(finalContent)
    newF.close()
  f.close()


def handleAttachmentFile(filePath):
  if logEachProcessedFile: print("Processing attachment file at", filePath)
  sourceFileName = os.path.basename(filePath)
  sourceDirectory = os.path.dirname(filePath)
  sourceRelDirectory = os.path.relpath(sourceDirectory, source)
  pathParts = list(Path(sourceRelDirectory).parts)
  if len(pathParts) == 0:
    return
  lastPart = pathParts.pop()
  pathParts = list(map(getSanitizedNameFromName, pathParts))
  pathParts.append(attachmentFolderName)
  pathParts.append(lastPart)
  newRelDirectory = os.path.join(*pathParts);
  newPath = os.path.join(dest, newRelDirectory, sourceFileName)
  try:
    os.makedirs(os.path.join(dest, newRelDirectory))
  except:
    pass
  
  shutil.copyfile(filePath, newPath)

shutil.move(os.path.join(dest, ".obsidian"), ".obsidian")

try:
  process()
except Exception as e:
  print()
  print("Processing failed with following exception: ")
  traceback.print_exception(e)
  print()
shutil.move(".obsidian", os.path.join(dest, ".obsidian"))
print("Processing complete!")

