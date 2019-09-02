from flask import Flask, request, render_template, redirect, url_for
from datetime import datetime
import data_manager
import os


app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'static/images'
app.config['MAX_CONTENT_LENGTH'] = 5 * 2000 * 1400


@app.route('/')
def route_list():
    sort_by = 'submission_time'
    order_direction = 'desc'
    if 'sort' in request.args:
        sort_by = request.args.get('sort')
    if 'order' in request.args:
        order_direction = request.args.get('order')
    questions = data_manager.get_all_data_sql('question',  sort_by, order_direction, limit_it='LIMIT 5')
    return render_template('list.html',
                           questions=questions,
                           sort_options=['submission_time', 'view_number', 'vote_number', 'title'],
                           sort_titles=['submission time', 'view number', 'vote number', 'title'],
                           sort_by=sort_by,
                           order_direction=order_direction,
                           )


@app.route('/list')
def route_list_all():
    sort_by = 'submission_time'
    order_direction = 'desc'
    if 'sort' in request.args:
        sort_by = request.args.get('sort')
    if 'order' in request.args:
        order_direction = request.args.get('order')
    questions = data_manager.get_all_data_sql('question',  sort_by, order_direction)
    return render_template('list.html',
                           questions=questions,
                           sort_options=['submission_time', 'view_number', 'vote_number', 'title'],
                           sort_titles=['submission time', 'view number', 'vote number', 'title'],
                           sort_by=sort_by,
                           order_direction=order_direction,
                           )


@app.route('/add-question', methods=['GET', 'POST'])
def add_question():
    if request.method == 'POST':
        if 'image-upload' in request.files:
            image = request.files['image-upload']
            if image.filename != '' and data_manager.allowed_file(image.filename):
                image.save(os.path.join(app.config['UPLOAD_FOLDER'], image.filename))
            else:
                image = ''

        question_data_dict = data_manager.create_new_question(request.form['title'], request.form['message'], image)

        return redirect(url_for('show_details', question_id=question_data_dict['id']))

    return render_template("add-question.html")


@app.route('/question/view_count/<question_id>')
def route_view_count(question_id):
    data_manager.view_count_handling(question_id)
    return redirect(f'/question/{question_id}')


@app.route('/question/<int:question_id>')
def show_details(question_id):
    question_to_display = data_manager.get_question_to_display(question_id)
    answers_to_display = data_manager.get_answers_to_display(question_id)

    return render_template('show-details.html',
                           question_to_display=question_to_display,
                           answers_to_display=answers_to_display)


@app.route('/<redirect_question_id>/vote/<filename>/<data_id>/<vote_type>')
def route_vote(redirect_question_id, filename, data_id, vote_type):
    data_manager.vote(filename, data_id, vote_type)
    return redirect(url_for('show_details', question_id=redirect_question_id))


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


@app.route('/question/<question_id>/new-answer', methods=['GET', 'POST'])
def route_add_answer(question_id):
    if request.method == 'POST':
        answer_text = request.form['message']
        if 'image-upload' in request.files:
            image = request.files['image-upload']
            if image.filename != '' and data_manager.allowed_file(image.filename):
                image.save(os.path.join(app.config['UPLOAD_FOLDER'], image.filename))
            else:
                image = ''
        image_name = image.filename if image else None
        data_manager.add_answer(question_id, answer_text, image_name)
        return redirect(url_for('show_details', question_id=question_id))

    return render_template('answer.html', question_id=question_id)


@app.route('/answer/<question_id>/<answer_id>/delete')
def route_delete_answer(answer_id, question_id):
    data_manager.delete_answer(answer_id)
    return redirect(url_for('show_details', question_id=question_id))


if __name__ == '__main__':
    app.run(
        port=5000,
        debug=False,
    )