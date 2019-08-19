from flask import Flask, url_for, request, render_template
import data_manager


app = Flask(__name__)


@app.route('/')
def index():
    questions = data_manager.get_all_data('question')
    return render_template('list.html',
                           questions=questions)


if __name__ == '__main__':
    app.run(
        port=8000,
        debug=False,
    )