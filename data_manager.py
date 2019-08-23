import connection
from datetime import datetime


def get_all_data(filename):
    return connection.get_all_data_from_file(filename)


def export_data(filename, input_data, data_header):
    return connection.export_data_to_file(filename, input_data, data_header)


def get_sorted_data(filename, sort_by, order_direction):
    data_to_sort = get_all_data(filename)

    is_int = str if sort_by == 'title' else int
    is_reverse = True if order_direction == 'desc' else False

    sorted_questions = sorted(data_to_sort, key=lambda x: is_int(x[sort_by]), reverse=is_reverse)
    return sorted_questions


def view_count_handling(data_id):
    questions = get_all_data("question")
    for question in questions:
        if str(data_id) == question["id"]:
            question["view_number"] = str(int(question["view_number"])+1)
            export_data("question", questions, 'question_header')
    return


def vote(filename, data_id, vote_type):
    header = 'question_header' if filename == 'question' else 'answer_header'
    data = get_all_data(filename)
    vote_modificator = 1 if vote_type == 'up' else -1
    for row in data:
        if row['id'] == data_id:
            row['vote_number'] = str(int(row['vote_number']) + vote_modificator)
    return connection.export_data_to_file(filename, data, header)


"""Image handling section"""

ALLOWED_EXTENSIONS = ['jpg', 'jpeg', 'png', 'gif']


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS


"""Image handling section over."""


def add_answer(question_id):
    timestamp = datetime.timestamp(datetime.now())
    answers_list = get_all_data('answer')
    answer_data_dict = {
        "id": len(answers_list),
        'submission_time': int(timestamp),
        "vote_number": 0,
        "question_id": question_id,
        "message": request.form["message"],
        "image": "",
    }
    answers_list.append(answer_data_dict)
    export_data("answer", answers_list, 'answer_header')


def delete_answer(answer_id):
    answers = get_all_data("answer")
    for answer in answers:
        if answer["id"] == answer_id:
            del answers[answers.index(answer)]
    export_data("answer", answers, 'answer_header')