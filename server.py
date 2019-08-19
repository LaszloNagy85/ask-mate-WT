from flask import Flask, url_for, request, render_template, redirect
import data_manager
from datetime import datetime

app = Flask(__name__)


@app.route('/')
def index():
    questions = data_manager.get_all_data('question')
    return render_template('list.html',
                           questions=questions)


@app.route('/add-question', methods=["GET", "POST"])
def add_question():
    QUESTION = 0
    timestamp = datetime.timestamp(datetime.now())

    if request.method == "POST":
        question_data_dict = {}
        questions_list = data_manager.get_all_data('question')

        question_data_dict["id"] = len(questions_list)
        question_data_dict["submission_time"] = timestamp
        question_data_dict["view_number"] = 0
        question_data_dict["vote_number"] = 0
        question_data_dict["title"] = request.form["title"]
        question_data_dict["message"] = request.form["message"]
        question_data_dict["image"] = ">>>PLACEHOLDER_TEXT<<<"
        questions_list.append(question_data_dict)
        data_manager.export_data("test", questions_list, QUESTION)

        return redirect("/")

    return render_template("add-question.html")


if __name__ == '__main__':
    app.run(
        port=8000,
        debug=False,
    )