#encoding=utf8
from Utils import Utils


class StringBlock:
    string_offsets = None
    strings = None
    style_offsets = None
    styles = None

    CHUNK_TYPE = 0x001C0001

    @staticmethod
    def read(reader):
        Utils.check_type(reader, StringBlock.CHUNK_TYPE)
        chunk_size = reader.read_int()
        string_count = reader.read_int()
        style_offset_count = reader.read_int()
        reader.skip_int()
        strings_offset = reader.read_int()
        styles_offset = reader.read_int()
        block = StringBlock()
        block.string_offsets = reader.read_intarray(string_count)
        if style_offset_count != 0:
            block.style_offsets = reader.read_intarray(style_offset_count)
        if styles_offset == 0:
            size = chunk_size
        else:
            size = styles_offset
        size -= strings_offset
        if (size % 4) != 0:
            raise Exception("String data size is not multiple of 4 ("+size+").")
        block.strings = reader.read_intarray(int(size / 4))

        if styles_offset != 0:
            size=chunk_size-styles_offset
            if (size % 4) != 0:
                raise Exception("Style data size is not multiple of 4 ("+size+").")
            block.styles = reader.readIntArray(size / 4)
        return block

    #Returns raw string(without any styling information) at specified index.
    def getString(self,index):
        if index < 0 or not self.string_offsets or index >= len(self.string_offsets):
            return None
        offset = self.string_offsets[index]
        length = self.get_short(self.strings, offset)
        #print(length)
        result = ""
        while length > 0:
            offset += 2
            result += chr(self.get_short(self.strings, offset))
            length -= 1
        return result

    def get_short(self, intarray, offset):
        value = intarray[int(offset/4)]
        if (offset%4)/2 == 0:
            return value & 0xFFFF
        else:
            return value >> 16
