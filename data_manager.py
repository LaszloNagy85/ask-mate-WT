import database_common
import util
from psycopg2 import sql
import bcrypt


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
def create_new_question(cursor, user_id, title, message, image):
    sub_time = util.convert_timestamp(util.create_timestamp())

    cursor.execute(
        sql.SQL("""INSERT INTO question (user_id, submission_time, view_number, vote_number, title, message, image) 
                   VALUES ({user_id},{sub_time}, 0, 0, {title}, {message}, {image});
                   """).format(user_id=sql.Literal(user_id),
                               sub_time=sql.Literal(str(sub_time)),
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

    """DELETE QUESTION IMAGE"""

    cursor.execute(
        sql.SQL("""SELECT image FROM question
                           WHERE id = {q_id};
                              """).format(q_id=sql.SQL(question_id)))
    image_name = cursor.fetchone()['image']
    if image_name and image_name != 'No image':
        util.delete_image(image_name)

    """DELETE ANSWER, ANSWER IMAGE AND ANSWER COMMENTS"""

    if answers:
        answer_ids = tuple([answer['id'] for answer in answers])
        answer_comment_ids = tuple([comment['id'] for comment in get_answer_comments_to_display(answer_ids)])
        if answer_comment_ids:
            cursor.execute(
                sql.SQL("""DELETE FROM comment WHERE id IN {answer_comment_ids};
                    """).format(answer_comment_ids=sql.Literal(answer_comment_ids)))

        cursor.execute(
            sql.SQL("""SELECT image FROM answer WHERE id IN {answer_ids};
                """).format(answer_ids=sql.Literal(answer_ids)))

        image_names = cursor.fetchall()
        if image_names:
            for row in image_names:
                if row['image'] != 'No image':
                    util.delete_image(row['image'])
        cursor.execute(
            sql.SQL("""DELETE FROM answer WHERE id IN {answer_ids};
                """).format(answer_ids=sql.Literal(answer_ids)))

    """DELETE TAGS, QUESTION TAGS, COMMENTS AND THE QUESTION"""
    questions_tag_ids = get_tag_ids(question_id)

    cursor.execute(
        sql.SQL("""DELETE FROM question_tag WHERE question_id = {q_id};
            """).format(q_id=sql.SQL(question_id)))

    if questions_tag_ids:
        cursor.execute(
            sql.SQL("""DELETE FROM tag WHERE id IN {questions_tag_ids};
                    """).format(questions_tag_ids=sql.Literal(questions_tag_ids)))

    cursor.execute(
        sql.SQL("""DELETE FROM comment WHERE question_id = {q_id};
                   DELETE FROM question WHERE id = {q_id};
                            """).format(q_id=sql.SQL(question_id)))


"""------QUESTION SECTION OVER------"""

"""------ANSWER SECTION------"""


@database_common.connection_handler
def add_answer(cursor, user_id, question_id, answer_text, image_name):
    sub_time = util.convert_timestamp(util.create_timestamp())

    cursor.execute(
        sql.SQL("""INSERT INTO answer (user_id,submission_time, vote_number, question_id, message, image) 
                   VALUES ({user_id}, {sub_time}, 0, {question_id}, {message}, {image});
                   """).format(user_id=sql.Literal(user_id),
                               sub_time=sql.Literal(str(sub_time)),
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
def new_comment(cursor, comment_type, data_id, comment, user_id):
    sub_time = util.convert_timestamp(util.create_timestamp())
    cursor.execute(
        sql.SQL("""INSERT INTO comment ({com_type}, user_id,  message, submission_time)
                   VALUES ({id_number}, {user_id}, {msg}, {sub_time});
                   """).format(com_type=sql.SQL(comment_type),
                               id_number=sql.SQL(data_id),
                               user_id=sql.Literal(user_id),
                               msg=sql.Literal(comment),
                               sub_time=sql.Literal(str(sub_time)))
    )


@database_common.connection_handler
def get_comment_message(cursor, comment_id):
    cursor.execute(
        sql.SQL("""SELECT message, user_id FROM comment
                   WHERE id = {comment_id}
                   """).format(comment_id=sql.SQL(comment_id))
    )
    data = cursor.fetchone()
    return data


@database_common.connection_handler
def get_question_comments_to_display(cursor, question_id):
    cursor.execute(
        sql.SQL("""SELECT id, question_id, submission_time, user_id, message, edited_count FROM comment
                   WHERE question_id={q_id};
                   """).format(q_id=sql.Literal(question_id))
    )
    data = cursor.fetchall()
    return data


@database_common.connection_handler
def get_answer_comments_to_display(cursor, answer_ids):
    if answer_ids:
        cursor.execute(
        sql.SQL("""SELECT id, answer_id, submission_time, user_id, message, edited_count FROM comment
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


"""------TAG SECTION OVER------"""

"""------PASSWORD SECTION------"""


def hash_password(plain_text_password):
    hashed_bytes = bcrypt.hashpw(plain_text_password.encode('utf-8'), bcrypt.gensalt())
    return hashed_bytes.decode('utf-8')


def verify_password(plain_text_password, hashed_password):
    hashed_bytes_password = hashed_password.encode('utf-8')
    return bcrypt.checkpw(plain_text_password.encode('utf-8'), hashed_bytes_password)


@database_common.connection_handler
def check_user_validity(cursor, user_name, user_input_password):
    cursor.execute(
        sql.SQL("""SELECT name, password FROM users
                   WHERE name = {user_name};
                    """).format(user_name=sql.Literal(user_name))
    )
    user_data = cursor.fetchone()
    if user_data:
        if verify_password(user_input_password, user_data['password']):
            return True
    return False


@database_common.connection_handler
def save_user_registration(cursor, user_name, password):
    hashed_password = hash_password(password)
    sub_time = util.convert_timestamp(util.create_timestamp())

    cursor.execute(
        sql.SQL("""INSERT INTO users(name, password, submission_time, reputation)
                   VALUES ({user_name}, {hashed_password}, {submission_time}, 0)
                   """).format(user_name=sql.Literal(user_name),
                               hashed_password=sql.Literal(hashed_password),
                               submission_time=sql.Literal(str(sub_time)))
    )


@database_common.connection_handler
def get_user_id(cursor, user_name):
    cursor.execute(
        sql.SQL("""SELECT id FROM users
                   WHERE name = {user_name}
                       """).format(user_name=sql.Literal(user_name)))
    user_id = cursor.fetchone()

    return user_id
