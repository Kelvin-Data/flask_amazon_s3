from flask import Flask, app, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
import boto3
import uuid

ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

db = SQLAlchemy()

class File(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    original_filename = db.Column(db.String(100))
    filename = db.Column(db.String(100))
    bucket = db.Column(db.String(100))
    region = db.Column(db.String(100))
    url = db.Column(db.String(200))

def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///s3.db'
    db.init_app(app)

    @app.route('/', methods=['GET', 'POST'])
    def index():
        if request.method == 'POST':
          
            
            uploaded_file = request.files['file-to-save']
            if not allowed_file(uploaded_file.filename):
               
                return 'FILE NOT ALLOWED'
            
           
            bucket_name = 'flaskupload76'    
            
            new_filename = uuid.uuid4().hex + '.'+ uploaded_file.filename.rsplit('.', 1)[1].lower()
            
            s3 = boto3.resource('s3')
            s3.Bucket(bucket_name).upload_fileobj(uploaded_file, new_filename)    
            
            file = File(
                original_filename=uploaded_file.filename,
                filename=new_filename,
                bucket=bucket_name,
                region='ap-southeast-1',
                
            )
            db.session.add(file)
            db.session.commit()

            return redirect(url_for('index'))
        
        files = File.query.all()
        return render_template('index.html', files=files)

    return app

if __name__ == '__main__':
    app.run(debug=True)
