import connection
import database_common
from datetime import datetime
import util
from psycopg2 import sql


def get_all_data(filename):
    return connection.get_all_data_from_file(filename)


@database_common.connection_handler
def get_all_data_sql(cursor, table_name, sort_by, order_direction, limit_it=''):
    cursor.execute(
        sql.SQL("""SELECT * FROM {table} 
                ORDER BY {order} {direction}
                {limit};
                """).format(table=sql.Identifier(table_name),
                            order=sql.Identifier(sort_by),
                            direction=sql.SQL(order_direction),
                            limit=sql.SQL(limit_it))
    )
    data = cursor.fetchall()
    return data


def export_data(filename, input_data, data_header):
    connection.export_data_to_file(filename, input_data, data_header)


@database_common.connection_handler
def view_count_handling(cursor, question_id):
    cursor.execute(
        sql.SQL("""UPDATE question
                SET view_number = view_number + 1
                WHERE id = {q_id};
                """).format(q_id=sql.SQL(question_id))
    )


def vote(filename, data_id, vote_type):
    header = 'question_header' if filename == 'question' else 'answer_header'
    data = get_all_data(filename)
    vote_modificator = 1 if vote_type == 'up' else -1
    for row in data:
        if row['id'] == data_id:
            row['vote_number'] = str(int(row['vote_number']) + vote_modificator)
    connection.export_data_to_file(filename, data, header)


"""Image handling section"""

ALLOWED_EXTENSIONS = ['jpg', 'jpeg', 'png', 'gif']


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS


"""Image handling section over."""


def add_answer(question_id, answer_text, image_name):
    timestamp = datetime.timestamp(datetime.now())
    answers_list = get_all_data('answer')
    answer_data_dict = {
        'id': len(answers_list),
        'submission_time': int(timestamp),
        'vote_number': 0,
        'question_id': question_id,
        'message': answer_text,
        'image': image_name,
    }
    answers_list.append(answer_data_dict)
    export_data('answer', answers_list, 'answer_header')


def delete_answer(answer_id):
    answers = get_all_data("answer")
    for answer in answers:
        if answer["id"] == answer_id:
            del answers[answers.index(answer)]
    export_data("answer", answers, 'answer_header')


def create_new_question(title, message, image):

    questions_list = get_all_data('question')

    question_data_dict = {
        'id': len(questions_list),
        'submission_time': util.create_timestamp(),
        'view_number': 0,
        'vote_number': 0,
        'title': title,
        'message': message,
        'image': image.filename if image else None,
    }
    questions_list.append(question_data_dict)
    connection.export_data_to_file("question", questions_list, 'question_header')

    return question_data_dict


def get_question_to_display(question_id):
    questions = get_all_data("question")

    for question in questions:
        if str(question_id) == question["id"]:
            question_to_display = question
    question_to_display["submission_time"] = datetime.fromtimestamp(int(question_to_display["submission_time"]))

    return question_to_display


def get_answers_to_display(question_id):
    answers = get_all_data("answer")
    answers_to_display = []

    for answer in answers:
        if str(question_id) == answer["question_id"]:
            answer["submission_time"] = datetime.fromtimestamp(int(answer["submission_time"]))
            answers_to_display.append(answer)

    return answers_to_display


def update_and_export_question(questions, data_id, title, message):
    for question in questions:
        if data_id == question["id"]:
            question["title"] = title
            question["message"] = message
            export_data("question", questions, 'question_header')


def remove_question_and_its_answers(data_id):
    questions = get_all_data("question")
    answers = get_all_data("answer")
    answers_to_remove_index = []

    for question in questions:
        if question["id"] == data_id:
            questions.remove(question)
            export_data("question", questions, 'question_header')

    for answer in answers:
        if answer["question_id"] == data_id:
            answers_to_remove_index.append(answers.index(answer))

    for index_number in answers_to_remove_index:
        del answers[index_number]

    export_data("answer", answers, 'answer_header')


