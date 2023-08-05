import os, sys, subprocess

path = os.path.join(os.path.dirname(__file__), "node.exe")

def call(args, **kwargs):
    return subprocess.call([
        path,
        *args
    ], **kwargs)

def run(args, **kwargs):
    return subprocess.run([
        path,
        *args
    ], **kwargs)

def Popen(args, **kwargs):
    return subprocess.Popen([
        path,
        *args
    ], **kwargs)

def main():
    sys.exit(call(sys.argv[1:]))

if __name__ == '__main__':
    main()