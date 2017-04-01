import os
import os.path
from PyAXML.AndroidXML import *
import zipfile
rootdir = "."
for parent,dirnames,filenames in os.walk(rootdir):
    #for dirname in dirnames:
    #    print(parent)
    #    print(dirname)
    if parent != rootdir:
        continue
    for filename in filenames:
        print(filename)
        if ".apk" in filename:
            zipFile = zipfile.ZipFile(filename)
            data = zipFile.read('AndroidManifest.xml')
            #print(data)
            apk = APK(data)
            apk.parse_androidxml()
            print(apk.getpackage()+" "+apk.getversion())
            zipFile.close()
