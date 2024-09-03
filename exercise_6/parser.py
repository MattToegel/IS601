text = "(+ (+ 1 2) (+ (+ 3 F) 5))"

class ParserException(Exception):
    pass

def find_open_parenthesis(text):
    for index, character in enumerate(text):
        if character == '(':
            return text[index + 1:]
    raise ParserException("Unable to find opening parenthesis")

def get_argument(text):
    start_index = None
    for index, character in enumerate(text):
        if character == '(':
            arg, remaining_text = perform_operation(text[index + 1:])
            return arg, remaining_text
        elif character != ' ' and start_index == None:
            start_index = index
        elif (character == ' ' or character == ')') and start_index != None:
            arg = int(text[start_index:index])
            remaining_text = text[index + 1:]
            return arg, remaining_text
    raise ParserException("Unable to get argument")

def perform_operation(text):
    if text[0] == '+':
        arg1, remaining_text = get_argument(text[1:])
        arg2, remaining_text = get_argument(remaining_text)
        return arg1 + arg2, remaining_text
    else:
        raise ParserException("Invalid operation")

perform_operation(find_open_parenthesis("(+ (+ 1 2) (+ (+ 3 F) 5))"))
