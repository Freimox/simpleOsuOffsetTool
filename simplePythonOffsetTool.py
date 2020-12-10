"""
Simple offset tool for .osu & .osb files when changing mp3s
Requests an input from the user for the offset and creates a new file with the offset applied
Current Problems: Having sprites named "Sprite" or "Animation" would ignore offsets
"""

__author__ = 'Sean (freihy), "freimox"'
__docformat__ = 'reStructuredText'

import os

class main_menu:
    """
    Main menu for choosing what to do with the input files or to edit how it's modified
    Also includes the file management system and file detection
    """

    def __init__(self):
        """
        Sets the initial settings and get the input file
        """
        self.settings = {"Hit_Objects": True, "Timing_Points": True, "Events": True, "Bookmarks": True}
        self.PRINT_MENU = ((30 * "-") + "MAIN MENU" + (30 * "-") + "\n" +
                           "1. Offset" + "\n" +
                           "2. Settings" + "\n" +
                           "0. Exit")
        self.updatePrintSettings()

    def getFiles(self) -> list:
        """
        Attempts to locate the operational files in the input directory
        Returns a list of the files of interest
        """
        try:
            os.mkdir('input')
            files = None
            self.noFileError()
        except:
            files = os.listdir('input')

        operationFiles = []
        for file in files:
            if 'osb' in file or 'osu' in file:
                operationFiles.append(file)

        return operationFiles

    def noFileError(self):
        """
        Used when no files can be located in the directory 'input'
        Prompts user to check and tries to find the applicable files again
        """
        while len(self.files) == 0:
            print("Oops! No files are found! Please check that you copied the contents INSIDE your osu beatmap to "
                  "input!")
            choice = input("Press any key to after you've placed the files correctly\n")
            self.files = self.getFiles()

    def updatePrintSettings(self):
        """
        Updates the variable print_settings when changes are made
        """
        self.print_settings = ((30 * "-") + "SETTINGS" + (30 * "-") + "\n" +
                               "1. Affect Hit Objects: " + str(self.settings["Hit_Objects"]) + "\n" +
                               "2. Affect Timing Points: " + str(self.settings["Timing_Points"]) + "\n" +
                               "3. Affect Events (Storyboard): " + str(self.settings["Events"]) + "\n" +
                               "4. Affect Bookmarks: " + str(self.settings["Bookmarks"]) + "\n" +
                               "0. Exit")

    def doSettings(self):
        """
        Menu for settings
        Picking a choice flips the variable in settings dictionary according to user choice
        """
        contSettings = True
        while contSettings:
            print(self.print_settings)
            choice = input("Choice: ")
            try:
                choice = int(choice)
                if choice == 1:
                    self.settings["Hit_Objects"] = self.settings["Hit_Objects"] is False
                    self.updatePrintSettings()
                elif choice == 2:
                    self.settings["Timing_Points"] = self.settings["Timing_Points"] is False
                    self.updatePrintSettings()
                elif choice == 3:
                    self.settings["Events"] = self.settings["Events"] is False
                    self.updatePrintSettings()
                elif choice == 4:
                    self.settings["Bookmarks"] = self.settings["Bookmarks"] is False
                    self.updatePrintSettings()
                elif choice == 0:
                    contSettings = False
                else:
                    print("\nYou've chosen an invalid choice!")
            except:
                print("\nChoices are numerical!")

    def doMenu(self):
        """
        Main user menu to allow the user to make choices
        """
        contMenu = True
        while contMenu:
            print(self.PRINT_MENU)
            choice = input("Choice: ")
            try:
                choice = int(choice)
                # Choose to do offset
                if choice == 1:
                    self.initOffset()
                # Goto settings
                elif choice == 2:
                    self.doSettings()
                elif choice == 0:
                    contMenu = False
                else:
                    print("Please pick a valid option!\n")
            except ValueError:
                print("Input a number that corresponds to the choice you want!\n")

    def initOffset(self):
        """
        Checks for files, does noFileError if files don't exist
        Creates environment for offset
        Does loop for each osb or osu file visible in <input>
        """
        # Try to locate osu/osb files in input folder
        self.files = self.getFiles()
        if len(self.files) == 0:
            self.noFileError()
        print((30 * "-") + "FILES FOUND" + (30 * "-"))
        for item in self.files:
            print(item)

        # Assign the proper input/output names
        inputFiles = [('input/' + item) for item in self.files]
        outputFiles = [('output/' + item) for item in self.files]

        # Get the offset wanted
        r = True
        while r:
            offsetWanted = input("Offset: ")
            try:
                offsetWanted = int(offsetWanted)
                r = False
            except ValueError:
                print("Invalid offset\n")

        # Do the actual offset using the appropriate files
        try:
            os.mkdir('output')
        except FileExistsError:
            pass
        for i in range(len(self.files)):
            run = offsetWizard(self.settings, inputFiles[i], outputFiles[i])
            run.driver(offsetWanted)
        print("Offset completed!\n")


class offsetWizard():
    """
    Attempts to conduct the offset of the input file, creates a new output file with the offset applied
    Also finds out what file we're dealing with, if osb - override user settings
    """

    def __init__(self, settings: dict, input: str, output: str):
        """
        Attempts to locate the input file
        Raises exception if not found
        """
        # Attempt to locate input file
        self.input = input
        self.output = output
        try:
            self.f = open(self.input, "r", encoding='utf-8')
            self.settings = settings
        except:
            raise Exception
        self.modified = []

    def driver(self, offset: int):
        """
        Main driver function
        Runs the offset - Creates new variable modified; the offsetted .osb/.osu file
        Write the variable into a new file
        """
        self.doOffset(offset)
        writeThis = self.getModified()
        self.writeFile(writeThis)

    def writeFile(self, write: list):
        """
        Write the completed offset file into the directory
        """
        global w
        self.f.close()
        # Re-write Twice to ensure completeness
        for i in range(2):
            w = open(self.output, "w", encoding='utf-8')
            for line in write:
                w.write(line)
            w.close()

    def doOffset(self, offset: int):
        """
        Attempts to do the offset
        """
        event_BreakPeriods = False
        event_Storyboard = False
        event_SoundSamples = False
        timing_point = False
        hit_objects = False
        for line in self.f:
            oriLine = line
            line = line.strip().split(",")

            # Event activators
            if "Break Periods" in line[0]:
                event_BreakPeriods = True
            elif "//Storyboard Layer" in line[0]:
                event_BreakPeriods = False
                event_Storyboard = True
            elif "//Storyboard Sound Samples" in line[0]:
                event_Storyboard = False
                event_SoundSamples = True
            # Timing Point activator
            elif line[0] == "[TimingPoints]":
                event_SoundSamples = False
                timing_point = True
            elif line[0] == "[Colours]" or line[0] == "[Colors]":
                timing_point = False
            # Hit Objects activator
            elif line[0] == "[HitObjects]":
                hit_objects = True

            # Attempt Bookmark offset
            if line[0][:9] == 'Bookmarks' and self.settings["Bookmarks"]:
                self.modified.append(self.offsetBookmarks(line, offset))
            # Attempt Event offset
            elif event_BreakPeriods and self.settings["Events"]:
                self.modified.append(self.offsetBreakPeriods(line, offset))
            elif event_Storyboard and self.settings["Events"]:
                self.modified.append(self.offsetStoryboard(line, offset))
            elif event_SoundSamples and self.settings["Events"]:
                self.modified.append(self.offsetSoundSamples(line, offset))
            # Attempt Timing Point offset
            elif timing_point and self.settings["Timing_Points"]:
                self.modified.append(self.offsetTimingPoints(line, offset))
            # Attempt Hit Object offset
            elif hit_objects and self.settings["Hit_Objects"]:
                self.modified.append(self.offsetHitObjects(line, offset))
            else:
                self.modified.append(oriLine)

    def getModified(self) -> list:
        """
        Returns the completed modified osu/osb file
        """
        return self.modified

    def offsetBookmarks(self, line: list, offset: int) -> str:
        """
        Takes the line where it has the bookmarks, modifies each timestamp according to offset
        Returns the modified line
        """
        offsetBookmarks = []
        offsetBookmarks.append("Bookmarks: " + str(int(line[0][11:]) + offset))
        for i in range(1, len(line)):
            offsetBookmarks.append(str(int(line[i]) + offset))
        offsetBookmarks[len(line) - 1] = str(offsetBookmarks[len(line) - 1]) + '\n'
        return ','.join([str(elem) for elem in offsetBookmarks])

    def offsetBreakPeriods(self, line: list, offset: int) -> str:
        """
        Modifies break periods
        Creates a new list and doesn't modify the first variable of the break period.
        The rest are modified
        """
        offsetBreakPeriods = []
        offsetBreakPeriods.append(line[0])
        for i in range(1, len(line)):
            offsetBreakPeriods.append(str(int(line[i]) + offset))
        offsetBreakPeriods[len(line) - 1] = str(offsetBreakPeriods[len(line) - 1]) + '\n'
        return ','.join([str(elem) for elem in offsetBreakPeriods])

    def offsetStoryboard(self, line: list, offset: int) -> str:
        """
        Modifies storyboard elements
        Only affects the start and end time of the elements
        """
        if line[0] == "Sprite" or line[0] == "Animation" or "//Storyboard Layer" in line[0]:
            return ','.join([str(elem) for elem in line]) + '\n'
        elif line[0] != "Sprite" and line[0] != "Animation" and "//Storyboard Layer" not in line[0]:
            line[0] = ' ' + line[0]
            line[2] = int(line[2]) + offset
            if line[3] != '':
                line[3] = int(line[3]) + offset
            return ','.join([str(elem) for elem in line]) + '\n'

    def offsetSoundSamples(self, line: list, offset: int) -> str:
        """
        Modifies Sound Samples
        Only affects the second variable, the start time
        Leaves a space if there's no variable "Sample" found in the first slot
        """
        if line[0] == 'Sample':
            line[1] = int(line[1]) + offset
        return ','.join([str(elem) for elem in line]) + '\n'

    def offsetTimingPoints(self, line: list, offset: int) -> str:
        """
        Modifies timing points
        Only affects the first variable, where the timing point is placed
        """
        try:
            line[0] = int(line[0]) + offset
            return ','.join([str(elem) for elem in line]) + '\n'
        except:
            return ','.join([str(elem) for elem in line]) + '\n'

    def offsetHitObjects(self, line: list, offset: int) -> str:
        """
        Modifies hit objects
        Only affects the third variable, where the object is placed
        """
        try:
            line[2] = int(line[2]) + offset
            return ','.join([str(elem) for elem in line]) + '\n'
        except:
            return ','.join([str(elem) for elem in line]) + '\n'

if __name__ == '__main__':
    print('\n' * 50)
    print("Simple osu/osb offset script created by freihy! - V1.1\n")
    e = main_menu()
    e.doMenu()