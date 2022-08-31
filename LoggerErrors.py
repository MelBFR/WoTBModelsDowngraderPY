import sys

def LoggerError(printError):
    print(printError)
    sys.exit()

def LoggerErrorV(printError, logValue):
    print(printError, logValue)
    sys.exit()