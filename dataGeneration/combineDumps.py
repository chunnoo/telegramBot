import glob

content = []

with open("combinedDump.txt", "w") as outFile:
    for fileName in glob.glob("convertedMessages/*.txt"):
        print("adding", fileName)
        with open(fileName, "r") as inFile:
            for line in inFile:
                outFile.write(line)

