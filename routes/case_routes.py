import os
import time  # 用于生成时间戳解决重名问题
from flask import Blueprint, request, redirect, url_for, current_app
from werkzeug.utils import secure_filename
from models import db, Case

case_bp = Blueprint('case', __name__)


@case_bp.route('/add_case', methods=['POST'])
def add_case():
    if request.args.get('key') != current_app.config['ADMIN_KEY']:
        return "Unauthorized", 403

    title = request.form.get('title')
    desc = request.form.get('description')
    tag = request.form.get('tag', 'General')

    raw_rank = request.form.get('rank')
    try:
        rank = int(raw_rank) if raw_rank else 10
    except (ValueError, TypeError):
        rank = 10

    before = request.files.get('before')
    after = request.files.get('after')

    if before and after:
        timestamp = int(time.time())

        b_filename = f"{timestamp}_{secure_filename(before.filename)}"
        before.save(os.path.join(current_app.config['UPLOAD_FOLDER'], b_filename))
        a_filename = f"{timestamp}_{secure_filename(after.filename)}"
        after.save(os.path.join(current_app.config['UPLOAD_FOLDER'], a_filename))

        new_case = Case(
            title=title,
            description=desc,
            before_img=b_filename,
            after_img=a_filename,
            rank=rank,
            tag=tag
        )
        db.session.add(new_case)
        db.session.commit()

    return redirect(url_for('admin', key=current_app.config['ADMIN_KEY']))


@case_bp.route('/delete_case/<int:id>')
def delete_case(id):
    if request.args.get('key') != current_app.config['ADMIN_KEY']:
        return "Unauthorized", 403
    case = Case.query.get_or_404(id)

    # 如果需要物理删除服务器上的图片文件，可以在这里加上 os.remove
    db.session.delete(case)
    db.session.commit()
    return redirect(url_for('admin', key=current_app.config['ADMIN_KEY']))


@case_bp.route('/hide_case/<int:id>')
def hide_case(id):
    if request.args.get('key') != current_app.config['ADMIN_KEY']:
        return "Unauthorized", 403
    case = Case.query.get_or_404(id)
    case.is_hidden = not case.is_hidden
    db.session.commit()
    return redirect(url_for('admin', key=current_app.config['ADMIN_KEY']))


@case_bp.route('/edit_case/<int:id>', methods=['POST'])
def edit_case(id):
    if request.args.get('key') != current_app.config['ADMIN_KEY']:
        return "Unauthorized", 403

    case = Case.query.get_or_404(id)

    case.title = request.form.get('title')
    case.description = request.form.get('description')
    case.tag = request.form.get('tag', 'General')  # 默认值General

    # 保存 rank 权重字段
    new_rank = request.form.get('rank')
    if new_rank:
        try:
            case.rank = int(new_rank)
        except ValueError:
            case.rank = 10

    db.session.commit()
    return redirect(url_for('admin', key=current_app.config['ADMIN_KEY']))