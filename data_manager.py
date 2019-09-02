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


@database_common.connection_handler
def vote(cursor, table_name, data_id, vote_type):
    vote_modificator = '1' if vote_type == 'up' else '-1'
    cursor.execute(
        sql.SQL("""UPDATE {table}
                SET vote_number = vote_number + {vote}
                WHERE id = {data_id}
                """).format(table=sql.Identifier(table_name),
                            vote=sql.SQL(vote_modificator),
                            data_id=sql.SQL(data_id))
    )


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


@database_common.connection_handler
def create_new_question(cursor, title, message, image):
    sub_time = util.convert_timestamp(util.create_timestamp())

    cursor.execute(
        sql.SQL("""INSERT INTO question (submission_time, view_number, vote_number, title, message, image) 
                   VALUES ({sub_time}, 0, 0, {title}, {message}, {image});
                   """).format(sub_time=sql.Literal(str(sub_time)),
                               title=sql.Literal(title),
                               message=sql.Literal(message),
                               image=sql.Literal(image)))

    cursor.execute(
        sql.SQL("""SELECT * FROM question
                   WHERE id=(SELECT max(id) FROM question)     """))
    data = cursor.fetchall()
    return data


@database_common.connection_handler
def get_question_to_display(cursor, question_id):
    cursor.execute(
        sql.SQL("""SELECT * FROM question 
                   WHERE id = {question_id};
                    """).format(question_id=sql.Literal(question_id)))
    data = cursor.fetchall()
    return data


@database_common.connection_handler
def get_answers_to_display(cursor, question_id):
    cursor.execute(
        sql.SQL("""SELECT * FROM answer 
                   WHERE question_id = {question_id};
                    """).format(question_id=sql.Literal(question_id)))
    data = cursor.fetchall()
    return data


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


