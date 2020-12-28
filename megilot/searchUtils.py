import re
import requests
import collections
from megilot import app


def strip_strings(strings):
    """Remove leading and tailing whitespace from each of the strings in the list.

    Args:
        strings (list): list of strings.

    Returns:
        list: of string without leading and tailing whitespace.

    """
    res = []
    for s in strings:
        res.append(s.strip("\t|\n"))
    return res


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

def create_sub_pattern_with_nikud(string):
    #create a list of the string splitted by letters or [] with a string inside
    #for exapmle if string is 'he[ll]o', strings=['h','e','[ll],'o']
    strings = []
    p = re.compile('(\[[א-ת]+\])')
    temp_strings = p.split(string)
    for s in temp_strings:
        if '[' in s:
            strings.append(s)
        else:
            strings.extend(list(s))

    # create a pattern from strings. Have zero or more nikud chars after each element (letter or [] with a string inside)
    pattern = ''
    for string in strings:
        pattern = pattern + string + r'[\u0591-\u05c7]*'
    return pattern


def create_pattern(string):
    '''Create a regex pattern to search strings inside Hebrew text with nikud. Return a string.'''
    str_list = string.split("*")
    star = r'(.[\u0591-\u05c7]*){0,3}'
    pattern = star.join([create_sub_pattern_with_nikud(s) for s in str_list])
    return pattern


def build_single_string_regex(string):
    string = string.replace("*",
                            ".{0,3}").replace("?", "\S").replace("]",
                                                                 "]?")  # should be .{0,3}, but because of the hebrew script we switched the location of the dot.
    return string

def single_string_spans(text, string, offset = 0, already_seen=None):
    """Get enumperated spans of apearances of a single string in text. 

    Args:
        text (str): text to search string in.
        string (str): string to search in text.
        nikud (bool, optional): Indicates if text is a Hebrew str with nikud. Defaults to False.

    Returns:
        list: enumerated spans.
    """
    #"[u05d0-u05f2]"
    string = string.replace("*",
                                ".{0,3}").replace("?", "\S").replace("]", "]?")  # should be .{0,3}, but because of the hebrew script we switched the location of the dot.
    p = re.compile(string)
    matches = p.finditer(text)
    def add_offset_to_span(span, offset):
        return (span[0] + offset, span[1] + offset)
    res = [add_offset_to_span(match.span(), offset) for match in matches]
    if already_seen is not None:
        #avoid duplicate spans from overlapping regex search results
        res = [x for x in res if x not in already_seen]
        already_seen.update(res)
    res = list(enumerate(res))
    return res


def all_strings_spans(text, strings_list, spans_from_regex, max_row_len):
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
        spans_for_string = set()
        cur = []
        for span_from_regex in spans_from_regex:
            curr_text = text[span_from_regex: span_from_regex + max_row_len*(len(strings_list) + 1)]
            res_for_span = single_string_spans(curr_text, string, offset=span_from_regex, already_seen=spans_for_string)
            res_for_span = [(x+len(cur), y) for x,y in res_for_span] #fixt enumerations, since pre list always starts from 0
            cur += res_for_span
        if cur:
            result.append(cur)
        else:  # one of the strings in strings_list wasn't found in text. In that case, there are no results for the search.
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


def single_string_search(all_strings_spans, text):
    """Calculate index of start of the expended passege to the left. 

    Args:
        all_strings_spans (list): list of enumerated spans of all accurances of the single string to search in text.
        text (str): text searched in. 

    Returns:
        tuple (list, int): list of groups - each group representing a passage starting with the same word.
                            Each group contains list of string that when joined result in one sentence with the searched string in. 
    """
    result = []
    # only one string to search - meaning only one list in all_string_spans
    enums = all_strings_spans[0]
    for enum in enums:
        span = enum[1]
        cur_res = []
        group_wrapper = []

        # left expantion
        left_index = expand_passage_left(span, text, 12)
        cur_res.append(text[left_index:span[0]])

        # string
        cur_res.append(text[span[0]:span[1]])

        # right expantion
        right_index = expand_passage_right(span, text, 12)
        cur_res.append(text[span[1]:right_index])

        group_wrapper.append(cur_res)
        result.append(group_wrapper)

    return (result, len(result))


def expand_passage_left(start_span, text, num_spaces=6):
    """Calculate index of start of the expended passege to the left. 

    Args:
        start_span (tuple): span representing first string searched.
        text (str): text searched in. 

    Returns:
        int: index of expended passege to the left. 
    """
    spaces = 0
    i = start_span[0]
    while spaces < num_spaces and i > 0:
        if text[i] == ' ':
            spaces += 1
        i -= 1
    return i+1


def expand_passage_right(end_span, text, num_spaces=6):
    """Calculate index of start of the expended passege to the right. 

    Args:
        start_span (tuple): span representing last string searched.
        text (str): text searched in. 

    Returns:
        int: index of expended passege to the right. 
    """
    spaces = 0
    i = end_span[1]
    while spaces < num_spaces and i < len(text):
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


    res_len = sum(len(x) for x in res)
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
    start_indices = []
    for group in grouped_spans:
        paragraphs_group = []
        paragraph_indices = []
        for indices in group:
            cur_parag = indices_to_text(indices, all_string_spans_list, text)
            paragraphs_group.append(cur_parag)
            paragraph_indices.append(all_string_spans_list[0][indices[0]][1][0])
        final_res.append(paragraphs_group)
        start_indices.append(paragraph_indices)
    return (final_res, num_res, start_indices)


def search_txt_regex(texts, strings_list,min_row_len, max_row_len):
    search_offset = 20
    strings_regex = [build_single_string_regex(x) for x in strings_list]
    strings_regex = [f"({x})"  if not x.startswith("(") else x for x in strings_regex]
    regex_for_search = f"(.{{{max(0, min_row_len-search_offset)},{max_row_len}}})".join(strings_regex)
    p = re.compile(regex_for_search)
    all_pages_spans = {}
    num_res = 0
    for text_name, text in texts.items():
        text_clean = text.replace("\n", " ")
        all_start_spans = []
        for match in p.finditer(text_clean):
            all_start_spans.append(match.span(0)[0])
        all_pages_spans[text_name] = all_start_spans
    if all_pages_spans:
        return all_pages_spans
    else:
        return None


def search_txt(texts, strings_list, min_row_len, max_row_len, index=True):
    """Find passeges in text containing each string from strings_list in an ordered way and with a space of
    minimum window_l charcters and maximum window_r charcters inbetween each string. Return each passage represented as 
    a list of strings, which when combined together form the passege. Currently supports search in Hebrew text only.

    Args:
        texts (str): text to search in.
        strings_list (list): strings to search in text.
        min_row_len (int): minimum  distance between each string.
        max_row_len (int): maximum distance between each string.

    Returns:
        (list, int): list of lists representing grouped passages. Each group contains lists of strings which when combined
        together form a single passege - a result.
    """
    spans_from_regex_search_all_pages = search_txt_regex(texts, strings_list, min_row_len, max_row_len)
    if not spans_from_regex_search_all_pages:
        return None
    #if sum(len(x) for x in spans_from_regex_search_all_pages.value()) > 500:
    #    return "too_many_results"
    all_pages = {}
    for text_name, text in texts.items():
        text_clean = text.replace("\n", " ")
        spans_from_regex_search = spans_from_regex_search_all_pages[text_name]
        if len(spans_from_regex_search) == 0:
            continue
        #no_nikud_txt = remove_nikud(text)
        spans_for_search = all_strings_spans(text_clean, strings_list, spans_from_regex_search, max_row_len)
        #spans_nikud = all_strings_spans(text, strings_list)
        # all_strings_spans() returned None -> indicates one of the strings wasn't found, thus no results can be found.
        if  spans_for_search == None:
            continue

        if len(strings_list) == 1:

            final, num_res = single_string_search(spans_for_search, text_clean)
            start_spans = []
            i = 0
            for same_sequence in final:
                start_spans.append([x[1][0] for x in spans_for_search[0][i: i+len(same_sequence)]])
                i += len(same_sequence)
        else:
            result = search_rec_raw(
                min_row_len, max_row_len, spans_for_search[0], spans_for_search, 0)
            # result isn't an empty list -> some results were found.
            if result:
                final, num_res, start_spans = get_final_results(result, spans_for_search, text_clean)
            else:  # result is an empty list -> no results for the search.
                continue
        for s in start_spans:
            for i in range(len(s)):
                line_index = text[:s[i]].count("\n")
                s[i] = line_index
        all_pages[text_name] = (final, num_res, start_spans)

    if all_pages:
        if len(strings_list) != 1:
            return sort_results_by_average_line_length(all_pages)
        else:
            return all_pages
    else:
        return None


def calc_average_line_length_for_single_results(single_res):
    curr_lengths = []
    for i in range(1, len(single_res)-2, 2): # we are not intersted in the last matched line because the length constraints don't apply to it.
        curr_lengths.append(len(single_res[i] + single_res[i + 1]))
    return max(curr_lengths) - min(curr_lengths)

def calc_average_line_length_for_passage(single_passage):
    texts = single_passage[0]
    all_lengths = []
    for text in texts:
        all_lengths.append(calc_average_line_length_for_single_results(text))
    return min(all_lengths)

def sort_results_by_average_line_length(all_pages):
    for text_name in all_pages:
        curr_res = all_pages[text_name]
        zipped = zip(curr_res[0], curr_res[2])
        sorted_zipped = sorted(zipped, key=calc_average_line_length_for_passage)
        sorted_zipped = sort_internally_for_each_passage(sorted_zipped)
        texts, spans = zip(*sorted_zipped)
        all_pages[text_name] = (texts, curr_res[1], spans)
    return all_pages

def sort_internally_for_each_passage(zipped):
    new_zipped = []
    for passage_tuple in zipped:
        zipped_passage = zip(passage_tuple[0], passage_tuple[1])
        sorted_zipped_passage = sorted(zipped_passage, key=lambda x: calc_average_line_length_for_single_results(x[0]))
        texts, spans = zip(*sorted_zipped_passage)
        new_zipped.append((texts, spans))
    return new_zipped