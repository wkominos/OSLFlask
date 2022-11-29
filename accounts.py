from app import create_app, db
from app.models import LibraryUser, User, Post

app = create_app()

@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'User': User, 'Post': Post, 'LibraryUser': LibraryUser}