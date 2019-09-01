from datetime import  datetime


def create_timestamp():
    return int(datetime.timestamp(datetime.now()))


def convert_timestamp(submission_time):
    return datetime.fromtimestamp(submission_time)

