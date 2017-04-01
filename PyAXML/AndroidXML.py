import zipfile
try:
    from . import NamespaceStack
    from . import StringBlock 
    from . import Utils
    from . import IntReader
    from . import TypeValue
except:
    import NamespaceStack
    import StringBlock 
    import Utils
    import IntReader
    import TypeValue

fw = None


def printf(msg):
    #print(msg)
    global fw
    if fw:
        try:
            fw.write(msg+"\n")
        except:
            fw.write("error...")
    return msg+"\n"


class AXmlResourceParser:
    reader = None
    strings = None
    m_event = 0
    decrease_depth = False
    namespaces = NamespaceStack.NamespaceStack()

    CHUNK_AXML_FILE = 0x00080003
    CHUNK_RESOURCEIDS = 0x00080180
    CHUNK_XML_FIRST = 0x00100100
    CHUNK_XML_START_NAMESPACE = 0x00100100
    CHUNK_XML_END_NAMESPACE = 0x00100101
    CHUNK_XML_START_TAG = 0x00100102
    CHUNK_XML_END_TAG = 0x00100103
    CHUNK_XML_TEXT = 0x00100104
    CHUNK_XML_LAST = 0x00100104

    ATTRIBUTE_IX_NAMESPACE_URI = 0
    ATTRIBUTE_IX_NAME = 1
    ATTRIBUTE_IX_VALUE_STRING = 2
    ATTRIBUTE_IX_VALUE_TYPE = 3
    ATTRIBUTE_IX_VALUE_DATA = 4
    ATTRIBUTE_LENGHT = 5

    TEXT = 0
    START_TAG = 1
    END_TAG = 2
    START_DOCUMENT = 3
    END_DOCUMENT = 4
    ERROR = 5

    def __init__(self, data = None):
        self.date = data
        self.reader = IntReader.IntReader(data=data)

    def open(self, data = None):
        if data != None:
            self.date = data
            self.reader = IntReader.IntReader(data=data)

    def close(self):
        self.data = None
        self.reader = None

    def next(self):
        self.do_next()
        return self.m_event
        '''try:
            self.do_next()
            return self.m_event
        except Exception as e:
            printf("error"+str(e))
            self.close()
            return self.ERROR'''

    def do_next(self):
        if not self.strings:
            Utils.Utils.check_type(self.reader, self.CHUNK_AXML_FILE)
            self.reader.skip_int()
            self.strings = StringBlock.StringBlock.read(self.reader)
            self.namespaces.increase_depth()
            self.m_operational = True

        if self.m_event == self.END_DOCUMENT:
            return
        event = self.m_event
        self.reset_eventinfo()
        while True:
            if self.decrease_depth:
                self.decrease_depth = False
                self.namespaces.decreaseDepth()
            if event == self.END_TAG and self.namespaces.get_depth() == 1 and self.namespaces.get_currentcount() == 0:
                self.m_event = self.END_DOCUMENT
            chunk_type = self.CHUNK_XML_START_TAG
            if event != self.START_DOCUMENT:
                chunk_type = self.reader.read_int()
                if not chunk_type:
                    self.m_event = self.END_DOCUMENT
                    break
            if chunk_type == self.CHUNK_RESOURCEIDS:
                chunk_size = self.reader.read_int()
                if chunk_size < 8 or chunk_size%4 != 0:
                    raise Exception("Invalid resource ids size ("+chunk_size+").")
                self.resource_ids = self.reader.read_intarray(chunk_size/4-2)
                continue
            if chunk_type < self.CHUNK_XML_FIRST or chunk_type > self.CHUNK_XML_LAST:
                raise Exception("Invalid chunk type ("+chunk_type+").")

            # Fake START_DOCUMENT event.
            if chunk_type == self.CHUNK_XML_START_TAG and event == -1:
                self.m_event=self.START_DOCUMENT
                break


            # Common header.
            self.reader.skip_int();
            line_number = self.reader.read_int()
            self.reader.skip_int();
            if chunk_type == self.CHUNK_XML_START_NAMESPACE or chunk_type == self.CHUNK_XML_END_NAMESPACE:

                    if chunk_type == self.CHUNK_XML_START_NAMESPACE:
                        prefix = self.reader.read_int()
                        uri = self.reader.read_int()
                        self.namespaces.push(prefix, uri)
                    else:
                        #/ * prefix * /
                        self.reader.read_int()
                        #/ * uri * /
                        self.reader.read_int()
                        self.namespaces.pop()
                    continue

            self.linenumber = line_number
            if chunk_type == self.CHUNK_XML_START_TAG:
                self.namespaceUri = self.reader.read_int()
                self.name = self.reader.read_int()
                #/ *flags? * /
                self.reader.skip_int()
                attributeCount = self.reader.read_int()
                self.idAttribute = (attributeCount >> 16) - 1
                attributeCount &= 0xFFFF
                self.classAttribute = self.reader.read_int()
                self.styleAttribute = (self.classAttribute >> 16) - 1
                self.classAttribute = (self.classAttribute & 0xFFFF) - 1
                self.attributes = self.reader.read_intarray(attributeCount * self.ATTRIBUTE_LENGHT)
                for i in range(self.ATTRIBUTE_IX_VALUE_TYPE, len(self.attributes), self.ATTRIBUTE_LENGHT):
                    self.attributes[i] = (self.attributes[i] >>24)
                self.namespaces.increase_depth()
                self.m_event = self.START_TAG
                break

            if chunk_type == self.CHUNK_XML_END_TAG:
                self.namespaceUri = self.reader.read_int()
                self.name = self.reader.read_int()
                self.m_event = self.END_TAG
                self.decrease_depth = True
                break

            if chunk_type == self.CHUNK_XML_TEXT:
                self.name = self.reader.read_int()
                self.reader.read_int()
                self.reader.read_int()
                self.m_event = self.TEXT
                break


    def reset_eventinfo(self):
        self.m_event = -1
        self.line_number = -1
        self.name = -1

    def get_prefix(self):
        prefix = self.namespaces.findPrefix(self.namespaceUri)
        return self.strings.getString(prefix)

    def get_namespace_prefix(self, pos):
        prefix = self.namespaces.getPrefix(pos)
        return self.strings.getString(prefix)

    def get_text(self):
        if self.name == -1 or self.m_event != self.TEXT:
            return null
        return self.strings.getString(self.name)

    def get_name(self):
        if self.name == -1 or (self.m_event != self.START_TAG and self.m_event != self.END_TAG):
            return None
        #printf(self.name)
        return self.strings.getString(self.name)

    def get_namespace_count(self, depth):
        return self.namespaces.getAccumulatedCount(depth)

    def get_depth(self):
        return self.namespaces.get_depth()-1

    def get_namespace_uri(self, pos):
        uri = self.namespaces.getUri(pos)
        self.strings.getString(uri)

    def getAttributeCount(self):
        return len(self.attributes) / self.ATTRIBUTE_LENGHT

    def getAttributeName(self, i):
        offset = self.getAttributeOffset(i)
        name = self.attributes[offset + self.ATTRIBUTE_IX_NAME]
        return self.strings.getString(name)

    def getAttributeValue(self, i):
        offset = self.getAttributeOffset(i)
        valueType = self.m_attributes[offset + self.ATTRIBUTE_IX_VALUE_TYPE]
        if valueType == 3:
            valueString = self.m_attributes[offset + self.ATTRIBUTE_IX_VALUE_STRING]
            return self.getString(valueString)
        return ""

    def getAttributeOffset(self, i):
        return i * 5

    def get_attribute_prefix(self,i):
        offest = self.getAttributeOffset(i)
        uri = self.attributes[offest + self.ATTRIBUTE_IX_NAMESPACE_URI]
        prefix = self.namespaces.findPrefix(uri)
        if prefix == -1:
            return ""
        return self.strings.getString(prefix)

    def get_attribute_type(self,i):
        offset = self.getAttributeOffset(i)
        return self.attributes[offset + self.ATTRIBUTE_IX_VALUE_TYPE]

    def get_attribute_data(self,i):
        offset = self.getAttributeOffset(i)
        return self.attributes[offset + self.ATTRIBUTE_IX_VALUE_DATA]

    def get_attribute_value(self,i):
        offset = self.getAttributeOffset(i)
        type = self.attributes[offset + self.ATTRIBUTE_IX_VALUE_TYPE]
        if type == 3: #TypedValue.TYPE_STRING
            value_str = self.attributes[offset + self.ATTRIBUTE_IX_VALUE_STRING]
            return self.strings.getString(value_str)
        #value_data = self.attributes[offset + self.ATTRIBUTE_IX_VALUE_DATA]
        return ""

class APK:
    indentStep = "	"
    FRACTION_UNITS = ["%", "%p", "", "", "", "", "", ""]
    RADIX_MULTS = [0.00390625, 3.051758E-005, 1.192093E-007, 4.656613E-010]
    DIMENSION_UNITS = ["px", "dip", "sp", "pt", "in", "mm", "", ""]
    AndroidManifest = ""
    Parse_Flag = False 

    def __init__(self, xmlstr):
        self.xml = AXmlResourceParser(xmlstr)
        self.package = 'www.sbfeng.cn.unknown'
        self.version = '1.0'
        self.AndroidManifest = ""

    def parse_androidxml(self):
        indent = ""
        while True:
            node = self.xml.next()
            if node == self.xml.ERROR:
                break
            if node == self.xml.END_DOCUMENT:
                break
            if node == self.xml.START_DOCUMENT:
                self.AndroidManifest += printf('''<?xml version="1.0" encoding="utf-8"?>''')
                continue
            if node == self.xml.START_TAG:
                self.AndroidManifest += printf("%s<%s%s" % (indent,self.get_namespace_prefix(self.xml.get_prefix()), self.xml.get_name()))
                indent += self.indentStep

                namespaceCountBefore = self.xml.get_namespace_count(self.xml.get_depth() - 1)
                namespaceCount = self.xml.get_namespace_count(self.xml.get_depth())
                for i in range(namespaceCountBefore,namespaceCount,1):
                    self.AndroidManifest += printf("%sxmlns:%s=\"%s\""%(indent,
                          self.xml.get_namespace_prefix(i),self.xml.get_namespace_uri(i)))

                for i in range(0,int(self.xml.getAttributeCount()),1):
                    self.AndroidManifest += printf('''%s%s%s="%s"''' % (indent,
                                self.get_namespace_prefix(self.xml.get_attribute_prefix(i)),
                                self.xml.getAttributeName(i), self.get_sttribute_value(self.xml, i)))

                self.AndroidManifest += printf("%s>" % indent);
                continue
            if node == self.xml.END_TAG:
                indent = indent[:len(indent) - len(self.indentStep)]
                self.AndroidManifest += printf("%s</%s%s>" % (indent, self.get_namespace_prefix(self.xml.get_prefix()),self.xml.get_name()))
                continue
            if node == self.xml.TEXT:
                self.AndroidManifest += printf("%s%s" % (indent, self.xml.get_text()))
                continue

    def get_namespace_prefix(self, prefix):
        if prefix == None or len(prefix) == 0:
            return ""
        return prefix+":"

    def get_package(self, id):
        if id>>24 == 1:
            return "android:"
        return ""

    def get_sttribute_value(self,axml,i):
        type = axml.get_attribute_type(i)
        data = axml.get_attribute_data(i)
        TValue = TypeValue.TypeValue()
        if type == TValue.TYPE_STRING:
            return axml.get_attribute_value(i)
        if type == TValue.TYPE_ATTRIBUTE:
            return "?%s%08X" % (self.get_package(data), data)
        if type == TValue.TYPE_REFERENCE:
            return "@%s%08X" % (self.get_package(data), data)
        if type == TValue.TYPE_FLOAT:
            return str(float(data))
        if type == TValue.TYPE_INT_HEX:
            return "0x%08X" % data
        if type == TValue.TYPE_INT_BOOLEAN:
            if data != 0:
                return "true"
            else:
                return "false"
        if type == TValue.TYPE_DIMENSION:
            return str(self.complexToFloat(data) + self.DIMENSION_UNITS[data & TValue.COMPLEX_UNIT_MASK])
        if type == TValue.TYPE_FRACTION:
            return Float.toString(self.complexToFloat(data)) + self.FRACTION_UNITS[data & TValue.COMPLEX_UNIT_MASK]
        if type >= TValue.TYPE_FIRST_COLOR_INT and type <= TValue.TYPE_LAST_COLOR_INT:
            return "#%08X"% data
        if type >= TValue.TYPE_FIRST_INT and type <= TValue.TYPE_LAST_INT:
            return str(data)
        return "<0x%X, type 0x%02X>" % (data, type)

    def complexToFloat(self,complex):
        return (float)(complex & 0xFFFFFF00) * self.RADIX_MULTS[(complex >> 4) & 3]

    def unpack(self):
        pass

    @staticmethod
    def pack(self, path):
        pass
    def reserve_manifest(self):
        flag = False
        for line in self.AndroidManifest.split("\n"):
            line = line.strip()
            if flag:
                print(line)
            if 'package=' == line[:len("package=")]:
                self.package = line[len("package="):]
                if len(self.package) < 2:
                    flag = True
                
            if 'android:versionName=' == line[:len("android:versionName=")]:
                self.version = line[len("android:versionName="):]
                
    def getpackage(self):
        if not self.Parse_Flag:
            self.reserve_manifest()
        return self.package
    def getversion(self):
        if not self.Parse_Flag:
            self.reserve_manifest()
        return self.version


if __name__ == '__main__':
    global fw
    fw = open("zachary.xml","w")
    zipFile = zipfile.ZipFile('cmb.pb.1702231742.apk')
    data = zipFile.read('AndroidManifest.xml')
    apk = APK(data)
    apk.parse_androidxml()
    print(apk.getpackage())
    print(apk.getversion())
    fw.close()
