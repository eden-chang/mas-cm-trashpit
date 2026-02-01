"""Flask API 진입점"""

import sys

# 상위 디렉토리 import를 위한 경로 추가
sys.path.insert(0, str(__file__).rsplit("\\", 2)[0])

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
