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


"""Image handling section"""

ALLOWED_EXTENSIONS = ['jpg', 'jpeg', 'png', 'gif']


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS


"""Image handling section over."""


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

    cursor.execute(
        sql.SQL("""SELECT * FROM answer
                   WHERE id=(SELECT max(id) FROM answer)     """))
    data = cursor.fetchall()
    return data


@database_common.connection_handler
def delete_answer(cursor, answer_id):
    cursor.execute(
        sql.SQL("""DELETE FROM answer 
                   WHERE id = {answer_id};
                       """).format(answer_id=sql.Literal(answer_id)))


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
def update_and_export_question(cursor, data_id, title, message):
    cursor.execute(
        sql.SQL("""UPDATE question
                   SET  title = {title}, message = {message}
                   WHERE id = {data_id};
                    """).format(title=sql.Literal(title),
                                message=sql.Literal(message),
                                data_id=sql.SQL(data_id)))


@database_common.connection_handler
def remove_question_and_its_answers(cursor, data_id):
    cursor.execute(
        sql.SQL("""DELETE FROM answer WHERE question_id = {data_id};
                   DELETE FROM question WHERE id = {data_id};
                        """).format(data_id=sql.SQL(data_id)))


