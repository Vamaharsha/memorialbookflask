from app import app, db
from flask_migrate import Migrate

migrate = Migrate(app, db)

# Optional: This lets you use "flask shell" with app/db pre-imported
@app.shell_context_processor
def make_shell_context():
    return {'db': db}
