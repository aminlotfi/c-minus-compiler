import string

buffer = "\n"
pointer = 0
line_no = 0
symbols = "; : , [ ] ( ) { } + - * = < /".split()
legal = list(string.digits) + list(string.ascii_letters) + list(string.whitespace) + symbols
keywords = ["if", "else", "void", "int", "repeat", "break", "until", "return"]
id_list = list()
last_error = 0


def new_line(file, tokens):
    global buffer
    global pointer
    global line_no
    buffer = file.readline()
    pointer = 0
    line_no += 1
    tokens.write(f"\n{line_no}.\t")


def error_handler(token: str, comment: str, line_num):
    global last_error
    if last_error == 0:
        last_error = line_num
        msg = f"{line_num}.\t({token}, {comment}) "
    elif line_num == last_error:
        msg = f"({token}, {comment}) "
    else:
        last_error = line_num
        msg = f"\n{line_num}.\t({token}, {comment}) "
    with open("lexical_errors.txt", "a") as f:
        f.write(msg)


def first_setup():
    with open("symbol_table.txt", "w") as f:
        for i, word in enumerate(keywords, 1):
            id_list.append(word)
            f.write(f"{i}.\t{word}\n")
    with open("tokens.txt", 'w') as f:
        pass
    with open("lexical_errors.txt", 'w') as f:
        pass


def find_id():
    global buffer
    global pointer
    other = symbols + list(string.whitespace)
    identifier = buffer[pointer]
    pointer += 1
    while buffer[pointer] in string.ascii_letters + string.digits:
        identifier += buffer[pointer]
        pointer += 1
    if buffer[pointer] in other:
        if identifier not in id_list:
            id_list.append(identifier)
            with open("symbol_table.txt", 'a') as f:
                f.write(f"{len(id_list)}.\t{identifier}\n")
        return identifier
    else:
        identifier += buffer[pointer]
        pointer += 1
        error_handler(identifier, "Invalid input", line_no)
        return None


def find_num():
    global buffer
    global pointer
    other = symbols + list(string.whitespace)
    try:
        num = buffer[pointer]
        pointer += 1
        while pointer < len(buffer) and buffer[pointer] in string.digits:
            num += buffer[pointer]
            pointer += 1
        if pointer < len(buffer) and buffer[pointer] in other:
            return num
        else:
            num += buffer[pointer]
            pointer += 1
            error_handler(num, "Invalid number", line_no)
            return None
    except IndexError:
        return buffer

def find_comment(file, start_line):
    global buffer
    global pointer
    global line_no
    comment = ""
    with open("tokens.txt", "a") as f:
        try:
            while not (buffer[pointer] == '*' and buffer[pointer + 1] == '/'):
                if buffer[pointer + 1] == '\n':
                    comment += buffer[pointer:]
                    new_line(file, f)
                else:
                    comment += buffer[pointer]
                    pointer += 1
            pointer += 2
        except IndexError:
            error_handler(comment[:7] + "...", "Unclosed comment", start_line)
            return "$"


def get_next_token(file):
    global buffer
    global pointer
    global line_no
    white_except_newline = list(string.whitespace)
    white_except_newline.remove('\n')

    with open("tokens.txt", "a") as f:
        try:
            token = None
            while True:
                if buffer[pointer] in string.ascii_letters:
                    identifier = find_id()
                    if identifier in keywords:
                        token = ("KEYWORD", identifier)
                    elif identifier is not None:
                        token = ("ID", identifier)
                elif buffer[pointer] in string.digits:
                    num = find_num()
                    if num is not None:
                        token = ("NUM", num)
                elif buffer[pointer] in symbols:
                    if buffer[pointer] not in ['=', '/', '*']:
                        token = ("SYMBOL", buffer[pointer])
                        pointer += 1
                    else:
                        try:
                            if buffer[pointer] == '=':
                                if buffer[pointer + 1] == '=':
                                    token = ("SYMBOL", '==')
                                    pointer += 2
                                elif buffer[pointer + 1] in legal:
                                    token = ("SYMBOL", '=')
                                    pointer += 1
                                else:
                                    error_handler(buffer[pointer:pointer + 2], "Invalid input", line_no)
                                    pointer += 2
                            elif buffer[pointer] == '/' and buffer[pointer + 1] != '*':
                                if buffer[pointer + 1] == '/' or buffer[pointer + 1].isspace() or buffer[pointer + 1].isdigit() or (buffer[pointer + 1] in symbols):
                                    error_handler(buffer[pointer:pointer + 1], "Invalid input", line_no)
                                    pointer += 1
                                else:
                                    error_handler(buffer[pointer:pointer + 2], "Invalid input", line_no)
                                    pointer += 2
                            elif buffer[pointer] == '*':
                                if buffer[pointer + 1] == '/':
                                    error_handler("*/", "Unmatched comment", line_no)
                                    pointer += 2
                                elif buffer[pointer + 1] in legal:
                                    token = ("SYMBOL", '*')
                                    pointer += 1
                                else:
                                    error_handler(buffer[pointer:pointer + 2], "Invalid input", line_no)
                                    pointer += 2
                            else:
                                if buffer[pointer + 1] == '/':
                                    new_line(file, f)
                                    continue
                                elif buffer[pointer + 1] == '*':
                                    if find_comment(file, line_no) == "$":
                                        token = "$"
                                        f.write('\n')
                                        break
                                    continue
                                elif buffer[pointer + 1] in legal:
                                    pointer += 1
                                else:
                                    error_handler(buffer[pointer:pointer + 2], "Invalid input", line_no)
                                    pointer += 2
                        except IndexError:
                            token = ("SYMBOL", buffer[pointer])
                            pointer += 1
                elif buffer[pointer] in white_except_newline:
                    pointer += 1
                elif buffer[pointer] == '\n':
                    new_line(file, f)
                else:
                    error_handler(buffer[pointer], "Invalid input", line_no)
                    pointer += 1
                if token:
                    break
            f.write(f"({token[0]}, {token[1]}) ")
            return token
        except IndexError:
            f.write('\n')
            return "$"
