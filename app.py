from flask import Flask, redirect, request
from flask_sqlalchemy import SQLAlchemy
from flask_limiter import Limiter
import os
import threading

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = (
    f"mysql+pymysql://{os.environ['DB_USER']}:{os.environ['DB_PASS']}@{os.environ['DB_HOST']}:{os.environ['DB_PORT']}/{os.environ['DB_NAME']}"
    f'?ssl_ca={os.path.abspath("ca.pem")}'
    f'&ssl_cert={os.path.abspath("client-cert.pem")}'
    f'&ssl_key={os.path.abspath("client-key.pem")}'
)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ENCODING'] = "utf8mb4"
db = SQLAlchemy(app)


class ShortURL(db.Model):
    __tablename__ = 'url'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    key = db.Column(db.String(10), unique=True, nullable=False)
    longurl = db.Column(db.String(2048), nullable=False)
    visit_count = db.Column(db.Integer, default=0)


class CatLog(db.Model):
    __tablename__ = 'log'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    key = db.Column(db.String(10), nullable=False)
    time = db.Column(db.DateTime, nullable=False)
    ip = db.Column(db.String(45), nullable=False)
    ua = db.Column(db.String(512), nullable=False)
    referer = db.Column(db.String(2048), nullable=True)


def get_real_ip():
    if request.headers.get('X-Forwarded-For'):
        # 可能有多个IP，取第一个
        return request.headers.get('X-Forwarded-For').split(',')[0].strip()
    elif request.headers.get('X-Real-IP'):
        return request.headers.get('X-Real-IP')
    else:
        return request.remote_addr

def async_log(cat_log):
    with app.app_context():
        db.session.add(cat_log)
        db.session.commit()


limiter = Limiter(
    key_func=get_real_ip,
    app=app,
    default_limits=["50 per hour", "8 per minute"]
)


@app.route('/<short_code>')
def redirect_to_url(short_code):
    short_url = ShortURL.query.filter_by(key=short_code).first()
    # Log the access
    cat_log = CatLog(
        key=short_code,
        time=db.func.now(),
        ip=get_real_ip(),
        ua=request.headers.get('User-Agent', None),
        referer=request.headers.get('Referer', None)
    )
    if short_url:
        short_url.visit_count += 1
        db.session.commit()
        threading.Thread(target=async_log, args=(cat_log,)).start()
        return redirect(short_url.longurl)
    else:
        threading.Thread(target=async_log, args=(cat_log,)).start()
        return redirect('https://www.g2022cyk.top/404.html')


@app.route('/')
def home():
    return redirect('https://www.g2022cyk.top')


@app.route('/sitemap.xml')
def sitemap_xml():
    # 记录日志
    cat_log = CatLog(
        key='sitemap',
        time=db.func.now(),
        ip=get_real_ip(),
        ua=request.headers.get('User-Agent', None),
        referer=request.headers.get('Referer', None)
    )
    threading.Thread(target=async_log, args=(cat_log,)).start()
    return redirect('https://www.g2022cyk.top/sitemap.xml')


@app.route('/sitemap.txt')
def sitemap_txt():
    # 记录日志
    cat_log = CatLog(
        key='sitemap',
        time=db.func.now(),
        ip=get_real_ip(),
        ua=request.headers.get('User-Agent', None),
        referer=request.headers.get('Referer', None)
    )
    threading.Thread(target=async_log, args=(cat_log,)).start()
    return redirect('https://www.g2022cyk.top/sitemap.txt')


@app.route('/robots.txt')
# 允许爬虫抓取
def robots_txt():
    # 记录日志
    cat_log = CatLog(
        key='robots',
        time=db.func.now(),
        ip=get_real_ip(),
        ua=request.headers.get('User-Agent', None),
        referer=request.headers.get('Referer', None)
    )
    threading.Thread(target=async_log, args=(cat_log,)).start()
    return '''User-agent: *
Allow: /'''


@app.route('/ads.txt')
def ads_txt():
    # 记录日志
    cat_log = CatLog(
        key='ads',
        time=db.func.now(),
        ip=get_real_ip(),
        ua=request.headers.get('User-Agent', None),
        referer=request.headers.get('Referer', None)
    )
    threading.Thread(target=async_log, args=(cat_log,)).start()
    return redirect('https://www.g2022cyk.top/ads.txt')


@app.errorhandler(429)
def ratelimit_handler(e):
    return "ILGLR AMNS", 429


if __name__ == '__main__':
    app.run(debug=True)
