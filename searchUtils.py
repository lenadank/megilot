import urllib.request as uli
import re

# for testing and debugging.
# text_url is a url consisting of plain text
# html_url is a url constisting of an html page
text_url = 'https://ia800908.us.archive.org/6/items/alicesadventures19033gut/19033-8.txt'
html_url = 'http://mdn.github.io/beginner-html-site-styled/'

# Takes txt in url and transforms the text to a one line string.
# url must be a string
def oneline_format(url):

    # Read row text from url in form of bytes.
    txt = uli.urlopen(url).read()

    # Decode bytes to string.
    # TO-DO add try-except block for text encoded in different standards (utf-8 for example)
    txt = txt.decode('iso-8859-1')

    #Strip text from white spaces
    #txt_list = txt.splitlines()
    #txt = ''.join(txt_list)

    #delete escape characters
    #escapes = ''.join([chr(char) for char in range(1, 32)])
    #escapes = {}
    #txt = txt.translate(escapes)

    return txt



def search(text, first, last, window_l, window_r):
    results=[]
    first_indexes= [m.start() for m in re.finditer(first, text, re.I)] #list of all occurances of 'first' in text
    for f_index in first_indexes:
        x = min(f_index+window_l-len(last)-1, len(text)-len(last)-1) #min index to start searching for 'last'
        y = min(f_index+window_r-len(last), len(text)-len(last)) #max index to search for 'last'
        cur_results = []
        for j in range(x,y):
            cur_text = text[j:j+len(last)]
            if cur_text.lower() == last.lower():
                cur_results.append(text[f_index:j+len(last)])
        if len(cur_results)>0:
            results.append(cur_results)
                #print("start at:"+str(f_index)+":")
                #print(text[f_index:j+len(last)]+"\n")
    return results

#song = "Let it go, let it go can't hold it back anymore! Let it go, let it go turn away and slam the doore. I don't let what they are going to say let the storm ragere"
#search(oneline_format(text_url),'let','re',1,50)