from flask import Flask, request, render_template, redirect, url_for
import data_manager
import os
from datetime import datetime


app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = "images"
app.config['MAX_CONTENT_LENGTH'] = 5 * 2000 * 1400


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
    if request.method == "POST":
        if 'image-upload' in request.files:
            image = request.files['image-upload']
            if image.filename != '' and data_manager.allowed_file(image.filename):
                image.save(os.path.join(app.config['UPLOAD_FOLDER'], image.filename))
            else:
                image = ''

        questions_list = data_manager.get_all_data('question')
        timestamp = datetime.timestamp(datetime.now())
        question_data_dict = {
            "id": len(questions_list),
            "submission_time": int(timestamp),
            "view_number": 0,
            "vote_number": 0,
            "title": request.form["title"],
            "message": request.form["message"],
            "image": image.filename if image else None,
        }
        questions_list.append(question_data_dict)
        data_manager.export_data("question", questions_list, 'question_header')

        return redirect(url_for('show_details', data_id=question_data_dict['id']))

    return render_template("add-question.html")


@app.route('/question/view_count/<int:data_id>')
def view_count(data_id):
    data_manager.view_count_handling(data_id)
    return redirect(f'/question/{data_id}')


@app.route('/question/<int:data_id>')
def show_details(data_id):
    questions = data_manager.get_all_data("question")
    answers = data_manager.get_all_data("answer")
    answers_to_display = []

    for question in questions:
        if str(data_id) == question["id"]:
            question_to_display = question
    for answer in answers:
        if str(data_id) == answer["question_id"]:
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


@app.route('/question/<data_id>/edit', methods=["GET", "POST"])
def edit_question(data_id):
    questions = data_manager.get_all_data("question")
    if request.method == "POST":
        for question in questions:
            if data_id == question["id"]:
                question["title"] = request.form["title"]
                question["message"] = request.form["message"]
                data_manager.export_data("question", questions, 'question_header')

        return redirect("/")

    return render_template("edit-question.html", questions=questions, data_id=data_id)


@app.route('/question/<data_id>/delete')
def delete_question(data_id):
    questions = data_manager.get_all_data("question")
    answers = data_manager.get_all_data("answer")
    answers_to_remove_index = []

    for question in questions:
        if question["id"] == data_id:
            questions.remove(question)
            data_manager.export_data("question", questions, 'question_header')

    for answer in answers:
        if answer["question_id"] == data_id:
            answers_to_remove_index.append(answers.index(answer))

    for index_number in answers_to_remove_index:
        del answers[index_number]

    data_manager.export_data("answer", answers, 'answer_header')

    return redirect("/")


@app.route('/question/<data_id>/new-answer', methods=["GET", "POST"])
def add_answer(data_id):
    HEADER = 1
    timestamp = datetime.timestamp(datetime.now())

    if request.method == "POST":
        answer_data_dict = {}
        answers_list = data_manager.get_all_data('answer')

        answer_data_dict["id"] = len(answers_list)
        answer_data_dict["submission_time"] = int(timestamp)
        answer_data_dict["vote_number"] = 0
        answer_data_dict["question_id"] = data_id
        answer_data_dict["message"] = request.form["message"]
        answer_data_dict["image"] = ""
        answers_list.append(answer_data_dict)
        data_manager.export_data("answer", answers_list, HEADER)

        return redirect("/")

    return render_template('answer.html', data_id=data_id)


@app.route('/answer/<answer_id>/delete')
def delete_answer(answer_id):
    answers = data_manager.get_all_data("answer")
    for answer in answers:
        if answer["id"] == answer_id:
            del answers[answers.index(answer)]
    data_manager.export_data("answer", answers, 'answer_header')

    return redirect("/")


if __name__ == '__main__':
    app.run(
        port=5000,
        debug=False,
    )