import os
from flask import Flask, render_template, request, current_app
from flask_migrate import Migrate
from flask_wtf import CSRFProtect

from config import Config
from models import db, Case, Provider, Treatment

from routes.case_routes import case_bp
from routes.provider_routes import provider_bp
from routes.treatment_routes import treatment_bp

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    csrf = CSRFProtect(app)

    # --- 路径初始化部分 ---
    instance_path = os.path.join(app.config['BASE_DIR'], 'instance')
    upload_path = app.config.get('UPLOAD_FOLDER')

    # 确保 instance 和 upload 文件夹存在 (exist_ok=True 兼容 Docker 挂载)
    os.makedirs(instance_path, exist_ok=True)
    if upload_path:
        os.makedirs(upload_path, exist_ok=True)

    db.init_app(app)
    # 通过 'flask db migrate' 来更新数据库表结构
    migrate = Migrate(app, db)

    # 注册 Blueprints
    app.register_blueprint(case_bp)
    app.register_blueprint(provider_bp)
    app.register_blueprint(treatment_bp)

    @app.route('/')
    def index():
        cases = Case.query.filter_by(is_hidden=False).order_by(
            Case.rank.asc(),  # 升序（1在最前）
            Case.upload_date.desc()  # 当权重相同时，按日期倒序
        ).limit(4).all()

        providers = Provider.query.filter_by(is_hidden=False).order_by(Provider.rank.asc()).all()

        return render_template('index.html',
                               cases=cases,
                               providers=providers,
                               admin_key=app.config['ADMIN_KEY'])

    @app.route('/gallery')
    def gallery():
        all_cases = Case.query.filter_by(is_hidden=False).order_by(Case.upload_date.desc()).all()
        return render_template('gallery.html', cases=all_cases)

    @app.route('/about-us')
    def about():
        providers = Provider.query.filter_by(is_hidden=False).order_by(Provider.rank.asc()).all()
        return render_template('about-us.html', providers=providers)

    @app.route('/treatments')
    def treatments():
        # Rank 相同，按 ID 倒序
        all_treatments = Treatment.query.filter_by(is_active=True).order_by(
            Treatment.display_order.asc(),
            Treatment.id.desc()
        ).all()
        return render_template('treatments.html', treatments=all_treatments)

    @app.route('/secret_admin')
    def admin():
        if request.args.get('key') != app.config['ADMIN_KEY']:
            return "Unauthorized Access", 403

        page = request.args.get('page', 1, type=int)

        cases_pagination = Case.query.order_by(
            Case.rank.asc(),
            Case.upload_date.desc()
        ).paginate(page=page, per_page=10)

        existing_tags = db.session.query(Case.tag).distinct().all()
        case_tags = [t[0] for t in existing_tags if t[0] and t[0].strip()]

        providers = Provider.query.all()

        t_page = request.args.get('t_page', 1, type=int)
        treatments_pagination = (Treatment.query.order_by(Treatment.display_order.asc())
                                 .paginate(page=t_page, per_page=5))
        existing_categories = db.session.query(Treatment.category).distinct().all()
        categories = [c[0] for c in existing_categories if c[0]]

        return render_template('admin.html',
                               cases_pagination=cases_pagination,
                               treatments_pagination=treatments_pagination,
                               providers=providers,
                               categories=categories,
                               case_tags=case_tags,
                               admin_key=app.config['ADMIN_KEY'])

    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('404.html'), 404

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)