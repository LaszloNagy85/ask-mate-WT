import database_common
import util
from psycopg2 import sql


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


def allowed_file(filename):
    allowed_extensions = ['jpg', 'jpeg', 'png', 'gif']
    extension = 1
    return '.' in filename and filename.rsplit('.', 1)[extension] in allowed_extensions


@database_common.connection_handler
def add_answer(cursor, question_id, answer_text, image_name):
    sub_time = util.convert_timestamp(util.create_timestamp())

    cursor.execute(
        sql.SQL("""INSERT INTO answer (submission_time, vote_number, question_id, message, image) 
                   VALUES ({sub_time}, 0, {question_id}, {message}, {image});
                   """).format(sub_time=sql.Literal(str(sub_time)),
                               question_id=sql.Literal(question_id),
                               message=sql.Literal(answer_text),
                               image=sql.Literal(image_name)))


@database_common.connection_handler
def delete_answer(cursor, answer_id):
    cursor.execute(
        sql.SQL("""DELETE FROM answer 
                   WHERE id = {answer_id};
                       """).format(answer_id=sql.Literal(answer_id)))


@database_common.connection_handler
def edit_answer(cursor, answer_id, message):
    cursor.execute(
        sql.SQL(""" UPDATE answer
                    SET message = {message}
                    WHERE id = {answer_id}
                    """).format(message=sql.Literal(message),
                                answer_id=sql.SQL(answer_id)))
    cursor.execute(
        sql.SQL(""" SELECT question_id FROM answer 
                    WHERE id = {answer_id};
                           """).format(answer_id=sql.Literal(answer_id)))
    question_id = cursor.fetchone()
    return question_id


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
        sql.SQL("""SELECT id FROM question
                   WHERE id=(SELECT max(id) FROM question)     """))
    data = cursor.fetchone()
    return data


@database_common.connection_handler
def get_question_to_display(cursor, question_id):
    cursor.execute(
        sql.SQL("""SELECT * FROM question 
                   WHERE id = {question_id};
                    """).format(question_id=sql.Literal(question_id)))
    data = cursor.fetchone()
    return data


@database_common.connection_handler
def get_answers_to_display(cursor, question_id):
    cursor.execute(
        sql.SQL("""SELECT * FROM answer 
                   WHERE question_id = {question_id};
                    """).format(question_id=sql.Literal(question_id)))
    data = cursor.fetchall()
    return data


@database_common.connection_handler
def get_answers_to_edit(cursor, answer_id):
    cursor.execute(
        sql.SQL("""SELECT * FROM answer 
                   WHERE id = {answer_id};
                    """).format(answer_id=sql.Literal(answer_id)))
    data = cursor.fetchone()
    return data


@database_common.connection_handler
def get_answer_to_comment(cursor, answer_id):
    cursor.execute(
        sql.SQL("""SELECT * FROM answer 
                   WHERE answer_id = {a_id};
                    """).format(a_id=sql.Literal(answer_id)))
    data = cursor.fetchall()
    return data


@database_common.connection_handler
def update_question(cursor, data_id, title, message):
    cursor.execute(
        sql.SQL("""UPDATE question
                   SET  title = {title}, message = {message}
                   WHERE id = {data_id};
                    """).format(title=sql.Literal(title),
                                message=sql.Literal(message),
                                data_id=sql.SQL(data_id)))


@database_common.connection_handler
def remove_question_and_its_answers(cursor, question_id):
    cursor.execute(
        sql.SQL("""DELETE FROM answer WHERE question_id = {q_id};
                   DELETE FROM question WHERE id = {q_id};
                        """).format(q_id=sql.SQL(question_id)))


@database_common.connection_handler
def get_searched_data(cursor, search_string):
    result_ids = set()
    cursor.execute(
        sql.SQL("""SELECT id FROM question
                   WHERE message LIKE '%{search_string}%'
                   OR title LIKE '%{search_string}%';
                    """).format(search_string=sql.SQL(search_string)))
    questions_with_result = cursor.fetchall()

    cursor.execute(
        sql.SQL("""SELECT question_id FROM answer
                   WHERE message LIKE '%{search_string}%';
                        """).format(search_string=sql.SQL(search_string)))
    answers_with_result = cursor.fetchall()

    for question in questions_with_result:
        result_ids.add(question['id'])

    for answer in answers_with_result:
        result_ids.add(answer['question_id'])

    result_ids = tuple(result_ids)

    if result_ids:
        cursor.execute(
            sql.SQL("""SELECT * FROM question
                       WHERE id IN {result_ids};
                        """).format(result_ids=sql.Literal(result_ids)))
        result_data = cursor.fetchall()

    else:
        result_data = 'Search not found in database'

    return result_data


@database_common.connection_handler
def add_new_tag(cursor, question_id, new_tag):
    cursor.execute(
        sql.SQL("""INSERT INTO tag (name)
                   VALUES {new_tag};
                        """).format(new_tag=sql.Identifier(new_tag)))

    cursor.execute(
        sql.SQL("""INSERT INTO question_tag
                   VALUES (SELECT max(id) FROM tag)
                   WHERE question_id = {question_id};
                            """).format(question_id=sql.Identifier(question_id)))


@database_common.connection_handler
def new_comment(cursor, comment_type, data_id, comment):
    sub_time = util.convert_timestamp(util.create_timestamp())
    cursor.execute(
        sql.SQL("""INSERT INTO comment ({com_type}, message, submission_time)
                   VALUES ({id_number}, {msg}, {sub_time});
                   """).format(com_type=sql.SQL(comment_type),
                               id_number=sql.SQL(data_id),
                               msg=sql.Literal(comment),
                               sub_time=sql.Literal(str(sub_time)))
    )
