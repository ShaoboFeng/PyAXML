class IntReader:
    m_bigEndian = None
    m_position = None
    m_data = None
    pos = 0

    def __init__(self, big_endian = False, position = 0, data = None):
        self.m_bigEndian = big_endian
        self.m_position = position
        self.m_data = data

    def read_byte(self):
        return self.read_int(1)

    def read_short(self):
        return self.read_int(2)

    def read_int(self, length=4):
        result = 0
        i = length
        if self.m_bigEndian:
            #i = (length-1) * 8
            while i >= 0:
                b = self.m_data[self.m_position]
                if b == -1:
                    oops("error")
                self.m_position += 1
                result |= (b << i)
                i -= 8
        else:
            #length *= 8
            for i in range(length):
                pos = i*8
                if self.m_position >= len(self.m_data):
                    return None
                b = self.m_data[self.m_position]
                self.m_position += 1
                if type(b) == int:
                    result |= (b << pos)
                else:
                    result |= (ord(b) << pos)
                #print(result)
        return result

    def skip(self , bytes):
        self.m_position += bytes

    def skip_int(self):
        self.skip(4)

    def read_intarray(self, length, array=None, offset=0):
        try:
            length = int(length)
        except Exception as e:
            raise e
        if array == None:
            array = []
            for i in range(0,length,1):
                array.append(0)
        while length > 0:
            array[offset] = self.read_int()
            offset += 1
            length -= 1
        return array

    def read_bytearray(self, length):
        array = self.m_data[self.m_position:self.m_position+length]
        self.m_position += length
        return array
