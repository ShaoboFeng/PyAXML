
class Utils:

    @staticmethod
    def check_type(reader, expected_type):
        type = reader.read_int()
        if type != expected_type:
            raise Exception("check type error! actual type is "+hex(type)+
                            " expected type is "+str(hex(expected_type)))