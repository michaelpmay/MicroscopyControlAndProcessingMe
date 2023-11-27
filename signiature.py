import hashlib
import glob
import sys

if len(sys.argv)==1:
    raise ValueError('Needs a folder input')
files=glob.glob(sys.argv[1]+'/*',recursive=True)
hash=hashlib.sha256()
print(hash.hexdigest())
for file in files:
    try:
        with open(file,'rb') as f:
            for line in f:
#                print(line)
                hash.update(line)
    except IsADirectoryError as e:
        pass
hash=hash.hexdigest()

sys.stdout.write(hash)
sys.stdout.flush()
sys.exit(0)

