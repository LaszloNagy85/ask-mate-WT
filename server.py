from flask import Flask, request, render_template, redirect
import data_manager
from datetime import datetime

app = Flask(__name__)


@app.route('/')
@app.route('/list')
def index():
    sort_by = 'submission_time'
    order_direction = 'desc'
    if 'sort' in request.args:
        sort_by = request.args.get('sort')
    if 'order' in request.args:
        order_direction = request.args.get('order')

    questions = data_manager.get_sorted_data('question', sort_by, order_direction)
    return render_template('list.html',
                           questions=questions,
                           sort_options=['submission_time', 'view_number', 'vote_number', 'title'],
                           sort_titles=['submission time', 'view number', 'vote number', 'title'],
                           )


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


@app.route('/question/view_count/<id>')
def view_count(id):
    HEADER = 0
    questions = data_manager.get_all_data("question")
    for question in questions:
        if str(id) == question["id"]:
            question["view_number"] = str(int(question["view_number"])+1)
            data_manager.export_data("question", questions, HEADER)
    return redirect(f'/question/{id}')


@app.route('/question/<int:id>')
def show_details(id):
    questions = data_manager.get_all_data("question")
    answers = data_manager.get_all_data("answer")
    answers_to_display = []

    for question in questions:
        if str(id) == question["id"]:
            question_to_display = question

    for answer in answers:
        if str(id) == answer["question_id"]:
            answer["submission_time"] = datetime.fromtimestamp(int(answer["submission_time"]))
            answers_to_display.append(answer)

    question_to_display["submission_time"] = datetime.fromtimestamp(int(question_to_display["submission_time"]))

    return render_template("show-details.html",
                           question_to_display=question_to_display,
                           answers_to_display=answers_to_display)


@app.route('/<redirect_id>/vote/<filename>/<data_id>/<vote_type>')
def vote(redirect_id, filename, data_id, vote_type):
    data_manager.vote(filename, data_id, vote_type)
    return redirect(f'/question/{redirect_id}')


if __name__ == '__main__':
    app.run(
        port=5000,
        debug=False,
    )