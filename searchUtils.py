import urllib.request as uli

#for testing and debugging. 
#text_url is a url consisting of plain text
#html_url is a url constisting of an html page
text_url = 'https://ia800908.us.archive.org/6/items/alicesadventures19033gut/19033-8.txt'
html_url = 'http://mdn.github.io/beginner-html-site-styled/'

#Takes txt in url and transforms the text to a one line string.
#url must be a string
def oneline_format(url):

    #Read row text from url in form of bytes.
    txt = uli.urlopen(url).read()

    #Decode bytes to string.
    #TO-DO add try-except block for text encoded in different standards (utf-8 for example)
    txt = txt.decode('iso-8859-1')

    #Strip text from white spaces
    txt_list = txt.splitlines()
    txt = ''.join(txt_list)

    #delete escape characters
    escapes = ''.join([chr(char) for char in range(1, 32)])
    txt = txt.translate(escapes)
    return txt



