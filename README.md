# About Megilot

This text search engine was developed for the Israel Antiquities Authority to help research the Dead Sea Scrolls fragments.
This is a Flask based web-application that allows searching multiple strings simultaneously in multiple text files. 

## Why search multiple strings?

In some case, when large texts are involved, text searching tools such as "CTRL+F" that allow searching one string only, might not be good enough as they might produces too many search results to be reviewed. If we know of other strings that should appear later in the result, adding these strings to the search might significantly reduce the number of possible results, making a much more efficient search. 

## A real test-case: The [Dead Sea Scrolls](https://en.wikipedia.org/wiki/Dead_Sea_Scrolls)  fragments

In the fragment below, researches have concluded the upper word is “נפלאות”. The lower word is "ל" followed by what seems as a "ו" or “י”. Searching for “נפלאות” alone in the whole bible will produce many results, too many to have a conclusive decision regarding where in the bible does the fragment appear. But adding "ל" as a string that appears approximately 1-50 letters later in the text (a row beneath “נפלאות”) will produce very few results, enough to conclude. 

![Image](https://i.ibb.co/3FNBxBp/2019-11-14-01h32-04-2.png)


'Megilot' allows this:

![image](https://i.ibb.co/ggbjnc2/2019-11-14-02h51-16.png)


## Features:

1. Search in Hebrew text with Nikud is available.
2. Text uploads for search.
3. Search of multiple strings.
4. Search in multiple texts.
5. Advanced search options - adding \[\] allows search of multiple options: wor\[md\] will search both 'worm' and 'word'.  

## Restrictions:

1. Current version allows searching in .txt files only.
2. Search session are restricted to 30 minutes - after 30 minutes users must upload the text files again. 
   
## Authors

* **Anat Gilenson** 
