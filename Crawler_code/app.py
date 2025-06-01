from flask import Flask, render_template, request, jsonify
from Final_project_web_crawel import crawl_letterboxd

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/search', methods=['POST'])
def search():
    query = request.form['query']
    try:
        data = crawl_letterboxd(query)
        return jsonify({
            "title": data["title"],
            "year": data["year"],
            "director": data["director"],
            "description": data["description"],
            "poster_url": data["poster"],
            "average_rating": data["average_rating"],
            "rating_distribution": data["rating_distribution"],
            "reviews": [{
                "reviewer": r["reviewer_id"],
                "date": r["review_date"],
                "rating": r["rating"],
                "review_text": r["content"],
                "likes": r["likes"]
            } for r in data["reviews"]]
        })
    except Exception as e:
        return jsonify({'error': str(e)})

if __name__ == '__main__':
    app.run(debug=True)
