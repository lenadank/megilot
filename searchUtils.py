import re
import requests
import collections

# for testing and debugging.
# text_url is a url consisting of plain text
# html_url is a url constisting of an html page
text_url = 'https://ia800908.us.archive.org/6/items/alicesadventures19033gut/19033-8.txt'
html_url = 'http://mdn.github.io/beginner-html-site-styled/'


# Takes txt in url and transforms the text to a one line string.
# url must be a string
def format_txt(txt):

    #Remove hebrew panctuation from txt
    nikud = ''.join([chr(char) for char in range(1425, 1480)])
    nikud +=''.join([chr(char) for char in range(1520, 1525)])
    translation = txt.maketrans(nikud,nikud,nikud)
    txt = txt.translate(translation)

    return txt


    # Takes '.txt' url.
# Returns the formated '.txt' file as a string.
def get_txt(url, language):

    #Read raw text from url in form of bytes.
    request = requests.get(url)

    #decode text according to language
    if(language=='עברית'):
        request.encoding = 'windows-1255'
        txt = request.text
    else:
        request.encoding = 'UTF-8'
        txt = request.text

    return txt

# Takes url for a reposirary with texts and language of texts.
# Returns list of strings. Each string represents one text from the url.
#If '.txt' file is provided instead of a repositary, return list with one item.
def texts_from_url(url, language):
    texts = []
    is_txt = re.search(r'\.txt',url)
    if is_txt:
        texts.append(get_txt(url,language))
    else:
        repositary = requests.get(url).text #returns HTML of repositary
        pattern = re.compile(r'href=".+\.txt"')
        txt_urls = pattern.finditer(repositary)
        for txt_url in txt_urls:
            href = txt_url.group() 
            file_name = href[6:len(href)-1]
            file_url = url+"/"+file_name
            texts.append(get_txt(file_url,language))
    return texts


def create_pattern(text):
    pattern = ''
    for letter in text:
        pattern = pattern+letter+r'[\u0591-\u05c7]*'
    return pattern

# returns enumarated spans of apearances of a string in text.


def single_string_spans(text, string, nikud):
    if nikud:
        p = re.compile(create_pattern(string))
    else:
        p = re.compile(string)
    matches = p.finditer(text)
    res = list(enumerate([match.span() for match in matches]))

    return res

# given a list of strings (strings_list) returns list of single_span for each string.


def all_strings_spans(text, strings_list, nikud):
    result = []
    for string in strings_list:
        cur = single_string_spans(text, string, nikud)
        result.append(cur)
    return result

# pre: len(all_strings_spans)>=2
# len(all_strings_spans[0])>=1
# returns indexs of the appropriate spans as deques. Length of each deque is as the number of strings given by the user.
# cur_string_spans should be the spans list of the first string given by user.
# all_strings_spans should be list of spans of all strings given by the user (made with all_strings_spans method).
# i starts with 0. Indicates current string spans list to search matches in.
# i'th element of each deque represents the index of a span inside the i'th string spans list


def search_rec_raw(window_l, window_r, cur_string_spans, all_strings_spans, i):
    all_results = []
    for span in cur_string_spans:
        cur_results = []
        cur_span = span[1]
        cur_span_index = span[0]
        if i < len(all_strings_spans)-1:
            # list all possible candidates ( spans within the specified window) of being a match. Candidates are searched inside the next spans list (representing apearances of the next string the user has specified)
            candidates = list(
                (index, cand_span) for index, cand_span in all_strings_spans[i+1] if cand_span[1] > cur_span[0]+window_l and cand_span[1] < cur_span[0]+window_r)
            # no candidates - result isn't valid. continue.
            if len(candidates) == 0:
                continue

            # find results for current span and then append the current's span index to the beggining of each of the results
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

# returns index of start of the expended passege to the left.


def expand_passage_left(start_span, text):
    spaces = 0
    i = start_span[0]
    while spaces < 6 and i > 0:
        if text[i] == ' ':
            spaces += 1
        i -= 1
    return i+1

# returns index of end of the extended passege to the right.


def expand_passage_right(end_span, text):
    spaces = 0
    i = end_span[1]
    while spaces < 6 and i < len(text):
        if text[i] == ' ':
            spaces += 1
        i += 1
    return i-1
        
def indices_to_text(indices, all_string_spans_list, text):
    res = []

    #left expantion
    start_span = all_string_spans_list[0][indices[0]][1]
    left_index = expand_passage_left(start_span,text)
    res.append(text[left_index:start_span[0]])

    #body of text
    for i in range(0, len(indices)-1):
        cur_span = all_string_spans_list[i][indices[i]][1]
        next_span = all_string_spans_list[i+1][indices[i+1]][1]
        res.append(text[cur_span[0]:cur_span[1]])
        res.append(text[cur_span[1]:next_span[0]])      
    res.append(text[next_span[0]:next_span[1]])

    #right expantion
    end_span = all_string_spans_list[-1][indices[-1]][1]
    right_index = expand_passage_right(end_span,text)
    res.append(text[end_span[1]:right_index])

    return res

def group_by_first_string_raw(spans_indices_results):
    cur_start = spans_indices_results[0][0]
    i=0
    res = []
    cur_parag=[]
    while i<len(spans_indices_results):
        next_result = spans_indices_results[i]
        next_start = next_result[0]
        if cur_start != next_start:
            res.append(cur_parag)
            cur_parag = []
            cur_start = next_start
        cur_parag.append(next_result)
        i+=1
    res.append(cur_parag)
    return res


def get_final_results(result, all_string_spans_list, text):
    num_res = len(result)
    grouped_spans = group_by_first_string_raw(result)
    final_res=[]
    for group in grouped_spans:
        paragraphs_group=[]
        for indices in group:
            cur_parag = indices_to_text(indices,all_string_spans_list,text)
            paragraphs_group.append(cur_parag)
        final_res.append(paragraphs_group)
    return (final_res, num_res)

    #currently supports search in one text only
def search_txt(texts, letters_list, window_l, window_r):
    text = texts[0]
    no_nikud = format_txt(text)
    spans_for_search = all_strings_spans(no_nikud, letters_list, False)
    spans_nikud = all_strings_spans(text,letters_list, True)
    result = search_rec_raw(window_l, window_r, spans_for_search[0], spans_for_search, 0)
    if result:
        final, num_res = get_final_results(result,spans_nikud,text)
    else:
        final = None
        num_res = 0
    return (final, num_res)