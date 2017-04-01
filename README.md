## PyAXML

PyAXML is lib for python to decode AndroidManifest.xml


## Features

- Get AndroidManifest.xml from a Apk.
- decode AndroidManifest.xml
##Usage
	zipFile = zipfile.ZipFile(filename)
	#apk is a zip file,so we can decode it using zipfile
	data = zipFile.read('AndroidManifest.xml')
	#data is Unpacked bytes,you can read from file
	apk = APK(data)
	apk.parse_androidxml()
	#apk.AndroidManifest is the xml that you wanted
	print(apk.getpackage()+" "+apk.getversion())
	zipFile.close()
## Contacts

My webpage is [http://www.sbfeng.cn](http://www.sbfeng.cn)

