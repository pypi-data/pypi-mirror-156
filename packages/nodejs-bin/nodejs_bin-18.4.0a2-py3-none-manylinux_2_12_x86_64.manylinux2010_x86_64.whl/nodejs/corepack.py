import os, sys
from . import node

def call(args, **kwargs):
    return node.call([
        os.path.join(os.path.dirname(__file__), "lib/node_modules/corepack/dist/corepack.js"),
        *args
    ], **kwargs)

def run(args, **kwargs):
    return node.run([
        os.path.join(os.path.dirname(__file__), "lib/node_modules/corepack/dist/corepack.js"),
        *args
    ], **kwargs)

def Popen(args, **kwargs):
    return node.Popen([
        os.path.join(os.path.dirname(__file__), "lib/node_modules/corepack/dist/corepack.js"),
        *args
    ], **kwargs)

def main():
    sys.exit(call(sys.argv[1:]))

if __name__ == '__main__':
    main()