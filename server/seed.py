from app import app, db, bcrypt
from models import User, Article

with app.app_context():
    db.drop_all()
    db.create_all()

    # Create a test user
    user = User(
        username="testuser",
        password_hash=bcrypt.generate_password_hash("password123").decode("utf-8")
    )
    db.session.add(user)

    # Public Articles
    public1 = Article(
        author="Admin",
        title="Welcome to Our Blog",
        content="This article is free for everyone.",
        preview="Intro to our blog",
        minutes_to_read=2,
        is_member_only=False,
        user=user
    )

    public2 = Article(
        author="Admin",
        title="Getting Started",
        content="Here are some tips to get started.",
        preview="Helpful guide for new users",
        minutes_to_read=3,
        is_member_only=False,
        user=user
    )

    # Member-Only Articles
    member1 = Article(
        author="Admin",
        title="Exclusive Member Insights",
        content="Only members can see this detailed article.",
        preview="Premium content preview",
        minutes_to_read=5,
        is_member_only=True,
        user=user
    )

    member2 = Article(
        author="Admin",
        title="Advanced Tips & Tricks",
        content="A collection of powerful strategies for our members.",
        preview="Advanced strategies preview",
        minutes_to_read=6,
        is_member_only=True,
        user=user
    )

    db.session.add_all([public1, public2, member1, member2])
    db.session.commit()

    print("Database seeded successfully!")
