import connection


def get_all_data(filename):
    return connection.get_all_data_from_file(filename)


def export_data(filename, input_data, data_header):
    return connection.export_data_to_file(filename, input_data, data_header)
