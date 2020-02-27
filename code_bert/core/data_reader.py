from tokenize import INDENT, DEDENT, ENCODING, ENDMARKER, STRING, NEWLINE, tokenize
from io import BytesIO

from dpu_utils.codeutils.identifiersplitting import split_identifier_into_parts

spl_tokens = {INDENT: "__INDENT__",
              DEDENT: "__DEDENT__",
              ENCODING: None,
              ENDMARKER: None,
              NEWLINE: "__NEWLINE__"}


def _tokenize_code_string(code_string: str):
    try:
        return tokenize(BytesIO(code_string.encode('utf-8')).readline)
    except IndentationError:
        return None


def process_string_tokes(tok):
    s = []
    lines = tok.split("\n")
    n = len(lines) if len(lines) <= 4 else 4  # we do not consider more than 4 lines of docstring
    for line in lines[:n]:
        toks = line.lstrip().rstrip().split(" ")
        if toks[0].startswith('"""'):
            toks = toks[1:]
            t = ['"""'] + toks
            toks = t
        for t in toks:
            s.append(t.rstrip().lstrip().lower())
        s.append(spl_tokens[NEWLINE].lower())
    if s[-1] != spl_tokens[NEWLINE]:
        s.pop()
    if s[-1] != '"""':
        s.append('"""')
    return s


def process_code(code_string):
    g = _tokenize_code_string(code_string)

    s = []
    prev_tok = ""

    if g:
        try:
            for toknum, tokval, _, _, _ in g:
                if  toknum != ENCODING and toknum != ENDMARKER:
                    tok = spl_tokens.get(toknum) if spl_tokens.get(toknum) else tokval
                    if tok.startswith('"""') and prev_tok == "__INDENT__" and toknum == STRING:
                        # It is most likely a docstring.
                        docstr = process_string_tokes(tok)
                        s.extend(docstr)
                        prev_tok = tok
                        continue
                    else:
                        prev_tok = tok
                    if tok != "__INDENT__" and  tok != "__DEDENT__" and tok != "__NEWLINE__":
                        toks = split_identifier_into_parts(tok)
                        if not toks[0].startswith("#"):  # If the line it self is an in-line comment
                            for t in toks:
                                if not t.startswith("#"):  # If we have in-line comments after the code (like this one)
                                    s.append(t.rstrip().lstrip().lower())
                    else:
                        if toknum == STRING:
                            s.extend(process_string_tokes(tok))
                        else:
                            s.append(tok.rstrip().lstrip().lower())
            
            return " ".join(s)
        except Exception:
            return None
    return None
