# LBR_Save_Parser
A script to parse Leaf Blower Revolution save files for relevant information, and output them as a CSV for use in associated community calculator spreadsheets.

## Usage
By default, the game saves to `%localappdata%/blow_the_leaves_away/save.dat` in binary-encoded base64, so the script reads from that location and decodes it before working. The data is processed and organized, and the output is saved to LBR_Save.csv on your Windows Desktop.

CLI hooks for different read/write locations have been requested. I'll probably allow for single files by CLI directly, or batch processing through the use of another file describing the associated lists of input/output locations.
