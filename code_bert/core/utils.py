from typing import List, Optional

from code_bert.exceptions import LimitIsMoreThanLengthError


def combine_logical_lines(logical_lines: List[str], 
                          limit: Optional[int]=None, 
                          replace_mask_with: Optional[str]=None, 
                          times: int=1,
                          mask_token: str='<mask>') -> str:
    """
    Combines the logical lines of code returned by process_code with optionally replacing a token as many times as you want with the mask

    Args:
        logical_lines: A list containing one line at a time from a code snippet
        limit: If you do not want to take the entire code (because of max_position_embedding)
        replace_mask_with: Which token you want to replace the mask with
        times: An integer telling how many times you want that replacement. Default=1
        mask_token: Specify the mask token. Default='<mask>'
    """
    l = len(logical_lines) if not limit else limit
    
    if l > len(logical_lines):
        raise LimitIsMoreThanLengthError(f"Limit {limit} can't be greater than the total length{len(logical_lines)}")

    combined_code = " ".join(logical_lines[:l])
    return combined_code.replace(replace_mask_with, mask_token, times) if replace_mask_with else combined_code
