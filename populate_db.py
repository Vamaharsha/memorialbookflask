from app import app, db, bcrypt, User

def create_user(roll, name, email, plain_password, user_type, batch, branch, section, **kwargs):
    hashed_pw = bcrypt.generate_password_hash(plain_password).decode('utf-8')
    return User(
        roll_number=roll,
        name=name,
        email=email,
        password=hashed_pw,
        user_type=user_type,
        batch_year=batch,
        branch=branch,
        section=section,
        **kwargs
    )

with app.app_context():
    print("🔁 Dropping all tables...")
    db.drop_all()
    print("✅ Creating tables...")
    db.create_all()

    print("👥 Populating users...")
    users = [
        create_user('22A81A0532', 'Nikhil Rao', 'nikhil@example.com', 'password123', 'graduated', 2024, 'CSE', 'A'),
        create_user('22A81A0564', 'Sofia Khan', 'sofia@example.com', 'password123', 'graduated', 2024, 'CSE', 'A'),
        create_user('22A81A0567', 'koushik', 'koushik@example.com', 'password123', 'graduated', 2024, 'CSE', 'B')
        # Add more users as needed
    ]

    # Sample users per branch & year
    branches = ['CSE', 'ECE', 'CST', 'MECH','CIVIL','ECT','AML','CAI','EEE']
    batches = [2023, 2024, 2025]
    counter = 1
    for year in batches:
        for branch in branches:
            roll = f"{year}{branch}{counter:03}"
            name = f"{branch} Student {counter}"
            email = f"{branch.lower()}.{counter}@example.com"
            users.append(create_user(roll, name, email, 'password123', 'graduated', year, branch, 'A'))
            counter += 1

    db.session.add_all(users)
    db.session.commit()
    print("✅ Users inserted successfully!")
