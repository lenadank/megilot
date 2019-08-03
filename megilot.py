from flask import Flask, render_template, request, redirect, url_for
app = Flask(__name__)

@app.route('/', methods=['GET','POST'])
def mainPage():
    return render_template('index.html')

@app.route('/results')
def searchResult():
    return render_template('results.html', title='Search Results', header ='תוצאות חיפוש')

if __name__=='__main__':
    app.run(debug=True)