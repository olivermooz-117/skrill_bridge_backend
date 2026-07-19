from app import create_app
from app.extensions import db
from app.models import User, Gig, Order, Review, Tag

app = create_app()

# THIS LINE IS THE FIX - Creates tables on startup
with app.app_context():
    db.create_all()
    print("✅ Database tables verified")

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)