OCR for Apex Legends stat tracking
======

This program uses Tesseract to perform Optical Character Recognition on the XP Breakdown screen at the end of every Apex Legends match. This screen has to be passed to the program as a screenshon, and the screenshot is pre-processed (cropping, image manipulation) and then read to glean the following information from the screen:
* Creation time of screenshot
* Approximate match start time
* Duration of match
* Number of kills
* Damage done
* Revives
* Respawns
* Whether the group was partially premade

This information will then be written to a csv file using Pandas, for future use in analysis.

Directory Structure
------

The program works by the current file directory,  and screenshots should be placed in a folder titled `image_data`. This folder should only contain screenshots of the XP Breakdown screen as there is no filtering done for non-end-screens.

.
|-Project folder
    |- image_data
    |     - 1.png
    |     - ....png
    game_data.csv  


Running the program
------
The program can be run by running `python ocrproject.py` in the working directory. `game_data.csv` will be updated with new screenshot information based on the datetime stored in `screenshot_datetime`. If you'd like to generate a new CSV file with all the images in the folder, please delete any instance of `game_data.csv` in the root folder of the program. 