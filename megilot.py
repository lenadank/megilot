from flask import Flask, render_template, request, redirect, url_for
app = Flask(__name__)

@app.route('/')
def mainPage():
    return render_template('index.html')

@app.route('/results',methods=['POST'])
def searchResult():
    first_let = request.form['first-letters']
    last_let = request.form['last-letters']
    text_len = request.form['text-length']
    url = request.form['text-url']
    return render_template('results.html', title='Search Results', header ='תוצאות חיפוש',first_letters=first_let, last_letters=last_let, text_length=text_len, text_url = url)

if __name__=='__main__':
    app.run(debug=True)