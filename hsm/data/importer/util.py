'''Common utilities for importers.'''

def compute_starts(tokens, sep=u' '):
    '''Compute start positions of tokens, if they were joined by given separator as a single string.'''
    seplen = len(sep)
    starts = []
    next_start = 0
    for token in tokens:
        starts.append(next_start)
        next_start += len(token) + seplen
    return starts
     
def compute_ends(tokens, sep=u' '):
    '''Compute end positions of tokens, if they were joined by given separator as a single string.'''
    ends = []
    if len(tokens) == 0:
        return ends
    else:
        seplen = len(sep)
        next_end = len(tokens[0])
        for token in tokens[1:]:
            ends.append(next_end)
            next_end += seplen + len(token)
        ends.append(next_end)
        return ends
