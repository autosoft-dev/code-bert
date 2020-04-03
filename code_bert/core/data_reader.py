from tokenize import INDENT, DEDENT, ENCODING, ENDMARKER, STRING, NEWLINE, tokenize
from io import BytesIO

from dpu_utils.codeutils.identifiersplitting import split_identifier_into_parts

FOREIGN_CHARS = 10000

spl_tokens = {INDENT: "indent",
              DEDENT: "dedent",
              ENCODING: None,
              ENDMARKER: None,
              NEWLINE: "<newline>",
              FOREIGN_CHARS: "foreignchars"
              }

def_tok = "def"


def _is_foreign_char(tok):
    try:
        tok.encode('ascii')
        return False
    except UnicodeEncodeError:
        return True


def _tokenize_code_string(code_string: str):
    try:
        return tokenize(BytesIO(code_string.encode('utf-8')).readline)
    except IndentationError:
        return None


def process_string_tokes(tok, is_docstr=False):
    buffer = []
    lines = tok.split("\n")
    if is_docstr:
        n = len(lines) if len(lines) <= 2 else 2  # we do not consider more than 4 lines of docstring
    else:
        n = len(lines)
    tripple_quote = '"""'
    # started_with_tripple_quote = False

    for line in lines[:n]:
        toks = line.lstrip().rstrip().split(" ")
        # tripple_quote = '"""' if toks[0].startswith('"""') else "'''"
        if (toks[0].startswith('"""') or toks[0].startswith("'''")) and len(toks) > 1:
            # started_with_tripple_quote = True
            toks = toks[1:]
            t = [tripple_quote] + toks
            toks = t
        # else:
        #     if (toks[0].startswith('"""') or toks[0].startswith("'''")) and len(toks) == 1:
        #         started_with_tripple_quote = True
        for idx, t in enumerate(toks):
            if idx > 50:
                break
            buffer.append(t.rstrip().lstrip().lower())

        ####################
        # Not treating the new lines inside STRING type tokens
        # @TODO - Verify this approach
        ####################
        # s.append(spl_tokens[NEWLINE].lower())
    # if s[-1] != spl_tokens[NEWLINE]:
    #     s.pop()
    
    if len(buffer) > 128:
        buffer = buffer[:128]
    if len(" ".join(buffer)) > 200:
        buffer = (" ".join(buffer))[:200].split()
    
    if buffer[0].lstrip().rstrip().startswith('"""') and buffer[-1].lstrip().rstrip() != '"""':
        buffer.append('"""')
    elif buffer[0].lstrip().rstrip().startswith("'''") and buffer[-1].lstrip().rstrip() != "'''":
        buffer.append("'''")
    elif buffer[0].lstrip().rstrip().startswith('b"""') and buffer[-1].lstrip().rstrip() != '"""':
        buffer.append('"""')
    elif buffer[0].lstrip().rstrip().startswith("b'''") and buffer[-1].lstrip().rstrip() != "'''":
        buffer.append("'''")

    return buffer


def divide_code_in_logical_lines(s):
    logical_lines = []
    substring_arr = []
    next_token_is_indent = False
    for idx, tok in enumerate(s):
        if next_token_is_indent:
            tok = tok if not _is_foreign_char(tok) else spl_tokens[FOREIGN_CHARS].lower()
            substring_arr.append(tok)
            if len(" ".join(substring_arr).split()) > 128:
                substring_arr = substring_arr[:128]
            res_str = " ".join(substring_arr)
            # res_str = res_str.replace('"""', "")
            res_str = res_str.rstrip().lstrip()
            logical_lines.append(res_str)
            substring_arr = []
            next_token_is_indent = False
            continue
        if tok == spl_tokens[NEWLINE].lower():
            if len(substring_arr) > 128:  # For the position embedding later
                substring_arr = substring_arr[:128]

            if (idx+1) < len(s) and s[idx+1] == spl_tokens[INDENT].lower():
                next_token_is_indent = True
                continue
            if len(" ".join(substring_arr).split()) > 128:
                substring_arr = substring_arr[:128]
            res_str = " ".join(substring_arr)
            # res_str = res_str.replace('"""', "")
            res_str = res_str.rstrip().lstrip()
            logical_lines.append(res_str)
            substring_arr = []
        else:
            tok = tok if not _is_foreign_char(tok) else spl_tokens[FOREIGN_CHARS].lower()
            substring_arr.append(tok)
    
    if substring_arr:
        all_dedents = True
        for t in substring_arr:
            if t != spl_tokens[DEDENT].lower():
                all_dedents = False
        if len(" ".join(substring_arr).split()) > 128:
                substring_arr = substring_arr[:128]
        last_part = " ".join(substring_arr)
        if all_dedents:
            logical_lines[-1] = logical_lines[-1] + " " + last_part
        else:
            logical_lines.append(last_part.lstrip().rstrip())
    
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
                    if (tok.startswith('"""') or  tok.startswith("'''")) and prev_tok == spl_tokens[INDENT] and toknum == STRING and def_tok_seen:
                        # It is most likely a docstring.
                        docstr = process_string_tokes(tok, is_docstr=True)
                        s.extend(docstr)
                        prev_tok = tok
                        def_tok_seen = False
                        continue
                    else:
                        prev_tok = tok
                    if tok != spl_tokens[INDENT] and  tok != spl_tokens[DEDENT] and tok != spl_tokens[NEWLINE]:
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
        except Exception as e:
            print(e)
            return None
    return None
