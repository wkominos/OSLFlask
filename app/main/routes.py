from flask import render_template, flash, redirect, url_for, request, jsonify, send_file
from app import db
from app.main.forms import ImportValidationForm, ValidationForm
from flask_login import current_user, login_user, logout_user, login_required
from app.main import bp


@bp.route('/', methods=['GET', 'POST'])
@bp.route('/main/index', methods=['GET', 'POST'])
def index():
        validation_form = ValidationForm(formdata=None)
        import_form = ImportValidationForm()
        return render_template('index.html', form=validation_form, import_form=import_form) 

@bp.route('/main/validation', methods=['POST'])
def validation_file():
        validation_form = ValidationForm()
        import_form = ImportValidationForm()
        if validation_form.validate_on_submit():
                if validation_form.attachment.data:
                        if validation_form.allowed_file(validation_form.attachment.data.filename):
                                validation_form.upload()
                                filename = validation_form.get_filename()
                                validation_form.create_validation_file(validation_form.parse_ILL_users_file(filename), filename)
                                name = validation_form.get_validation_file(filename)
                                try:
                                        validation_form.db_user(validation_form.parse_ILL_users_file(filename))
                                        db.session.commit()
                                except:
                                        flash('Database Error: Could not commit to database')
                                return send_file(name, as_attachment=True)
                        else:
                                flash('Wrong filetype')
                                return redirect(url_for("main.index"))
                else:
                        flash('No file attached in request')
                        return redirect(url_for("main.index"))
        return render_template('index.html', form=ValidationForm(formdata=None), import_form=import_form)

@bp.route('/main/import', methods=['POST'])
def import_file():
        validation_form = ValidationForm(formdata=None)
        import_form = ImportValidationForm()
        if import_form.validate_on_submit():
                if import_form.attachment.data:
                        if import_form.allowed_file(import_form.attachment.data.filename):
                                filename = import_form.get_filename()
                                print(filename)
                                import_form.upload()
                                try:
                                        import_form.send_validation_file()
                                        flash('Success')
                                        return redirect(url_for("main.index"))
                                except:
                                        flash("FTP transfer failed")
                                        return redirect(url_for("main.index"))
                        else:
                                flash('Wrong filetype')
                                return redirect(url_for("main.index"))
                else:
                        flash('No file attached in request')
                        return redirect(url_for("main.index"))
        return render_template('index.html', form=validation_form, import_form=import_form) 