import database_common
import util
from psycopg2 import sql


def allowed_file(filename):
    allowed_extensions = ['jpg', 'jpeg', 'png', 'gif']
    extension = 1
    return '.' in filename and filename.rsplit('.', 1)[extension] in allowed_extensions


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


@database_common.connection_handler
def get_searched_data(cursor, search_string):
    result_ids = set()
    search_string = search_string.strip("'")
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


"""------QUESTION SECTION------"""


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
def update_question(cursor, data_id, title, message):
    cursor.execute(
        sql.SQL("""UPDATE question
                   SET  title = {title}, message = {message}
                   WHERE id = {data_id};
                    """).format(title=sql.Literal(title),
                                message=sql.Literal(message),
                                data_id=sql.SQL(data_id)))


@database_common.connection_handler
def remove_question_and_its_answers(cursor, question_id, answers):
    questions_tag_ids = get_tag_ids(question_id)

    if answers:
        answer_ids = tuple([answer['id'] for answer in answers])

    cursor.execute(
        sql.SQL("""SELECT image FROM question
                       WHERE id = {q_id};
                          """).format(q_id=sql.SQL(question_id)))
    util.delete_image(cursor.fetchone()['image'])

    cursor.execute(
        sql.SQL("""DELETE FROM comment WHERE question_id = {q_id};
                   DELETE FROM comment WHERE answer_id = {a_id}
                   DELETE FROM answer WHERE question_id = {q_id};
                   DELETE FROM question_tag WHERE question_id = {q_id};
                   DELETE FROM question WHERE id = {q_id};
                            """).format(q_id=sql.SQL(question_id)))

    if questions_tag_ids:
        cursor.execute(
            sql.SQL("""DELETE FROM tag WHERE id = {questions_tag_ids};
                            """).format(questions_tag_ids=sql.SQL(questions_tag_ids)))



"""------QUESTION SECTION OVER------"""

"""------ANSWER SECTION------"""


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
def get_answers_to_display(cursor, question_id):
    cursor.execute(
        sql.SQL("""SELECT * FROM answer 
                   WHERE question_id = {question_id};
                    """).format(question_id=sql.Literal(question_id)))
    data = cursor.fetchall()
    return data


@database_common.connection_handler
def get_answer_to_edit(cursor, answer_id):
    cursor.execute(
        sql.SQL("""SELECT * FROM answer 
                   WHERE id = {answer_id};
                    """).format(answer_id=sql.Literal(answer_id)))
    data = cursor.fetchone()
    return data


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
def delete_answer(cursor, answer_id):
    cursor.execute(
        sql.SQL("""DELETE FROM answer 
                   WHERE id = {answer_id};
                       """).format(answer_id=sql.Literal(answer_id)))


"""------ANSWER SECTION OVER------"""

"""------COMMENT SECTION------"""


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


@database_common.connection_handler
def get_comment_message(cursor, comment_id):
    cursor.execute(
        sql.SQL("""SELECT message FROM comment
                   WHERE id = {comment_id}
                   """).format(comment_id=sql.SQL(comment_id))
    )
    data = cursor.fetchone()
    return data


@database_common.connection_handler
def get_question_comments_to_display(cursor, question_id):
    cursor.execute(
        sql.SQL("""SELECT id, question_id, submission_time, message, edited_count FROM comment
                   WHERE question_id={q_id};
                   """).format(q_id=sql.Literal(question_id))
    )
    data = cursor.fetchall()
    return data


@database_common.connection_handler
def get_answer_comments_to_display(cursor, answer_ids):
    if answer_ids:
        cursor.execute(
        sql.SQL("""SELECT id, answer_id, submission_time, message, edited_count FROM comment
                   WHERE answer_id IN {list_of_ids};
                   """).format(list_of_ids=sql.Literal(answer_ids))
    )
    data = cursor.fetchall()
    return data


@database_common.connection_handler
def edit_comment(cursor, comment_id, message):
    sub_time = util.convert_timestamp(util.create_timestamp())
    cursor.execute(
        sql.SQL("""UPDATE comment
                   SET  submission_time={sub_time}, message={msg}, edited_count = COALESCE(edited_count, 0) + 1 
                   WHERE id = {comment_id};
                   """).format(sub_time=sql.Literal(str(sub_time)),
                               msg=sql.Literal(message),
                               comment_id=sql.Literal(comment_id)))


@database_common.connection_handler
def delete_comment(cursor, comment_id):
    cursor.execute(
        sql.SQL(""" DELETE FROM comment 
                    WHERE id = {comment_id};
                           """).format(comment_id=sql.Literal(comment_id)))


"""------COMMENT SECTION OVER------"""

"""------TAG SECTION------"""


@database_common.connection_handler
def add_new_tag(cursor, question_id, new_tag):
    cursor.execute(
        sql.SQL("""INSERT INTO tag (name)
                   VALUES ({new_tag});
                        """).format(new_tag=sql.Literal(new_tag)))

    cursor.execute(
        sql.SQL("""INSERT INTO question_tag (question_id, tag_id)
                   VALUES ({question_id}, (SELECT max(id) FROM tag));
                            """).format(question_id=sql.SQL(question_id)))


@database_common.connection_handler
def get_all_tags(cursor):
    cursor.execute(
        sql.SQL("""SELECT name FROM tag;"""))
    data = cursor.fetchall()

    return data


@database_common.connection_handler
def get_questions_tags(cursor, question_id):
    tag_ids = get_tag_ids(question_id)

    if tag_ids:
        cursor.execute(
            sql.SQL("""SELECT * FROM tag
                       WHERE id IN {tag_ids};
                       """).format(tag_ids=sql.Literal(tag_ids)))
        data = cursor.fetchall()

    else:
        return tag_ids

    return data


@database_common.connection_handler
def delete_tag(cursor, tag_id):
    cursor.execute(
        sql.SQL("""DELETE FROM question_tag
                   WHERE tag_id = {tag_id};
                   """).format(tag_id=sql.Literal(tag_id)))

    cursor.execute(
        sql.SQL("""DELETE FROM tag
                   WHERE id = {tag_id};
                       """).format(tag_id=sql.Literal(tag_id)))


"""------TAG SECTION OVER------"""

"""------MISCELLANEOUS------"""


@database_common.connection_handler
def get_tag_ids(cursor, question_id):
    tag_ids = []

    cursor.execute(
        sql.SQL("""SELECT tag_id FROM question_tag
                   WHERE question_id = {question_id};
                       """).format(question_id=sql.Literal(question_id)))
    data = cursor.fetchall()

    for id in data:
        tag_ids.append(id['tag_id'])

    tag_ids = tuple(tag_ids)

    return tag_ids
