import inspect

class Errors:
    def __init__(self):
        pass

    def toFile(self):
        pass

    def __len__(self):
        curframe = inspect.currentframe()
        callframe = inspect.getouterframes(curframe, context=15)
        for upperframe in callframe:
            print "    caller: ", upperframe[1]
        print "len is called"
        return 0

e = Errors()
len(e)
e.toFile()
