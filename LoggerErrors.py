import sys

def Error(printError, logValue = None):
    if logValue != None:
        print(printError, logValue)
    else:
        print(printError)
    sys.exit()