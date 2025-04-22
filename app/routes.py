from app import app
from flask import render_template

@app.route('/wardrobe')
def wardrobe():
    return render_template('wardrobe.html')

@app.route('/outfits')
def outfits():
    return render_template('outfit.html')

@app.route('/analysis')
def analysis():
    return render_template('analysis.html')

@app.route('/social')
def social():
    return render_template('social.html')



# add the rest as needed (outfit, analysis, social)
