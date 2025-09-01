
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, login_required, logout_user, current_user, UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = 'change-me'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///gym.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# Association table for group memberships
group_members = db.Table('group_members',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
    db.Column('group_id', db.Integer, db.ForeignKey('group.id'), primary_key=True)
)

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    progresses = db.relationship('Progress', backref='user', lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Group(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), unique=True, nullable=False)
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    members = db.relationship('User', secondary=group_members, backref=db.backref('groups', lazy='dynamic'))

class Progress(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    exercise = db.Column(db.String(120), nullable=False)
    weight = db.Column(db.Float, nullable=True)
    reps = db.Column(db.Integer, nullable=True)
    notes = db.Column(db.Text, nullable=True)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

with app.app_context():
    db.create_all()


@app.route('/')
@login_required
def index():
    recent_progress = Progress.query.filter_by(user_id=current_user.id).order_by(Progress.created_at.desc()).limit(20).all()
    return render_template('index.html', recent_progress=recent_progress)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()
        if not username or not password:
            flash('Username and password are required.')
            return redirect(url_for('register'))
        if User.query.filter_by(username=username).first():
            flash('Username already taken.')
            return redirect(url_for('register'))
        user = User(username=username)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        flash('Registration successful. Please log in.')
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()
        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            login_user(user)
            return redirect(url_for('index'))
        flash('Invalid credentials.')
        return redirect(url_for('login'))
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/progress/new', methods=['GET', 'POST'])
@login_required
def new_progress():
    if request.method == 'POST':
        exercise = request.form.get('exercise', '').strip()
        weight = request.form.get('weight', '').strip()
        reps = request.form.get('reps', '').strip()
        notes = request.form.get('notes', '').strip()

        if not exercise:
            flash('Exercise is required.')
            return redirect(url_for('new_progress'))

        weight_val = float(weight) if weight else None
        reps_val = int(reps) if reps else None

        p = Progress(user_id=current_user.id, exercise=exercise, weight=weight_val, reps=reps_val, notes=notes)
        db.session.add(p)
        db.session.commit()
        flash('Progress added.')
        return redirect(url_for('index'))
    return render_template('progress.html')

@app.route('/groups', methods=['GET', 'POST'])
@login_required
def groups():
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        if not name:
            flash('Group name is required.')
            return redirect(url_for('groups'))
        if Group.query.filter_by(name=name).first():
            flash('Group name already exists.')
            return redirect(url_for('groups'))
        g = Group(name=name, owner_id=current_user.id)
        g.members.append(current_user)
        db.session.add(g)
        db.session.commit()
        flash('Group created and joined.')
        return redirect(url_for('groups'))

    all_groups = Group.query.order_by(Group.created_at.desc()).all()
    return render_template('groups.html', all_groups=all_groups)

@app.route('/groups/<int:group_id>')
@login_required
def group_detail(group_id):
    g = Group.query.get_or_404(group_id)
    # Get recent progress for all members
    member_ids = [m.id for m in g.members]
    member_progress = Progress.query.filter(Progress.user_id.in_(member_ids)).order_by(Progress.created_at.desc()).limit(100).all()
    return render_template('group_detail.html', group=g, member_progress=member_progress)

@app.route('/groups/<int:group_id>/join', methods=['POST'])
@login_required
def join_group(group_id):
    g = Group.query.get_or_404(group_id)
    if current_user not in g.members:
        g.members.append(current_user)
        db.session.commit()
        flash('Joined group.')
    else:
        flash('You are already a member.')
    return redirect(url_for('group_detail', group_id=g.id))

@app.route('/groups/<int:group_id>/leave', methods=['POST'])
@login_required
def leave_group(group_id):
    g = Group.query.get_or_404(group_id)
    if current_user in g.members:
        g.members.remove(current_user)
        db.session.commit()
        flash('Left group.')
    else:
        flash('You are not a member.')
    return redirect(url_for('groups'))

@app.route('/testing-route/')
def test_route():
    return "<h1>New route is working...</h1>"

@app.route('/testing-route/<name>/')
def test_route2(name):
    return f"<h1>The route is working Mr.{name}!</h1>"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=80)
