from flask import Flask, render_template, request, redirect, url_for
app = Flask(__name__)

@app.route('/')
def mainPage():
    return render_template('index.html')

@app.route('/results')
def searchResult():
    first_let = request.form['first-letters']
    last_let = request.form['last-letters']
    txt_len = request.form['text-length']
    txt_url = request.form['text-url']

    return render_template('results.html', title='Search Results', header ='תוצאות חיפוש',first_letters=first_let, last_letters=last_let, text_length=txt_len, text_url = txt_url)

if __name__=='__main__':
    app.run(debug=True)