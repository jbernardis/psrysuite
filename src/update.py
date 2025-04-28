import os
import shutil
from zipfile import ZipFile

newdir = "psrysuite.new"
olddir = "psrysuite.old"
curdir = "psrysuite"

zf = ZipFile("psrysuite-master.zip", "r")

zlist = zf.infolist()

zfdir = newdir

for zi in zlist:
	if not zi.filename.startswith("psrysuite-master/src"):
		continue

	if zi.filename.endswith(".gitignore"):
		continue

	if zi.is_dir():
		print("Processing directory %s" % zi.filename)
		zfdir = os.path.join(newdir, zi.filename[21:])
	else:
		print("    %s => %s" % (zi.filename, "path=%s" % zfdir))
		zf.extract(zi, path=zfdir)

print("renaming data directory to data-dist")
os.rename(os.path.join(newdir, "data"), os.path.join(newdir, "data.dist"))

print("moving virtual environment files to new directory")
shutil.move(os.path.join(curdir, "venv"), newdir)

print("copying the old data directory tree to the new environment")
shutil.copytree(os.path.join(curdir, "data"), os.path.join(newdir, "data"))

print("renaming the old enviironment to %s" % olddir)
os.rename(curdir, olddir)

print("renaming the new environment to %s" % curdir)
os.rename(newdir, curdir)

print("Creating logs and output directories in the new environment")
os.mkdir(os.path.join(curdir, "logs"))
os.mkdir(os.path.join(curdir, "output"))