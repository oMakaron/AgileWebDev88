from functools import wraps
from io import BytesIO, StringIO
import pandas as pd
import json
import os, uuid
from flask import (
    Blueprint, render_template, redirect, url_for, flash,
    session, current_app, request
)
from werkzeug.security import check_password_hash
from werkzeug.utils import secure_filename
from matplotlib.pyplot import close
from app.extensions import db
from app.models import User, Chart, File
from app.models.friend import Friend
from app.models.notification import Notification
from app.models.shared_data import SharedData
from app.models.associations import SharedChart
from app.forms import SignupForm, LoginForm, UploadForm, ChartForm, AddFriendForm
from app.services import Parser, registry, read_csv, save_to_string, save_figure_to_file

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

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('You need to log in to access this page.', 'error')
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
        if not user or not check_password_hash(user.password, form.password.data):
            flash('Invalid email or password.', 'error')
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

        new_user = User(fullname=form.name.data, email=form.email.data)
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
# Main Pages

@bp.route('/')
def index():
    return render_template("index.html")

@bp.route('/dashboard')
@login_required
def dashboard():
    charts = Chart.query.filter_by(owner_id=session['user_id']).all()
    return render_template("dashboard.html", charts=charts)

@bp.route('/profile')
@login_required
def profile():
    user = User.query.get(session['user_id'])
    return render_template("profile.html", user=user)

from app.forms import EditProfileForm

@bp.route('/edit-profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    user = User.query.get(session['user_id'])
    form = EditProfileForm()
    if form.validate_on_submit():
        user.fullname = form.name.data
        user.email = form.email.data
        if form.password.data:
            user.set_password(form.password.data)
        db.session.commit()
        flash('Profile updated successfully!', 'success')
        return redirect(url_for('routes.profile'))

    form.name.data = user.fullname
    form.email.data = user.email
    return render_template("edit_profile.html", form=form)

@bp.route('/settings')
@login_required
def settings():
    user = db.session.get(User, session['user_id'])
    return render_template('settings.html', user=user)

@bp.route('/delete-account', methods=['POST'])
@login_required
def delete_account():
    user_id = session['user_id']

    with db.session.no_autoflush:
        charts = Chart.query.filter_by(owner_id=user_id).all()
        for chart in charts:
            db.session.delete(chart)

        SharedData.query.filter_by(shared_by_user_id=user_id).delete(synchronize_session=False)
        SharedData.query.filter_by(shared_with_user_id=user_id).delete(synchronize_session=False)

        user = User.query.get(user_id)
        db.session.delete(user)

    db.session.commit()
    session.clear()
    flash("Your account and related data have been deleted.", "success")
    return redirect(url_for('routes.login'))



@bp.route('/friends')
@login_required
def friends():
    return render_template('friends.html')

@bp.route('/add-friend', methods=['GET', 'POST'])
@login_required
def add_friend():
    return render_template('add_friend.html')

@bp.route('/share/<int:chart_id>', methods=['GET', 'POST'])
@login_required
def share_chart(chart_id):
    user_id = session['user_id']
    chart = Chart.query.filter_by(id=chart_id, owner_id=user_id).first()
    if not chart:
        flash("You can only share your own charts.")
        return redirect(url_for('routes.dashboard'))

    if request.method == 'POST':
        shared_ids = request.form.getlist('shared_with')
        for fid in shared_ids:
            entry = SharedChart(
                chart_id=chart.id,
                shared_with_user_id=fid,
                shared_by_user_id=user_id
            )
            db.session.add(entry)
        db.session.commit()
        flash("Chart shared successfully.")
        return redirect(url_for('routes.dashboard'))

    friends = get_friends(user_id)
    return render_template('share.html', chart=chart, friends=friends)

@bp.route('/share-data/<int:friend_id>', methods=['GET', 'POST'])
@login_required
def share_data_with_friend(friend_id):
    user_id = session['user_id']
    charts = Chart.query.filter_by(owner_id=user_id).all()
    chart_id = None 

    if request.method == 'POST':
        chart_id = request.form.get('chart_id')

        if not chart_id:
            flash("Please select a chart to share.", "error")
            return redirect(url_for('routes.share_data_with_friend', friend_id=friend_id))

        already_shared = SharedData.query.filter_by(
            chart_id=chart_id,
            shared_with_user_id=friend_id,
            shared_by_user_id=user_id
        ).first()

        if already_shared and request.form.get('confirm') != 'yes':
            return render_template("share_data.html", charts=charts, friend_id=friend_id, confirm_chart_id=chart_id)

        new_share = SharedData(
            chart_id=chart_id,
            shared_with_user_id=friend_id,
            shared_by_user_id=user_id
        )
        db.session.add(new_share)

        chart = Chart.query.get(chart_id)
        sharer = User.query.get(user_id)
        notification = Notification(
            user_id=friend_id,
            message=f"{sharer.fullname} shared a chart with you: {chart.name}"
        )
        db.session.add(notification)

        db.session.commit()
        flash("Chart shared successfully!", "success")
        return redirect(url_for('routes.friends'))

    return render_template("share_data.html", charts=charts, friend_id=friend_id)



@bp.route('/message-received')
@login_required
def shared_with_me():
    user_id = session['user_id']

    shared_charts = (
        db.session.query(Chart)
        .join(SharedData, SharedData.chart_id == Chart.id)
        .filter(SharedData.shared_with_user_id == user_id)
        .all()
    )

    return render_template("shared_with_me.html", charts=shared_charts)



# ---------------------------------------------------------------------------------------------------------------------
# Generate Graph Route

@bp.route('/generate-graph', methods=['GET', 'POST'])
@login_required
def generate_graph():
    upload_form = UploadForm(prefix='up')
    chart_form = ChartForm(prefix='ch', formdata=request.form)
    chart_src = None
    show_config = False
    data = None

    # Handle CSV upload
    if upload_form.submit_upload.data and upload_form.validate_on_submit():
        raw = upload_form.file.data.read()
        df = read_csv(BytesIO(raw))

        filename = secure_filename(upload_form.file.data.filename)
        uploads_folder = current_app.config['UPLOADS_FOLDER']
        os.makedirs(uploads_folder, exist_ok=True)

        saved_name = f"{uuid.uuid4().hex}_{filename}"
        file_path = os.path.join(uploads_folder, saved_name)
        with open(file_path, 'wb') as f:
            f.write(raw)

        session['csv_string'] = raw.decode('utf-8')
        session['columns'] = df.columns.tolist()
        session['uploaded_filename'] = filename

        new_file = File(name=filename, owner_id=session['user_id'])
        db.session.add(new_file)
        db.session.commit()
        session['file_id'] = new_file.id

        return redirect(url_for('routes.generate_graph'))

    # Load file if already uploaded
    if 'file_id' in session:
        file = File.query.get(session['file_id'])
        if file:
            uploads_folder = current_app.config['UPLOADS_FOLDER']
            pattern = f"_{file.name}"
            matching = [f for f in os.listdir(uploads_folder) if f.endswith(pattern)]
            if matching:
                file_path = os.path.join(uploads_folder, matching[0])
                data = pd.read_csv(file_path)
                cols = data.columns.tolist()
                chart_form.x_col.choices = [('', '– Select X –')] + [(c, c) for c in cols]
                chart_form.y_col.choices = [('', '– Select Y –')] + [(c, c) for c in cols]
                chart_form.column.choices = [('', '– Select column –')] + [(c, c) for c in cols]
                show_config = True
            else:
                flash("Uploaded file is missing. Please re-upload.", "error")
                session.clear()

    # Handle preview chart
    if data is not None and chart_form.submit_generate.data and chart_form.validate_on_submit():
        spec = {'source': data}
        for fld in ['title', 'x_label', 'y_label', 'color', 'grid']:
            v = getattr(chart_form, fld).data
            if v:
                spec[fld] = v
        if chart_form.figsize.data:
            try:
                w, h = map(int, chart_form.figsize.data.split('x'))
                spec['figsize'] = (w, h)
            except ValueError:
                flash("Invalid figure size. Use e.g. 10x6", 'warning')

        t = chart_form.graph_type.data
        spec['graph_type'] = t
        if t in ['line', 'bar', 'scatter', 'area', 'box']:
            spec['x_col'], spec['y_col'] = chart_form.x_col.data, chart_form.y_col.data
        else:
            spec['column'] = chart_form.column.data

        bind_spec = spec.copy()
        bind_spec.pop('graph_type', None)

        bound, _ = registry.functions[t].bind_args(**bind_spec)
        fig = registry.functions[t].function(**bound)
        raw_b64 = save_to_string(fig)
        close(fig)

        chart_src = f"data:image/png;base64,{raw_b64}"
        store_spec = spec.copy()
        store_spec.pop('source', None)
        session['last_spec'] = json.dumps(store_spec)

        # For optional alternate flow (e.g., saving without re-generating)
        session['pending_chart'] = {
            'name': spec.get('title') or 'Untitled',
            'spec': json.dumps(store_spec),
            'image_data': raw_b64,
            'file_id': session.get('file_id')
        }

    # Handle save chart
    elif request.method == 'POST' and request.form.get('submit_save'):
        name = request.form.get("name") or "Untitled"
        spec = request.form.get("spec") or "{}"
        image_data = request.form.get("image_data")
        file_id = request.form.get("file_id")

        if not image_data:
            flash("No chart to save.", "error")
            return redirect(url_for('routes.generate_graph'))

        chart = Chart(
            name=name,
            owner_id=session['user_id'],
            file_id=file_id,
            spec=spec,
            image_data=image_data
        )
        db.session.add(chart)
        db.session.commit()

        flash("Chart saved to dashboard!", "success")
        return redirect(url_for('routes.dashboard'))

    return render_template(
        'generate-graph.html',
        upload_form=upload_form,
        chart_form=chart_form,
        show_config=show_config,
        chart_src=chart_src,
        uploaded_filename=session.get('uploaded_filename')
    )


@bp.route('/save-chart', methods=['POST'])
@login_required
def save_chart():
    pending = session.get('pending_chart')
    if not pending:
        flash("No chart to save.", "error")
        return redirect(url_for('routes.generate_graph'))

    chart = Chart(
        name       = pending['name'],
        owner_id   = session['user_id'],
        file_id    = pending.get('file_id'),
        spec       = pending['spec'],
        image_data = pending['image_data']
    )
    db.session.add(chart)
    db.session.commit()
    session.pop('pending_chart', None)

    flash("Chart saved to dashboard!", "success")
    return redirect(url_for('routes.dashboard'))


# --------------------------------------------------------------------------------------------------------------------
# Delete Graph Route

@bp.route('/charts/<int:chart_id>/delete', methods=['POST'])
@login_required
def delete_chart(chart_id):
    chart = Chart.query.filter_by(id=chart_id, owner_id=session['user_id']).first()
    if not chart:
        flash("Chart not found or not authorized.", "error")
        return redirect(url_for('routes.dashboard'))

    # Store file info before deleting chart
    file = chart.file
    file_name = file.name
    uploads_folder = current_app.config['UPLOADS_FOLDER']
    pattern = f"_{file_name}"

    # Delete the image file from disk
    if chart.image_path:
        image_path = os.path.join(current_app.root_path, 'static', 'chart_images', os.path.basename(chart.image_path))
        if os.path.exists(image_path):
            os.remove(image_path)

    # Delete chart from database
    db.session.delete(chart)
    db.session.commit()

    # If no charts remain that reference this file, delete the file
    if not file.charts:
        matching = [f for f in os.listdir(uploads_folder) if f.endswith(pattern)]
        for f in matching:
            try:
                os.remove(os.path.join(uploads_folder, f))
            except Exception as e:
                current_app.logger.warning(f"Failed to delete file {f}: {e}")
        db.session.delete(file)
        db.session.commit()

    flash("Chart and associated file (if unused) deleted successfully.", "success")
    return redirect(url_for('routes.dashboard'))
