from tokenize import INDENT, DEDENT, ENCODING, ENDMARKER, STRING, NEWLINE, tokenize
from io import BytesIO

from dpu_utils.codeutils.identifiersplitting import split_identifier_into_parts

spl_tokens = {INDENT: "__INDENT__",
              DEDENT: "__DEDENT__",
              ENCODING: None,
              ENDMARKER: None,
              NEWLINE: "__NEWLINE__"}


def _tokenize_code_string(code_string: str):
    return tokenize(BytesIO(code_string.encode('utf-8')).readline)


def process_code(code_string):
    g = _tokenize_code_string(code_string)

    s = []
    prev_tok = ""

    for toknum, tokval, _, _, _ in g:
        if  toknum != ENCODING and toknum != ENDMARKER:
            tok = spl_tokens.get(toknum) if spl_tokens.get(toknum) else tokval
            if tok.startswith('"""') and prev_tok == "__INDENT__" and toknum == STRING:
                # It is most likely a docstring.
                lines = tok.split("\n")
                # n = len(lines) if len(lines) <= 2 else 2  # we do not consider more than 2 lines of docstring
                for line in lines:
                    toks = line.lstrip().rstrip().split(" ")
                    for t in toks:
                        s.append(t.rstrip().lstrip().lower())
                if s[-1] != '"""':
                    s.append('"""')
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
                s.append(tok.rstrip().lstrip().lower())
    
    return " ".join(s)
