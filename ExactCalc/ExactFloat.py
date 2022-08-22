class ExactFloat:
    def __init__(self, number):
        self.sign = True if number[0] != '-' else False
        if number[0] == '-' or number[0] == '+':
            number = number[1:]
        number_parts = number.split('.')
        self.decimal = str(int(number_parts[0])) if len(number_parts[0]) else '0'
        aux_fraction = number_parts[1] if len(number_parts) > 1 else '00'
        self.fraction = aux_fraction if len(aux_fraction)>1 else f'{aux_fraction}0'

    def copy(self):
        return(ExactFloat(self.__str__()))

    def __add__(self, obj):
        addend1, addend2, float_len = format_variables(self, obj)
        result = str(addend1 + addend2)
        decimal, fraction, sign = format_result(result, float_len)
        return ExactFloat(f'{sign}{decimal}.{fraction}')

    def __sub__(self, obj):
        minuend, subtrahend, float_len = format_variables(self, obj)
        result = str(minuend - subtrahend)
        decimal, fraction, sign = format_result(result, float_len)
        return ExactFloat(f'{sign}{decimal}.{fraction}')

    def __str__(self):
        symbol = '' if self.sign else '-'
        fraction = str(self.fraction) if len(str(self.fraction)) >= 2 else str(self.fraction) + '0'
        return f'{symbol}{self.decimal}.{fraction}'


def format_variables(var1:ExactFloat, var2:ExactFloat):
    var1_fraction = var1.fraction + ('0' *(len(var1.fraction) - len(var2.fraction)))
    var2_fraction = var2.fraction + ('0' *(len(var2.fraction) - len(var1.fraction)))
    var1_total = int(var1.decimal + var1_fraction)
    var1_total = var1_total if var1.sign else var1_total * -1

    var2_total = int(var2.decimal + var2_fraction)
    var2_total = var2_total if var2.sign else var2_total * -1
    return var1_total, var2_total, len(var1_fraction)

def format_result(result, float_len):
    sign = ''
    if result[0] == '-':
        sign = '-'
        result = result[1:]
    if len(result) <= float_len:
        fraction = ('0' *(float_len - len(result))) + result
        decimal = '0'
    else:
        fraction = result[len(result) - float_len:]
        decimal = result[:len(result) - float_len]
    return decimal, fraction, sign