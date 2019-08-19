import connection


def get_all_data(filename):
    return connection.get_all_data_from_file(filename)


def get_sorted_data(filename, sort_by='submission_time', order_direction='desc'):
    data_to_sort = get_all_data(filename)

    is_int = str if sort_by == 'title' else int
    is_reverse = True if order_direction == 'desc' else False

    sorted_questions = sorted(data_to_sort, key=lambda x: is_int(x[sort_by]), reverse= is_reverse)
    return sorted_questions
