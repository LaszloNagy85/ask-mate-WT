import csv


DATA_HEADER_QUESTION = ['id', 'submission_time', 'view_number', 'vote_number', 'title', 'message', 'image']
DATA_HEADER_ANSWER = ['id', 'submission_time', 'vote_number', 'question_id', 'message', 'image']


def get_all_data_from_file(file_name):
    with open(f"sample_data/{file_name}.csv", "r") as csv_file:
        csv_reader = csv.DictReader(csv_file)
        return [dict(row) for row in csv_reader]


def export_data_to_file(file_name, input_data, question_or_answer):
    headers = [DATA_HEADER_QUESTION, DATA_HEADER_ANSWER]

    with open(f"sample_data/{file_name}.csv", "w") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=headers[question_or_answer])
        writer.writeheader()
        for each in input_data:
            writer.writerow(each)
