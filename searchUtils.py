import re
import requests
import collections

def remove_nikud(txt):
    """Remove nikud from Hebrew text.

    Args:
        txt (str): a Hebrew string with Nikud.

    Returns:
        str: The text without Nikud.

    """
    nikud = ''.join([chr(char) for char in range(1425, 1480)])
    nikud += ''.join([chr(char) for char in range(1520, 1525)])
    translation = txt.maketrans(nikud, nikud, nikud)
    txt = txt.translate(translation)

    return txt

def decode_txt(url, language='עברית'):
    """Get text from .txt url, decode it and returng it's string representation. 

    Args:
        url (str): A string representing of the url containing the .txt file.
        language (str): language of text in the .txt file. Deafult - "עברית".

    Returns:
        str: the text as a string
    """
    # Read raw text from url in form of bytes.
    request = requests.get(url)

    # decode text according to language
    if(language == 'עברית'):
        request.encoding = 'windows-1255'
        txt = request.text
    else:
        request.encoding = 'UTF-8'
        txt = request.text

    return txt

def texts_from_url(url, language):
    """Get a str list of texts from url representing a repositary with .txt files or a single .txt file.

    Args:
        url (str): string representation of url with a repositary containing .txt files
                   or a single .txt file url.
        language (str): language of texts in repositary/.txt file.

    Returns:
        list: str list of texts obtained from the url. 
    """
    texts = []
    is_txt = re.search(r'\.txt', url)
    if is_txt:
        texts.append(decode_txt(url, language))
    else:
        repositary = requests.get(url).text  # get HTML of repositary
        pattern = re.compile(r'href=".+\.txt"')
        txt_urls = pattern.finditer(repositary)
        for txt_url in txt_urls:
            href = txt_url.group()
            file_name = href[6:len(href)-1]
            file_url = url+"/"+file_name
            texts.append(decode_txt(file_url, language))
    return texts

def create_pattern(text):
    '''Create a regex pattern to search strings inside Hebrew text with nikud. Return a string.'''
    pattern = ''
    for letter in text:
        pattern = pattern+letter+r'[\u0591-\u05c7]*'
    return pattern

def single_string_spans(text, string, nikud=False):
    """Get enumperated spans of apearances of a single string in text. 
    
    Args:
        text (str): text to search string in.
        string (str): string to search in text.
        nikud (bool, optional): Indicates if text is a Hebrew str with nikud. Defaults to False.
    
    Returns:
        list: enumerated spans.
    """

    if nikud:
        p = re.compile(create_pattern(string))
    else:
        p = re.compile(string)
    matches = p.finditer(text)
    res = list(enumerate([match.span() for match in matches]))

    return res

def all_strings_spans(text, strings_list, nikud=False):
    """Get list of lists contating spans of apearances in text for all strings in strings_list.
    
    Args:
        text (str): text to search string in.
        strings_list (list): list of strings to search in text.
        nikud (bool, optional): Indicates if text is a Hebrew str with nikud. Defaults to False.
    
    Returns:
        list: list of lists, each contains enumperated spans of apearances of a single string in text.
            or None if one of the strings wasn't found. (one of the lists is empty).
    """
    result = []
    for string in strings_list:
        cur = single_string_spans(text, string, nikud)
        if cur:
            result.append(cur)
        else: #one of the strings in strings_list wasn't found in text. In that case, there are no results for the search.
            return None
    return result

def search_rec_raw(window_l, window_r, cur_string_spans, all_strings_spans, i):
    """Recursively get indexes of spans inside all_string_spans representing a result in which the i'th string found is at least
        window_l and at most window_r far from the i+1 string in text. ONLY WORKS WHEN at least two strings were specified by user to search.  
    
    Args:
        window_l (int): minimum distance between each string
        window_r (int): maximum distance between each string
        cur_string_spans (list): Note - initiate with all_string_spans[0]. list of spans representing occurances of a single string in the text.
        all_strings_spans (list): list of all lists of spans. Each list representing occurances of a single string.
        i (int): Note - initiate with 0. Represents current string spans list to search matches in. 
    
    Returns:
        list: list of deques. Each deque represents a result. 
            Each deque contains indexes of spans in all_string_spans. 
            deque[i] is index of a span inside all_string_spans[i]. Meaning deque[i] represents a span of 
            the i'th string specified by the user to search. 

    Precondition: 
        all_string_spans: length of all_string_spans is greater then or equal to 2. (2 or more strings were specified by user to find)
                        Length of each list in all_string_spans is greater or equal to 1. (Spans are found in text for each string)
    """
    all_results = []
    for span in cur_string_spans:
        cur_results = []
        cur_span = span[1]
        cur_span_index = span[0]
        if i < len(all_strings_spans)-1:
            # list all possible candidates ( spans within the specified window) of being a match.
            # Candidates are searched inside the next spans list (representing apearances of the 
            # next string the user has specified)
            candidates = list(
                (index, cand_span) for index, cand_span in all_strings_spans[i+1] if cand_span[1] > cur_span[0]+window_l and cand_span[1] < cur_span[0]+window_r)
            # no candidates - result isn't valid. continue.
            if len(candidates) == 0:
                continue

            # find results for current span and then append the current's span index to the beggining
            # of each of the results
            cur_results = search_rec_raw(
                window_l, window_r, candidates, all_strings_spans, i+1)

            # append cur_span_index to the begining of each of the results.
            for j in range(0, len(cur_results)):
                cur_results[j].appendleft(cur_span_index)

        # last spans (reflecting last string given by user) - append it as a deque to cur_results
        else:
            cur_res = collections.deque([cur_span_index])
            cur_results.append(cur_res)

        all_results.extend(cur_results)

    return all_results

def expand_passage_left(start_span, text):
    """Calculate index of start of the expended passege to the left. 
    
    Args:
        start_span (tuple): span representing first string searched.
        text (str): text searched in. 
    
    Returns:
        int: index of expended passege to the left. 
    """
    spaces = 0
    i = start_span[0]
    while spaces < 6 and i > 0:
        if text[i] == ' ':
            spaces += 1
        i -= 1
    return i+1

def expand_passage_right(end_span, text):
    """Calculate index of start of the expended passege to the right. 
    
    Args:
        start_span (tuple): span representing last string searched.
        text (str): text searched in. 
    
    Returns:
        int: index of expended passege to the right. 
    """
    spaces = 0
    i = end_span[1]
    while spaces < 6 and i < len(text):
        if text[i] == ' ':
            spaces += 1
        i += 1
    return i-1

def indices_to_text(indices, all_string_spans_list, text):
    """Convert a single deque of indices of spans representing a result to a list of strings representing the result. 
    
    Args:
        indices (deque): a single tuple representing a result. 
        all_string_spans_list (list): list of lists with spans representing the occurences of  the strings specified by the user. 
        text (str): text searched in. 
    
    Returns:
        list: list of strings representing a result = a single passege from the text
    """
    res = []

    # left expantion
    start_span = all_string_spans_list[0][indices[0]][1]
    left_index = expand_passage_left(start_span, text)
    res.append(text[left_index:start_span[0]])

    # body of passsege
    for i in range(0, len(indices)-1):
        cur_span = all_string_spans_list[i][indices[i]][1]
        next_span = all_string_spans_list[i+1][indices[i+1]][1]
        res.append(text[cur_span[0]:cur_span[1]])
        res.append(text[cur_span[1]:next_span[0]])
    res.append(text[next_span[0]:next_span[1]])

    # right expantion
    end_span = all_string_spans_list[-1][indices[-1]][1]
    right_index = expand_passage_right(end_span, text)
    res.append(text[end_span[1]:right_index])

    return res

def group_by_first_string_raw(spans_indices_results):
    '''Group result from search_rec_raw according to first string. All results starting with the same index are grouped in a list.
    Return a list of lists with deques. 
    '''

    cur_start = spans_indices_results[0][0]
    i = 0
    res = []
    cur_parag = []
    while i < len(spans_indices_results):
        next_result = spans_indices_results[i]
        next_start = next_result[0]
        if cur_start != next_start:
            res.append(cur_parag)
            cur_parag = []
            cur_start = next_start
        cur_parag.append(next_result)
        i += 1
    res.append(cur_parag)
    return res

def get_final_results(result, all_string_spans_list, text):
    """Convert all raw results to lists of strings representing a passage in the text grouped by first string.
    
    Args:
        result (list): raw result retrieved from search_rec_raw() method. 
        all_string_spans_list (list): list of lists with spans representing the occurences of  the strings specified by the user. 
        text (str): text searched in. 
    
    Returns:
        tuple: (list, int) - list of lists representing grouped results. Each group contains lists of strings repesenting a single result.
                the int represents total number of results.  
    """
    num_res = len(result)
    grouped_spans = group_by_first_string_raw(result)
    final_res = []
    for group in grouped_spans:
        paragraphs_group = []
        for indices in group:
            cur_parag = indices_to_text(indices, all_string_spans_list, text)
            paragraphs_group.append(cur_parag)
        final_res.append(paragraphs_group)
    return (final_res, num_res)

def search_txt(texts, strings_list, window_l, window_r):
    """Find passeges in text containing each string from strings_list in an ordered way and with a space of
    minimum window_l charcters and maximum window_r charcters inbetween each string. Return each passage represented as 
    a list of strings, which when combined together form the passege. Currently supports search in Hebrew text only.
    
    Args:
        texts (str): text to search in.
        strings_list (list): strings to search in text.
        window_l (int): minimum  distance between each string.
        window_r (int): maximum distance between each string. 
    
    Returns:
        (list, int): list of lists representing grouped passages. Each group contains lists of strings which when combined
        together form a single passege - a result.
    """

    text = texts[0] #currently supports search in one text only
    no_nikud_txt = remove_nikud(text)
    spans_for_search = all_strings_spans(no_nikud_txt, strings_list)
    spans_nikud = all_strings_spans(text, strings_list, True)
    if spans_for_search: #spans_for_search isn't None -> all strings are found in text and the algorithem can continue. 
        result = search_rec_raw(
            window_l, window_r, spans_for_search[0], spans_for_search, 0)
        if result: #result isn't an empty list -> some results were found. 
            final, num_res = get_final_results(result, spans_nikud, text)
        else: #result is an empty list -> no results for the search. 
            final = None
            num_res = 0
    else: #spans_for_search returned None -> indicates one of the strings wasn't found, thus no results can be found. 
        final = None
        num_res = 0
    return (final, num_res)
