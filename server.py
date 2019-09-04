from flask import Flask, request, render_template, redirect, url_for
import data_manager
import util


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


@app.route('/list', methods=['GET', 'POST'])
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


@app.route('/search')
def route_list_search_results():
    sort_by = 'submission_time'
    order_direction = 'desc'
    if 'sort' in request.args:
        sort_by = request.args.get('sort')
    if 'order' in request.args:
        order_direction = request.args.get('order')

    search_string = request.args.get('q')
    questions = data_manager.get_searched_data(search_string)

    if type(questions) is str:
        return render_template('error.html', error_message=questions)

    else:
        return render_template('search.html',
                               questions=questions,
                               sort_options=['submission_time', 'view_number', 'vote_number', 'title'],
                               sort_titles=['submission time', 'view number', 'vote number', 'title'],
                               sort_by=sort_by,
                               order_direction=order_direction,
                               )


@app.route('/question/<int:question_id>')
def route_show_details(question_id):
    question_to_display = data_manager.get_question_to_display(question_id)
    answers_to_display = data_manager.get_answers_to_display(question_id)

    return render_template('show-details.html',
                           question_to_display=question_to_display,
                           answers_to_display=answers_to_display)


@app.route('/add-question', methods=['GET', 'POST'])
def add_question():
    if request.method == 'POST':
        image = util.upload_image(request.files, app)
        new_question_id = data_manager.create_new_question(request.form['title'], request.form['message'], image)
        return redirect(url_for('route_show_details', question_id=new_question_id['id']))

    return render_template('add-question.html')


@app.route('/question/<data_id>/edit', methods=["GET", "POST"])
def edit_question(data_id):
    question = data_manager.get_question_to_display(data_id)
    if request.method == 'POST':
        data_manager.update_question(data_id, request.form['title'], request.form['message'])
        return redirect(url_for('route_show_details', question_id=data_id))

    return render_template('edit-question.html', question=question, data_id=data_id)


@app.route('/answer/<answer_id>/edit', methods=["GET", "POST"])
def edit_answer(answer_id):
    answer = data_manager.get_answers_to_edit(answer_id)
    if request.method == 'POST':
        question_id = data_manager.edit_answer(answer_id, request.form['message'])
        return redirect(url_for('route_show_details', question_id=question_id['question_id']))

    return render_template('edit-answer.html', answer=answer)


@app.route('/question/<data_id>/delete')
def delete_question(data_id):
    data_manager.remove_question_and_its_answers(data_id)
    return redirect(url_for('route_list'))


@app.route('/question/<question_id>/new-answer', methods=['GET', 'POST'])
def route_add_answer(question_id):
    if request.method == 'POST':
        image = util.upload_image(request.files, app)
        data_manager.add_answer(question_id, request.form['message'], image)
        return redirect(url_for('route_show_details', question_id=question_id))

    return render_template('answer.html', question_id=question_id)


@app.route('/answer/<question_id>/<answer_id>/delete')
def route_delete_answer(answer_id, question_id):
    data_manager.delete_answer(answer_id)
    return redirect(url_for('route_show_details', question_id=question_id))


@app.route('/question/view_count/<question_id>')
def route_view_count(question_id):
    data_manager.view_count_handling(question_id)
    return redirect(url_for('route_show_details', question_id=question_id))


@app.route('/<redirect_question_id>/vote/<table_name>/<data_id>/<vote_type>')
def route_vote(redirect_question_id, table_name, data_id, vote_type):
    data_manager.vote(table_name, data_id, vote_type)
    return redirect(url_for('route_show_details', question_id=redirect_question_id))


@app.route('/comment/<question_id>', methods=['GET', 'POST'])
@app.route('/comment/<question_id>/<answer_id>', methods=['GET', 'POST'])
def route_new_comment(question_id, answer_id=''):
    question_data = data_manager.get_question_to_display(question_id)
    answer_data = None if not answer_id else data_manager.get_answer_to_comment(answer_id)

    if request.method == 'POST':
        data_id = question_id if not answer_id else answer_id
        comment_type = 'question_id' if not answer_id else 'answer_id'
        data_manager.new_comment(comment_type, data_id, request.form['comment'])
        return redirect(url_for('route_show_details', question_id=question_id))

    return render_template('comment.html', question_data=question_data, answer_data=answer_data)


@app.route('/question/<question_id>/new-tag', methods=['GET', 'POST'])
def route_new_tag(question_id):
    tags = data_manager.get_all_tags()
    if request.method == "POST":
        data_manager.add_new_tag(question_id, request.form['tag'])
        return redirect(url_for('route_show_details', question_id=question_id))
    return render_template('add-tag.html', question_id=question_id, tags=tags)


if __name__ == '__main__':
    app.run(
        port=5000,
        debug=False,
    )