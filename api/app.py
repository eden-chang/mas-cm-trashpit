"""Flask API 진입점"""

import os
import sys

# 프로젝트 루트를 path에 추가 (Railway 등에서 api/ 폴더를 루트로 실행해도 동작)
_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

from flask import Flask
from flask_cors import CORS

from api.config import DEBUG, HOST, PORT, CORS_ORIGINS
from api.routes import character, bag, nearby, items, admin

app = Flask(__name__)
CORS(app, origins=CORS_ORIGINS)

# 라우트 등록
app.register_blueprint(character.bp)
app.register_blueprint(bag.bp)
app.register_blueprint(nearby.bp)
app.register_blueprint(items.bp)
app.register_blueprint(admin.bp)


@app.route("/")
def index():
    return {"status": "ok", "message": "Trashpit Inventory API"}


@app.route("/health")
def health():
    return {"status": "healthy"}


if __name__ == "__main__":
    app.run(host=HOST, port=PORT, debug=DEBUG)
