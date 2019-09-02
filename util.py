from datetime import  datetime
import os
import data_manager


def create_timestamp():
    return int(datetime.timestamp(datetime.now()))


def convert_timestamp(submission_time):
    return datetime.fromtimestamp(submission_time)

def upload_image(files, app):
    image = files['image-upload']
    if image.filename != '' and data_manager.allowed_file(image.filename):
        image.save(os.path.join(app.config['UPLOAD_FOLDER'], image.filename))
    else:
        image = ''

    return image
