from flask import Flask, render_template, request, jsonify
from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, SubmitField
from wtforms.validators import DataRequired, NumberRange
from ..search import PaperSearch
from ..analysis import PaperAnalyzer
import json

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'  # Change this in production
app.config['DEBUG'] = True  # Enable debug mode for development
app.config['TEMPLATES_AUTO_RELOAD'] = True  # Enable template auto-reload

class SearchForm(FlaskForm):
    query = StringField('Search Query', validators=[DataRequired()])
    max_results = IntegerField('Maximum Results', default=5, 
                             validators=[NumberRange(min=1, max=20)])
    submit = SubmitField('Search')

@app.route('/', methods=['GET', 'POST'])
def index():
    form = SearchForm()
    results = []
    error = None
    
    if form.validate_on_submit():
        try:
            search_engine = PaperSearch()
            results = search_engine.search(form.query.data, form.max_results.data)
            if not results:
                error = "No results found for your query."
        except Exception as e:
            error = str(e)
            results = []  # Clear any partial results if there was an error
    
    return render_template('index.html', form=form, results=results, error=error)

@app.route('/api/search', methods=['POST'])
def api_search():
    try:
        data = request.get_json()
        query = data.get('query')
        max_results = data.get('max_results', 5)
        
        if not query:
            return jsonify({'error': 'Query is required'}), 400
            
        search_engine = PaperSearch()
        results = search_engine.search(query, max_results)
        
        return jsonify({'results': results})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/analyze', methods=['POST'])
def api_analyze():
    try:
        data = request.get_json()
        paper_id = data.get('paper_id')
        
        if not paper_id:
            return jsonify({'error': 'Paper ID is required'}), 400
            
        analyzer = PaperAnalyzer()
        analysis = analyzer.analyze(paper_id)
        
        if 'error' in analysis:
            return jsonify({'error': analysis['error']}), 500
            
        return jsonify(analysis)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True) 