def domath(type, first_value, second_value):
    if type == "a" or type == "add":
        result = first_value + second_value
        return result
    if type == "s" or type == "sub" or type == "subtract":
        result = first_value - second_value
        return result
    if type == "m" or type == "mult" or type == "multiply":
        result = first_value * second_value
        return result
    if type == "d" or type == "div" or type == "divide":
        result = first_value / second_value
        return result