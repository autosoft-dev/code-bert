from tokenize import INDENT, DEDENT, ENCODING, ENDMARKER, STRING, NEWLINE, tokenize
from io import BytesIO

from dpu_utils.codeutils.identifiersplitting import split_identifier_into_parts

spl_tokens = {INDENT: "__INDENT__",
              DEDENT: "__DEDENT__",
              ENCODING: None,
              ENDMARKER: None,
              NEWLINE: "__NEWLINE__"}

def_tok = "def"


def _tokenize_code_string(code_string: str):
    try:
        return tokenize(BytesIO(code_string.encode('utf-8')).readline)
    except IndentationError:
        return None


def process_string_tokes(tok, is_docstr=False):
    s = []
    lines = tok.split("\n")
    if is_docstr:
        n = len(lines) if len(lines) <= 2 else 2  # we do not consider more than 4 lines of docstring
    else:
        n = len(lines)
    for line in lines[:n]:
        toks = line.lstrip().rstrip().split(" ")
        if toks[0].startswith('"""'):
            toks = toks[1:]
            t = ['"""'] + toks
            toks = t
        for t in toks:
            s.append(t.rstrip().lstrip().lower())
        ####################
        # Not treating the new lines inside STRING type tokens
        # @TODO - Verify this approach
        ####################
        # s.append(spl_tokens[NEWLINE].lower())
    # if s[-1] != spl_tokens[NEWLINE]:
    #     s.pop()
    if s[-1] != '"""':
        s.append('"""')
    return s


def divide_code_in_logical_lines(s):
    logical_lines = []
    substring_arr = []
    for tok in s:
        if tok == spl_tokens[NEWLINE].lower():
            if len(substring_arr) > 256:  # For the position embedding later
                substring_arr = substring_arr[:255]

            logical_lines.append(" ".join(substring_arr))
            substring_arr = []
        else:
            substring_arr.append(tok)
    
    if substring_arr:
        all_dedents = True
        for t in substring_arr:
            if t != spl_tokens[DEDENT].lower():
                all_dedents = False

        last_part = " ".join(substring_arr)
        if all_dedents:
            logical_lines[-1] = logical_lines[-1] + " " + last_part
        else:
            logical_lines.append(last_part)
    
    return logical_lines


def process_code(code_string):
    g = _tokenize_code_string(code_string)

    s = []
    prev_tok = ""
    def_tok_seen = False  # to deal with nested functions

    if g:
        try:
            for toknum, tokval, _, _, _ in g:
                if  toknum != ENCODING and toknum != ENDMARKER:
                    tok = spl_tokens.get(toknum) if spl_tokens.get(toknum) else tokval
                    if tok.startswith('"""') and prev_tok == "__INDENT__" and toknum == STRING and def_tok_seen:
                        # It is most likely a docstring.
                        docstr = process_string_tokes(tok, is_docstr=True)
                        s.extend(docstr)
                        prev_tok = tok
                        def_tok_seen = False
                        continue
                    else:
                        prev_tok = tok
                    if tok != "__INDENT__" and  tok != "__DEDENT__" and tok != "__NEWLINE__":
                        if toknum == STRING:
                            s.extend(process_string_tokes(tok))
                            continue
                        if tok == "def":
                            def_tok_seen = True
                        toks = split_identifier_into_parts(tok)
                        if not toks[0].startswith("#"):  # If the line it self is an in-line comment
                            for t in toks:
                                if not t.startswith("#"):  # If we have in-line comments after the code (like this one)
                                    s.append(t.rstrip().lstrip().lower())
                    else:
                        s.append(tok.rstrip().lstrip().lower())
            
            # return " ".join(s)
            return divide_code_in_logical_lines(s)
        except Exception:
            return None
    return None
