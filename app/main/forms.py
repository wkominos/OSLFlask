import os
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, FileField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo
from werkzeug.utils import secure_filename
from app.models import User
from flask import current_app, flash
from app.main import new_accounts
from app.models import LibraryUser
from app import db
import paramiko

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField(
        'Repeat Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

    #querys the db
    #name structure tells WTForms to automatically use these validators
    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('Please use a different username.')

    #querys the db
    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('Please use a different email address.')

class UploadForm(FlaskForm):
    attachment = FileField('Image File')
    submit = SubmitField('Upload')

    def allowed_file(self, filename):
        ALLOWED_EXTENSIONS = {'xml'}
        return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

    def get_filename(request):
        filename = secure_filename(request.attachment.data.filename)
        return filename

    def upload(request):
        if request.attachment.data:
            filename = secure_filename(request.attachment.data.filename)
            request.attachment.data.save(os.path.join(current_app.config['UPLOAD_FOLDER'], filename))

class ValidationForm(UploadForm):
        submit = SubmitField("Get Validation File")

        def parse_ILL_users_file(request, filename):
            user_submitted_file = new_accounts.parse_XML_report(f'uploads/{filename}')
            return new_accounts.get_workflows_users_from_xml(user_submitted_file)

        def create_validation_file(request, xml_users, filename):
            #have to add the old user data here. Only useful with ILL so do not add to database.
            old_user_data = new_accounts.process_CSV_with_header_into_array(filePath="uploads/OldUserData.csv")
            validation_file = new_accounts.build_data_for_textfile(xml_users) + new_accounts.old_data(old_user_data)
            new_accounts.convert_data_to_texfile_for_ILL(validation_file, old_user_data, filename)
            #download the file for the user

        #define errors for the above function
        #this function might need to go into new accounts file
        def db_user(request, users):
            counter = 0
            for user in users:
                or_number = user.find(".//").text
                if or_number:
                    print(or_number)
                    in_db = db.session.execute(db.select(LibraryUser).filter_by(user_id=or_number)).one_or_none()
                    if in_db:
                        #in_db.update(new_accounts.get_db_user_from_submitted_file(user))
                        print("updated")
                        counter += 1
                    else:
                        #add user
                        #problem with this function
                        new_accounts.add_db_user(new_accounts.get_db_user_from_submitted_file(user))
                        print("added")
                        counter += 1
                else:
                    print('something wrong')
            print(f'Counter: {counter}')
            print(len(users))


        def get_validation_file(request, filename):
            name = new_accounts.get_new_ILL_filename(filename)
            return name

class ImportValidationForm(UploadForm):
    submit = SubmitField("Send Validation File")

    def allowed_file(self, filename):
        ALLOWED_EXTENSIONS = {'txt'}
        return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
    
    def upload(request):
        if request.attachment.data:
            #maybe put a regex in here to check the file for errors
            #make a different function
            filename = secure_filename('UserValidation.txt')
            request.attachment.data.save(os.path.join(current_app.config['TRANSFER_FOLDER'], filename))

    def send_validation_file(request):
        filename = os.path.join(current_app.config['TRANSFER_FOLDER'], 'UserValidation.txt')
        with paramiko.SSHClient() as ssh:
            #ssh.load_system_host_keys()
            #change to config after verifying works
            ILLFTPHOST = '206.107.45.67'
            ILLFTPUSER =  'import'
            ILLFTPPASS = 'vW+7r#=Aer8gX#rm~'
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.connect(ILLFTPHOST, port=222, username=ILLFTPUSER, password=ILLFTPPASS)
            print(ssh)
            sftp = ssh.open_sftp()
            sftp.chdir('import')
            sftp.put(filename, 'UserValidation.txt')
        return True