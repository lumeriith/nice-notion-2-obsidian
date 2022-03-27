# NN2O
Nice-Notion-2-Obsidian, Notion to Obsidian migration tool with helpful features

# Warning
This script is under development and has several caveats.
1. This script is not very user-friendly.
2. This script is not tested and might contain bugs.
3. This script is fitted to cover my very own exact use case, and it needs some adjustments for general users to make use.
4. This script does no attempt to extract additional data from .CSV files to help with the process.

# Features
- Change names of files and directories to use their full name
- Fixes attachment links/internal links to your notes
- Moves and arranges all attachments to subfolders of their notes
# Additional Nice Features
This script provides several helpful (and opinionated) features.
They are completely optional and can be toggled on and off to match your use case.
- Replace specific characters from file/directory names
- Ignore empty documents
- Strip white spaces from note content
- Remove Created: Updated: lines from notes
- Add padding on top of quote blocks like bottom side so they don't look awful
- Remove empty line after any headings (that Notion adds by default)
- Remove every empty lines

# Instructions (Read it)
1. Clone this repository or download main.py.
1. Create a new vault in Obsidian. (WARNING: All contents in that vault will be erased except your settings!)
1. Extract your exported .zip from Notion. 
1. Open main.py and edit settings on top of the file.
    1. Change value of `source` variable to absolute path of the folder you extracted. (The zip file you exported from Notion)
    2. Change value of `dest` variable to the vault path you created. (AGAIN, ALL CONTENTS IN THAT VAULT WILL BE ERASED!)
    3. Optionally edit other settings to match your use case.
1. Start the script by executing `python main.py` in your favourite terminal.
When the script successfully finishes, your vault will be populated with converted notes and attachment files.
If you encounter any problems, you can try editing the settings and executing the script again.
