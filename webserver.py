import os

from flask import flash, Flask, redirect, render_template, request, url_for
from flask import send_from_directory
from keras.models import Sequential, load_model
from PIL import Image
from werkzeug.utils import secure_filename
import keras,sys
import numpy as np


CLASSES = ['MORE', 'Ray', 'VERY']
NUM_CLASSES = len(CLASSES)
IMAGE_SIZE_W = 50
IMAGE_SIZE_H = 100

UPLOAD_FOLDER = './uploads'
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'gif'])


app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.',1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/', methods=['GET', 'POST'])
def upload_file():  
    if request.method == 'POST':
        print('============>POST開始')
        if 'file' not in request.files:
            flash('ファイルがありません')
            return redirect(request.url)
        file = request.files['file']
        if file.filename == '':
            flash('ファイル名がありません')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            keras.backend.clear_session()
            model = load_model('./visual_cnn.h5')
            image = Image.open(filepath)
            image = image.convert('RGB')
            image = image.resize((IMAGE_SIZE_W, IMAGE_SIZE_H))
            data = np.asarray(image)
            X = []
            X.append(data)
            X = np.array(X)
            result = model.predict([X])[0]
            predicted = result.argmax()
            percentage = int(result[predicted] * 100)

            os.remove('./uploads/' + filename)

            return render_template('index.html', filename=filename, predicted=CLASSES[predicted], percentage=percentage)
    return render_template('index.html')


# @app.route('/uploads/<filename>')
# def uploaded_file(filename):
#     return send_from_directory(app.config['UPLOAD_FOLDER'], filename)


@app.route('/reset')
def reset_site():
    return redirect(url_for('upload_file'))

def main():
    app.debug = True
    app.run(host='127.0.0.1', port=5000)


if __name__ == '__main__':
    main()
