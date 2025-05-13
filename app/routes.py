from functools import wraps
from io import BytesIO

from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from werkzeug.security import check_password_hash
from matplotlib.pyplot import close
from requests import get, post, delete

from app.extensions import db
from app.models import User, Follows
from app.forms import SignupForm, LoginForm, UploadForm, FollowForm
from app.services import Parser, registry, read_csv, save_to_string


bp = Blueprint('routes', __name__)


# ---------------------------------------------------------------------------------------------------------------------
# Utilities
#

@bp.after_request
def add_header(response):
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '-1'
    return response


# Login required decorator
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('You need to log in to access this page.')
            return redirect(url_for('routes.login'))
        return f(*args, **kwargs)

    return decorated_function


# ---------------------------------------------------------------------------------------------------------------------
# Auth routes
#

@bp.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if not user:
            flash('This email is not registered.', 'error')
            return render_template('login.html', form=form)
        if not check_password_hash(user.password, form.password.data):
            flash('Incorrect password.', 'error')
            return render_template('login.html', form=form)

        session['user_id'] = user.id
        flash('Login successful!', 'success')

        return redirect(url_for('routes.dashboard'))
 
    return render_template('login.html', form=form)


@bp.route('/signup', methods=['GET', 'POST'])
def signup():
    form = SignupForm()
    if form.validate_on_submit():
        existing_user = User.query.filter_by(email=form.email.data).first()
        if existing_user:
            flash('Email already registered.', 'error')
            return redirect(url_for('routes.signup'))

        new_user = User(
            fullname=form.name.data,
            email=form.email.data
        )
        new_user.set_password(form.password.data)
        db.session.add(new_user)
        db.session.commit()

        flash('Signup successful!', 'success')
        return redirect(url_for('routes.login'))

    return render_template('signup.html', form=form)


@bp.route('/logout')
def logout():
    session.pop('user_id', None)
    flash('Logout successful!', 'success')
    return redirect(url_for('routes.login'))


# ---------------------------------------------------------------------------------------------------------------------
# User/Profile routes
#

@bp.route('/profile')
@login_required
def profile():
    user = User.query.get(session['user_id'])
    return render_template('profile.html', user=user)


@bp.route('/edit-profile', methods=['GET', 'PATCH'])
@login_required
def edit_profile():
    if request.method == 'PATCH':
        # Handle form submission (e.g., save updated profile data)
        name = request.form.get('name')
        email = request.form.get('email')
        # Save the data (this is just a placeholder, implement actual services)
        print(f"Updated Name: {name}, Updated Email: {email}")
        return redirect('/profile')  # Redirect back to the profile page after saving

    return render_template("edit_profile.html")


@bp.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    return render_template('settings.html')


# ---------------------------------------------------------------------------------------------------------------------
# Landing routes
#

@bp.route('/')
def index():
    return render_template("index.html")


@bp.route('/dashboard')
@login_required
def dashboard():
    return render_template("dashboard.html")


# ---------------------------------------------------------------------------------------------------------------------
# Social routes
#

@bp.route('/friends', methods=['GET'])
@login_required
def friends():
    full_url = request.host_url.rstrip('/') + url_for('follows.get_follows')
    response = get(full_url)
    friends = response.json()['friends']
    return render_template('friends.html', friends=friends)


@bp.route('/add-friend', methods=['GET', 'POST'])
@login_required
def add_friend():
    form = FollowForm()
    if form.validate_on_submit():
        if request.method == 'POST':
            target_user = User.query.filter_by(id=form.user_id.data).first()
                
            if not target_user:
                flash("User ID not found.", "error")
            elif target_user.id == session['user_id']:
                flash("You cannot add yourself as a friend.", "error")
            else:
                existing = Follows.query.filter_by(follower=session['user_id'], following=target_user.id).first()
                if existing:
                    flash("This user is already your friend.", "info")
                else:
                    full_url = request.host_url.rstrip('/') + url_for('follows.follow', target_id=target_user.id)
                    response = post(full_url)
                    if response.status_code == 201:
                        flash(f"User '{target_user.fullname}' followed successfully!", "success")
                    else:
                        flash(f"Error {response.status_code}", "error")

    return render_template('add_friend.html')

@bp.route('/unfriend/<int:friend_id>', methods=['GET', 'DELETE'])
@login_required
def unfriend(friend_id):
    if request.method == 'DELETE':
        current_user_id = session['user_id']
        relation = Follows.query.filter_by(follower=current_user_id, following=friend_id).first()

        if relation:
            full_url = request.host_url.rstrip('/') + url_for('follows.unfollow', target_id=relation.following)
            response = delete(full_url)
            if response.status_code == 204:
                flash("User unfollowed successfully!", "success")
            else:
                flash(f"Error {response.status_code}", "error")
        else:
            flash("Friend not found.", "error")

        return redirect(url_for('routes.friends'))


# ---------------------------------------------------------------------------------------------------------------------
# Business routes
#

@bp.route('/upload', methods=['GET', 'POST'])
@login_required
def upload():
    form = UploadForm()
    chart = None

    # returns True if the method is POST and the field conforms to all validators
    if form.validate_on_submit():

        # parses primitive frame data into useful constructs
        data = read_csv(BytesIO(form.file.data.read()))
        spec = Parser.parse_string(form.spec.data)

        if 'type' not in spec:
            raise Exception('Need a type')

        plot_type = spec.pop('type')
        plot_type = plot_type[0] if isinstance(plot_type, list) else plot_type

        plotter = registry.functions[plot_type]

        # TODO: Catch errors and report the message to the user
        bound, unbound = plotter.bind_args(source=data, **spec)

        if unbound:
            # TODO: Flash these messages to the user so that they can understand why their
            # option isn't doing anything. Maybe make `unbound` also offer near matches?
            print(unbound)

        # generates a base64 encoding of a png so that we don't have to save locally
        figure = plotter.function(**bound)
        image = save_to_string(figure)
        close(figure)

        # this boilerplate is necessary to get the browser to interpret the string as a png
        chart = f"data:image/png;base64,{image}"

    return render_template('upload.html', form=form, chart=chart)


@bp.route('/visualise', methods=['GET', 'POST'])
@login_required
def visualise():
    chart = None

    # This just needs to be reworked
    #
    #    if request.method == 'GET':
    #        # Handle visualization services here
    #        x_col = request.args.get('xCol')
    #        y_col = request.args.get('yCol')
    #        chart_type = request.args.get('chartType')
    #        title = request.args.get('title', 'Visualization')
    #        color = request.args.get('color', 'blue')
    #        grid = request.args.get('grid', '1') == '1'
    #        figsize = tuple(map(int, request.args.get('figsize', '10,6').split(',')))
    #
    #        # Generate the chart using your existing plotting functions
    #        if x_col and y_col and chart_type:
    #            if chart_type == 'line':
    #                chart = plots.plot_line(x_col, y_col, title=title, color=color, grid=grid, figsize=figsize)
    #            elif chart_type == 'bar':
    #                chart = plots.plot_bar(x_col, y_col, title=title, color=color, grid=grid, figsize=figsize)
    #            # Add other chart types here...

    return render_template('visualise.html', chart=chart)


@bp.route('/analytics')
@login_required
def analytics():
    return render_template('analytics.html')
