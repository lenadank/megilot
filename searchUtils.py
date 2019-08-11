import re
import requests

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
        txt = format_txt(txt)
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

def search_txt(texts, letters_list, window_l, window_r):
    results=[]
    print(letters_list)
    first=letters_list[0]
    last=letters_list[1]
    text=texts[0]
    first_indexes= [m.start() for m in re.finditer(first, text, re.I)] #list of all occurances of 'first' in text
    for f_index in first_indexes:
        x = min(f_index+window_l-len(last)-1, len(text)-len(last)-1) #min index to start searching for 'last'
        y = min(f_index+window_r-len(last), len(text)-len(last)) #max index to search for 'last'
        cur_results = []
        for j in range(x,y):
            cur_text = texts[0][j:j+len(last)]
            if cur_text.lower() == last.lower():
                cur_results.append(text[f_index:j+len(last)])
        if len(cur_results)>0:
            results.append(cur_results)
                #print("start at:"+str(f_index)+":")
                #print(text[f_index:j+len(last)]+"\n")
    return results

#song = "Let it go, let it go can't hold it back anymore! Let it go, let it go turn away and slam the doore. I don't let what they are going to say let the storm ragere"
#search(oneline_format(text_url),'let','re',1,50)