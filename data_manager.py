import connection


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


def vote(filename, data_id, vote_type):
    header = 0 if filename == 'question' else 1
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
