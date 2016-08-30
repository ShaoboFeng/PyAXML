#encoding=utf8


class NamespaceStack:
    m_data = []
    m_dataLength = 0
    m_count = 0
    m_depth = 0

    def __init__(self):
        self.m_data = [0 for i in range(32)]

    def reset(self):
        self.m_dataLength = 0
        self.m_count = 0
        self.m_depth = 0

    def getTotalCount(self):
        return self.m_count

    def get_currentcount(self):
        if self.m_dataLength == 0:
            return 0
        offset = self.m_dataLength - 1
        return self.m_data[offset]

    def getAccumulatedCount(self,depth):
        if self.m_dataLength == 0 or depth < 0:
            return 0
        if depth > self.m_depth:
            depth = self.m_depth
        accumulatedCount = 0
        offset = 0
        while depth > 0:
            count = self.m_data[offset]
            accumulatedCount += count
            offset += (2 + count * 2)
            depth -= 1
        return accumulatedCount

    def push(self, prefix, uri):
        if self.m_depth == 0:
            self.increaseDepth()

        self.ensureDataCapacity(2)
        offset = self.m_dataLength - 1
        count = self.m_data[offset]
        self.m_data[offset - 1 - count * 2] = count + 1
        self.m_data[offset] = prefix
        self.m_data[offset + 1] = uri
        self.m_data[offset + 2] = count + 1
        self.m_dataLength += 2
        self.m_count += 1

    def pop(self,prefix,uri):
        if self.m_dataLength == 0:
            return False

        offset = self.m_dataLength - 1
        count = self.m_data[offset]
        o = offset - 2
        for i in range(count):

            if self.m_data[o] != prefix or self.m_data[o + 1] != uri:
                continue
            count -= 1
            if i == 0:
                self.m_data[o] = count
                o -= (1 + count * 2)
                self.m_data[o] = count
            else:
                self.m_data[offset] = count
                offset -= (1 + 2 + count * 2)
                self.m_data[offset] = count
                self.m_data[o:self.m_dataLength-o] = self.m_data[o+2:self.m_dataLength-(o+2)]
                self.m_dataLength -= 2
                self.m_count -= 1
                return True
            o -= 2
        return False

    def pop(self):
        if self.m_dataLength == 0:
            return False
        offset = self.m_dataLength - 1
        count = self.m_data[offset]
        if count == 0:
            return False
        count -= 1
        offset -= 2
        self.m_data[offset] = count
        offset -= (1 + count * 2)
        self.m_data[offset] = count
        self.m_dataLength -= 2
        self.m_count -= 1
        return True

    def getPrefix(self,index):
        return self.get(index, True)

    def getUri(self,index):
        return self.get(index, False)

    def findPrefix(self,uri):
        return self.find(uri, False)

    def findUri(self,prefix):
        return self.find(prefix, True)

    def get_depth(self):
        return self.m_depth

    def increase_depth(self):
        self.ensureDataCapacity(2)
        offset = self.m_dataLength
        self.m_data[offset] = 0
        self.m_data[offset + 1] = 0
        self.m_dataLength += 2
        self.m_depth += 1

    def decreaseDepth(self):
        if (self.m_dataLength == 0) :
            return;
        offset = self.m_dataLength - 1
        count = self.m_data[offset]
        if ((offset - 1 - count * 2) == 0):
            return
        self.m_dataLength -= 2 + count * 2
        self.m_count -= count
        self.m_depth -= 1

    def ensureDataCapacity(self, capacity):
        available = len(self.m_data)- self.m_dataLength
        if available > capacity:
            return
        newLength = (self.m_data.length + available) * 2
        newData = [0 for i in range(newLength)]
        newData[0:self.m_dataLength] = self.m_data[0:self.m_dataLength]
        self.m_data = newData

    def find(self, prefixOrUri, prefix):
        if self.m_dataLength == 0:
            return -1
        offset = self.m_dataLength - 1
        i = self.m_depth
        while i> 0:
            count = self.m_data[offset]
            offset -= 2;
            while count>0:
                if (prefix):
                    if (self.m_data[offset] == prefixOrUri):
                        return self.m_data[offset + 1]
                else:
                    if (self.m_data[offset + 1] == prefixOrUri):
                        return self.m_data[offset];
                offset -= 2
                count -= 1
            i -= 1
        return -1


    def get(self, index, prefix):
        if self.m_dataLength == 0 or index < 0:
            return -1
        offset = 0
        i = self.m_depth
        while i > 0:
            count = self.m_data[offset];
            if (index >= count):
                index -= count;
                offset += (2+count * 2)
                i -= 1
                continue
            offset += (1 + index * 2);
            if not prefix:
                offset += 1
            return self.m_data[offset]
        return -1
