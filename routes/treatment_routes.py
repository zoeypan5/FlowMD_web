import os
from flask import Blueprint, request, redirect, url_for, current_app, render_template
from models import db, Treatment
from werkzeug.utils import secure_filename

treatment_bp = Blueprint('treatment', __name__)


@treatment_bp.route('/hide_treatment/<int:id>')
def hide_treatment(id):
    if request.args.get('key') != current_app.config['ADMIN_KEY']:
        return "Unauthorized", 403

    t = Treatment.query.get_or_404(id)
    t.is_active = not t.is_active

    db.session.commit()
    return redirect(url_for('admin', key=current_app.config['ADMIN_KEY']))

@treatment_bp.route('/admin/treatment/add', methods=['POST'])
def add_treatment():
    if request.args.get('key') != current_app.config['ADMIN_KEY']:
        return "Unauthorized", 403

    file = request.files.get('image')
    filename = ""
    if file and file.filename:
        filename = secure_filename(file.filename)
        file.save(os.path.join(current_app.config['UPLOAD_FOLDER'], filename))

    new_t = Treatment(
        name=request.form.get('name'),
        category=request.form.get('category'),
        short_description=request.form.get('short_description'),
        full_description=request.form.get('full_description'),
        display_order=request.form.get('display_order', 0),
        image=filename,
        is_active=True
    )
    db.session.add(new_t)
    db.session.commit()
    return redirect(url_for('admin', key=current_app.config['ADMIN_KEY']))


@treatment_bp.route('/admin/treatment/edit/<int:id>', methods=['GET', 'POST'])
def edit_treatment(id):
    treatment = Treatment.query.get_or_404(id)
    admin_key = current_app.config['ADMIN_KEY']

    if request.args.get('key') != admin_key:
        return "Unauthorized", 403

    if request.method == 'POST':
        treatment.name = request.form.get('name')
        treatment.category = request.form.get('category')
        treatment.display_order = request.form.get('display_order', 0)
        treatment.short_description = request.form.get('short_description')
        treatment.full_description = request.form.get('full_description')

        # 如果上传了新图片
        file = request.files.get('image')
        if file and file.filename:
            filename = secure_filename(file.filename)
            file.save(os.path.join(current_app.config['UPLOAD_FOLDER'], filename))
            treatment.image = filename

        db.session.commit()
        return redirect(url_for('admin', key=admin_key))

    return render_template('edit_treatment.html', treatment=treatment, admin_key=admin_key)


@treatment_bp.route('/admin/treatment/delete/<int:id>')
def delete_treatment(id):
    if request.args.get('key') != current_app.config['ADMIN_KEY']:
        return "Unauthorized", 403
    t = Treatment.query.get_or_404(id)
    db.session.delete(t)
    db.session.commit()
    return redirect(url_for('admin', key=current_app.config['ADMIN_KEY']))