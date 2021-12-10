import sys
import re
import tkinter as tk
import configparser

# function to receive a list of strings and determine whether these match RE for members section
def validateMembers(input):
    patternString = r"^members\[\]={(\"[0-9]+\",)+\"[0-9]+\"};"
    pattern = re.compile(patternString, re.M)

    processLines = "".join(("".join(input)).split())
    match = pattern.search(processLines)
        
    if(match):
        return True
    else:
        return False

# function to receive a list of strings and determine whether these match RE for ranks section
def validateRanks(input):
    patternString = r"ranks\[\]={({\"[a-zA-Z0-9\.\-_()\[\]]+?\",\"[0-9]+?\",\"\w+?\"},)+{\"[a-zA-Z0-9\.\-_()\[\]]+?\",\"[0-9]+?\",\"\w+?\"}};"
    pattern = re.compile(patternString, re.M)

    processLines = "".join(("".join(input)).split())
    match = pattern.search(processLines)
        
    if(match):
        return True
    else:
        return False

# function to receive a list of strings and determine whether these match RE for vehicles section
def validateVehicles(input):
    patternString = r"vehicles\[\]={({\".*\",[0-9]+},)+{\".*\",[0-9]+}};"
    pattern = re.compile(patternString, re.M)

    processLines = "".join(("".join(input)).split())
    match = pattern.search(processLines)
        
    if(match):
        return True
    else:
        return False

# main function to validate an input file - receives filename (str) as input
def validateFile(input):
    print("Opening file {0} as a read-only file".format(input))
    try:
        with open(input, "r") as input:
            Lines = [line for line in input.readlines() if line.strip()]
        
        if not Lines:
            #logger.error("Error reading file " + input)
            print("Error reading file %s", input)
            sys.exit(2)

        # remove comments from file
        for line in Lines:
            if line.strip().startswith("//"):
                Lines.remove(line)

        # regular expression to validate file
        patternString = r"^members\[\]={(\"[0-9]+\",)+\"[0-9]+\"};ranks\[\]={({\"[a-zA-Z0-9\.\-_()\[\]]+?\",\"[0-9]+?\",\"\w+?\"},)+{\"[a-zA-Z0-9\.\-_()\[\]]+?\",\"[0-9]+?\",\"\w+?\"}};vehicles\[\]={({\".*\",[0-9]+},)+{\".*\",[0-9]+}};"
        pattern = re.compile(patternString, re.M)

        processLines = "".join(("".join(Lines)).split())
        match = pattern.search(processLines)
        
        # Build window for GUI
        window = tk.Tk()

        # Set label based on whether overall validation passed or failed
        if(match):
            result = "Processing overall file - MATCH FOUND"
            bg = "green"
        else:
            result = "Processing overall file - NO MATCH FOUND"
            bg = "red"
        overallResultLabel = tk.Label(text=result, bg=bg)

        # identify members section - assumes members section is a single line
        for line in Lines:
            if line.startswith('members'):
                membersSection = line
                break

        # process identified members section for individual validation
        if membersSection:
            membersResult = validateMembers(membersSection)
        else:
            print("Members section not found - error")
            exit(1)

        # build label for displaying result of members section processing
        if membersResult:
            result = "Processing members section - SUCCESS"
            bg = "green"
        else:
            result = "Processing members section - ERROR"
            bg = "red"
        membersResultLabel = tk.Label(text=result, bg=bg)

        # identify ranks section
        lineCount = 0
        ranksStartsAt = 0
        for line in Lines:
            if line.startswith('ranks'):
                ranksStartsAt = lineCount
                lineCount += 1
                break
            lineCount += 1
        
        if not ranksStartsAt:
            print("Ranks section not found - error")
            exit(2)

        for line in Lines[ranksStartsAt:]:
            if line.strip().endswith('};'):
                ranksEndsAt = lineCount
                break
            lineCount += 1

        # validate identified ranks section and build label based on result
        ranksResult = validateRanks(Lines[ranksStartsAt:ranksEndsAt])
        if ranksResult:
            result = "Processing ranks section - SUCCESS"
            bg = "green"
        else:
            result = "Processing ranks section - ERROR"
            bg = "red"
        ranksResultLabel = tk.Label(text=result, bg=bg)

        # identify vehicles section
        vehiclesStartsAt = 0
        for line in Lines[ranksEndsAt:]:
            if line.startswith('vehicles'):
                vehiclesStartsAt = lineCount
                lineCount += 1
                break
            lineCount += 1

        if vehiclesStartsAt == 0:
            print("Vehicles section not found - error")
            exit(2)

        for line in Lines[vehiclesStartsAt:]:
            lineCount += 1
            if line.strip().endswith('};'):
                vehiclesEndsAt = lineCount
                break

        # validate identified ranks section and build label based on result
        vehiclesResult = validateVehicles(Lines[vehiclesStartsAt:vehiclesEndsAt])

        if vehiclesResult:
            result = "Processing vehicles section - SUCCESS"
            bg = "green"
        else:
            result = "Processing vehicles section - ERROR"
            bg = "red"
        vehiclesResultLabel = tk.Label(text=result, bg=bg)

        # add result labels to UI and display
        overallResultLabel.pack()
        membersResultLabel.pack()
        ranksResultLabel.pack()
        vehiclesResultLabel.pack()
        window.mainloop()


    except IOError as e:
        print("I/O error({0}): {1}".format(e.errno, e.strerror))
        sys.exit(3)

# MAIN BODY

# name of config file to read from
confFile = "validator.conf"

config = configparser.ConfigParser()
config.sections()
config.read(confFile)

# name of file to validate
filename = config['FILE']['filename']

validateFile(filename)