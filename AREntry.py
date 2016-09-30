import sys
import os
import ARContext

def autoResign(path, configuration):
    context = ARContext.ARContext(path, configuration)
    if context.validResignDir():
        context.startWork()

if __name__ == '__main__':
    workspace = sys.argv[1]
    if len(sys.argv) >= 2:
        configuration = sys.argv[2]
    else:
        configuration = 'product'
    if os.path.exists(workspace):
        autoResign(workspace, configuration)
    else:
        print "please set the resign workspace"