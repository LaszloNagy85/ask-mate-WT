from flask import Flask, request, render_template, redirect, url_for, session
import data_manager
import util

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'static/images'
app.config['MAX_CONTENT_LENGTH'] = 5 * 2000 * 1400
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'
app.jinja_env.add_extension('jinja2.ext.loopcontrols')


@app.route('/')
def route_list():
    sort_by = 'submission_time'
    order_direction = 'desc'
    if 'sort' in request.args:
        sort_by = request.args.get('sort')
    if 'order' in request.args:
        order_direction = request.args.get('order')
    questions = data_manager.get_all_data_sql('question', sort_by, order_direction, limit_it='LIMIT 5')
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
    questions = data_manager.get_all_data_sql('question', sort_by, order_direction)

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
    tags = data_manager.get_questions_tags(question_id)

    question_comments_to_display = data_manager.get_question_comments_to_display(question_id)

    answer_ids = tuple([answer['id'] for answer in answers_to_display]) if answers_to_display else None
    answer_comments_to_display = data_manager.get_answer_comments_to_display(answer_ids) if answer_ids else None

    comment_answer_ids = []
    if answer_comments_to_display:
        comment_answer_ids = [comment['answer_id'] for comment in answer_comments_to_display]

    return render_template('show-details.html',
                           question_to_display=question_to_display,
                           answers_to_display=answers_to_display,
                           question_comments=question_comments_to_display,
                           answer_comments=answer_comments_to_display,
                           comment_answer_ids=comment_answer_ids,
                           tags=tags)


@app.route('/add-question', methods=['GET', 'POST'])
def add_question():
    if request.method == 'POST':
        image = util.upload_image(request.files, app)
        user_id = session['user_id']['id']
        new_question_id = data_manager.create_new_question(user_id, request.form['title'], request.form['message'], image)
        return redirect(url_for('route_show_details', question_id=new_question_id['id']))

    return render_template('add-question.html')


@app.route('/question/<data_id>/edit', methods=["GET", "POST"])
def edit_question(data_id):
    user_id = session['user_id']['id']
    question = data_manager.get_question_to_display(data_id)
    if request.method == 'POST':
        if user_id != question['user_id']:
            return render_template('error.html', error_message='Stop hacking!!!')
        else:
            data_manager.update_question(data_id, request.form['title'], request.form['message'])
            return redirect(url_for('route_show_details', question_id=data_id))

    return render_template('edit-question.html', question=question, data_id=data_id)


@app.route('/answer/<answer_id>/edit', methods=["GET", "POST"])
def edit_answer(answer_id):
    user_id = session['user_id']['id']
    answer = data_manager.get_answer_to_edit(answer_id)
    if request.method == 'POST':
        if user_id != answer['user_id']:
            return render_template('error.html', error_message='Stop hacking!!!')
        else:
            question_id = data_manager.edit_answer(answer_id, request.form['message'])
            return redirect(url_for('route_show_details', question_id=question_id['question_id']))

    return render_template('edit-answer.html', answer=answer)


@app.route('/question/<data_id>/delete')
def delete_question(data_id):
    answers = data_manager.get_answers_to_display(data_id)
    data_manager.remove_question_and_its_answers(data_id, answers)
    return redirect(url_for('route_list'))


@app.route('/question/<question_id>/new-answer', methods=['GET', 'POST'])
def route_add_answer(question_id):
    if request.method == 'POST':
        image = util.upload_image(request.files, app)
        user_id = session['user_id']['id']
        data_manager.add_answer(user_id, question_id, request.form['message'], image)
        return redirect(url_for('route_show_details', question_id=question_id))

    return render_template('answer.html', question_id=question_id)


@app.route('/answer/<question_id>/<answer_id>/delete')
def route_delete_answer(answer_id, question_id):
    data_manager.delete_answer(answer_id)
    return redirect(url_for('route_show_details', question_id=question_id))


@app.route('/answer/accept')
def route_answer_acceptance():
    data_manager.set_accepted_answer(request.args['answer_id'], request.args['user_id'])
    return redirect(url_for('route_show_details', question_id=request.args['redirect_question_id']))


@app.route('/comments/<redirect_question_id>/<comment_id>/delete')
def route_delete_comment(redirect_question_id, comment_id):
    print(comment_id)
    data_manager.delete_comment(comment_id)
    return redirect(url_for('route_show_details', question_id=redirect_question_id))


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
    answer_data = None if not answer_id else data_manager.get_answer_to_edit(answer_id)

    if request.method == 'POST':
        data_id = question_id if not answer_id else answer_id
        comment_type = 'question_id' if not answer_id else 'answer_id'
        user_id = session['user_id']['id']
        data_manager.new_comment(comment_type, data_id, request.form['comment'], user_id)
        return redirect(url_for('route_show_details', question_id=question_id))

    return render_template('comment.html', question_data=question_data, answer_data=answer_data)


@app.route('/comment/<comment_id>/edit', methods=["GET", 'POST'])
def route_edit_comment(comment_id):
    user_id = session['user_id']['id']
    redirect_question_id = request.args['redirect_question_id']
    comment_message = data_manager.get_comment_message(comment_id)
    if request.method == 'POST':
        if user_id != comment_message['user_id']:
            return render_template('error.html', error_message='Stop hacking!!!')
        else:
            modified_comment_message = request.form['comment']
            data_manager.edit_comment(comment_id, modified_comment_message)
            return redirect(url_for('route_show_details', question_id=redirect_question_id))

    return render_template('comment.html',
                           comment_id=comment_id,
                           comment_message=comment_message,
                           redirect_question_id=redirect_question_id)


@app.route('/question/<question_id>/new-tag', methods=['GET', 'POST'])
def route_new_tag(question_id):
    tag_data = data_manager.get_all_tags()
    tags = set()
    for each in tag_data:
        tags.add(each['name'])

    if request.method == "POST":
        if data_manager.add_new_tag(question_id, request.form['tag']) == 'Already added':
            return render_template('error.html', error_message='Tag already added to question')
        else:
            data_manager.add_new_tag(question_id, request.form['tag'])
            return redirect(url_for('route_show_details', question_id=question_id))
    return render_template('add-tag.html', question_id=question_id, tags=tags)


@app.route('/question/<question_id>/tag/<tag_id>/delete', methods=['GET', 'POST'])
def route_delete_tag(question_id, tag_id):
    data_manager.delete_tag(tag_id)
    return redirect(url_for('route_show_details', question_id=question_id))


@app.route('/tags')
def route_tags():
    data = data_manager.get_all_tags_and_count()
    return render_template('list-all-tags.html', data=data)


@app.route('/registration', methods=['GET', 'POST'])
def route_register():
    if request.method == 'POST':
        data_manager.save_user_registration(request.form['user_name'], request.form['password'])
        session['username'] = request.form['user_name']
        session['user_id'] = data_manager.get_user_id(request.form['user_name'])
        return redirect(url_for('route_list'))
    return render_template('register-login.html', html_data='Registration')


@app.route('/login', methods=['GET', 'POST'])
def route_login():
    if request.method == 'POST':
        if data_manager.check_user_validity(request.form['user_name'], request.form['password']):
            session['username'] = request.form['user_name']
            session['user_id'] = data_manager.get_user_id(request.form['user_name'])
            return redirect(url_for('route_list'))
        else:
            error_message = "Invalid user name or password"
            return render_template('error.html', error_message=error_message)

    return render_template('register-login.html', html_data='Login')


@app.route('/logout')
def logout():
    session.pop('username', None)
    session.clear()
    return redirect(url_for('route_list'))


@app.route('/users')
def route_users():
    data = data_manager.get_all_users_data()
    return render_template('users.html', data=data)


@app.route('/user/<user_id>')
def route_user_activity(user_id):
    user_questions = data_manager.get_all_user_questions(user_id)
    user_answers = data_manager.get_all_user_answers(user_id)
    user_question_comments = data_manager.get_all_user_question_comments(user_id)
    user_answer_comments = data_manager.get_all_user_answer_comments(user_id)

    return render_template('user-activity.html',
                           user_questions=user_questions,
                           user_answers=user_answers,
                           user_question_comments=user_question_comments,
                           user_answer_comments=user_answer_comments)


if __name__ == '__main__':
    app.run(
        host='10.44.1.211',
        port=8000,
        debug=False,
    )
