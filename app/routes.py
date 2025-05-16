from functools import wraps
from io import BytesIO
import os
import uuid
import json
import pandas as pd
import base64

from flask import (
    Blueprint,
    render_template,
    redirect,
    url_for,
    flash,
    session,
    current_app,
    request,
)
from werkzeug.security import check_password_hash
from werkzeug.utils import secure_filename
from matplotlib.pyplot import close
from requests import patch

from app.extensions import db
from app.models import User, Chart, File, Notification
from app.models.friend import Friend
from app.models import User, Chart
from app.models.friend import Friend
from app.models.notification import Notification
from app.forms import SignupForm, LoginForm, UploadForm, ChartForm, AddFriendForm
from app.models.shared_data import SharedData
from app.models.associations import SharedChart
from app.forms import (
    SignupForm,
    LoginForm,
    UploadForm,
    ChartForm,
    AddFriendForm,
    EditProfileForm,
)
from app.services import (
    Parser,
    registry,
    read_csv,
    save_to_string,
    save_figure_to_file,
)


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
    current_user_id = session['user_id']
    friends = (
        db.session.query(User)
        .join(Friend, Friend.friend_id == User.id)
        .filter(Friend.user_id == current_user_id)
        .all()
    )
    return render_template('friends.html', friends=friends)

@bp.route('/unfriend/<int:friend_id>', methods=['DELETE'])
@login_required
def unfriend(friend_id):
    current_user_id = session['user_id']
    relation = Friend.query.filter_by(user_id=current_user_id, friend_id=friend_id).first()
    reverse_relation = Friend.query.filter_by(user_id=friend_id, friend_id=current_user_id).first()

    if relation:
        db.session.delete(relation)
    if reverse_relation:
        db.session.delete(reverse_relation)
    user = User.query.get(current_user_id)
    notification = Notification(
        user_id=friend_id,
        message=f"{user.fullname} removed you from friends list."
    )
    db.session.add(notification)

    db.session.commit()
    flash("Friend removed successfully!", "success")
    return redirect(url_for('routes.friends'))

@bp.route('/add-friend', methods=['GET', 'POST'])
@login_required
def add_friend():
    form = AddFriendForm()
    current_user_id = session['user_id']

    if form.validate_on_submit():
        target_user = User.query.filter_by(id=form.user_id.data).first()

        if not target_user:
            flash("User ID not found.", "error")
        elif target_user.id == current_user_id:
            flash("You cannot add yourself as a friend.", "error")
        else:
            existing = Friend.query.filter_by(user_id=current_user_id, friend_id=target_user.id).first()
            if existing:
                flash("This user is already your friend.", "info")
            else:
                db.session.add(Friend(user_id=current_user_id, friend_id=target_user.id))
                db.session.add(Friend(user_id=target_user.id, friend_id=current_user_id))

                from app.models.notification import Notification
                notify = Notification(
                    user_id=target_user.id,
                    message=f"{User.query.get(current_user_id).fullname} added you as a friend!"
                )
                db.session.add(notify)

                db.session.commit()
                flash(f"Friend '{target_user.fullname}' added successfully!", "success")
                return redirect(url_for('routes.friends'))

    return render_template('add_friend.html', form=form)

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

    friends = User.query.get(user_id).friends
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


# ---------------------------------------------------------------------------------------------------------------------
# Generate Graph Route

@bp.route('/generate-graph', methods=['GET', 'POST'])
@login_required
def generate_graph():
    upload_form = UploadForm(prefix='up')
    chart_form  = ChartForm(prefix='ch', formdata=request.form)
    chart_src   = None
    show_config = False
    data        = None

    # 1) CSV upload
    if upload_form.submit_upload.data and upload_form.validate_on_submit():
        raw = upload_form.file.data.read()
        filename = secure_filename(upload_form.file.data.filename)
        folder = current_app.config['UPLOADS_FOLDER']
        os.makedirs(folder, exist_ok=True)
        unique = f"{uuid.uuid4().hex}_{filename}"
        path = os.path.join(folder, unique)
        with open(path, 'wb') as f:
            f.write(raw)
        session['file_id'] = File(name=filename, owner_id=session['user_id'])
        db.session.add(session['file_id'])
        db.session.commit()
        session['file_id'] = session['file_id'].id
        session['uploaded_filename'] = filename
        return redirect(url_for('routes.generate_graph'))

    # 2) Load DataFrame & populate choices
    if 'file_id' in session:
        file = File.query.get(session['file_id'])
        if file:
            folder = current_app.config['UPLOADS_FOLDER']
            suffix = f"_{file.name}"
            candidates = [fn for fn in os.listdir(folder) if fn.endswith(suffix)]
            if candidates:
                data = pd.read_csv(os.path.join(folder, candidates[0]))
                cols = list(data.columns)
                chart_form.x_col.choices = [('', '– Select X –')] + [(c, c) for c in cols]
                chart_form.y_col.choices = [('', '– Select Y –')] + [(c, c) for c in cols]
                chart_form.column.choices = [('', '– Select column –')] + [(c, c) for c in cols]
                show_config = True
            else:
                flash("Uploaded file missing; please re-upload.", "error")
                session.clear()

    # 3) Preview only—do NOT commit anything
    if data is not None and chart_form.submit_generate.data and chart_form.validate_on_submit():
        spec = {'source': data}
        # copy optional fields
        for fld in ['title','x_label','y_label','color','grid']:
            v = getattr(chart_form, fld).data
            if v:
                spec[fld] = v
        # figsize parsing
        if chart_form.figsize.data:
            try:
                w,h = map(int, chart_form.figsize.data.split('x'))
                spec['figsize'] = (w,h)
            except ValueError:
                flash("Invalid figure size; use e.g. 10x6", "warning")

        t = chart_form.graph_type.data
        spec['graph_type'] = t

        # require correct inputs
        if t in ['line','bar','scatter','area','box']:
            x,y = chart_form.x_col.data, chart_form.y_col.data
            if not x or not y:
                flash("Both X and Y are required.", "error")
                return redirect(url_for('routes.generate_graph'))
            spec['x_col'], spec['y_col'] = x,y
        else:
            col = chart_form.column.data
            if not col:
                flash("A column must be selected.", "error")
                return redirect(url_for('routes.generate_graph'))
            spec['column'] = col

        # bind & validate types
        bind_spec = spec.copy(); bind_spec.pop('graph_type',None)
        try:
            bound,_ = registry.functions[t].bind_args(**bind_spec)
            if t=='scatter' and not pd.api.types.is_numeric_dtype(data[bound['x_col']]):
                flash("X must be numeric for scatter.", "error")
                return redirect(url_for('routes.generate_graph'))
            if t in ['line','scatter','bar','area','box'] and not pd.api.types.is_numeric_dtype(data[bound['y_col']]):
                flash("Y must be numeric for this chart.", "error")
                return redirect(url_for('routes.generate_graph'))
            fig = registry.functions[t].function(**bound)
        except KeyError as e:
            flash(f"Column '{e.args[0]}' not found.", "error")
            return redirect(url_for('routes.generate_graph'))
        except Exception as e:
            current_app.logger.error(f"Chart gen error: {e}")
            flash("Error generating chart. Check inputs.", "error")
            return redirect(url_for('routes.generate_graph'))

        # render preview as base64
        buf = BytesIO(); fig.savefig(buf, format='png'); buf.seek(0)
        chart_src = 'data:image/png;base64,' + base64.b64encode(buf.read()).decode()
        close(fig)

        # stash minimal info for save_chart
        session['pending_spec'] = {k:v for k,v in spec.items() if k!='source'}
        session['pending_file_id'] = session['file_id']
        session['pending_title'] = spec.get('title') or 'Untitled'

        show_config = True

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
    pending = {
        'spec':   session.pop('pending_spec', None),
        'file_id':session.pop('pending_file_id', None),
        'title':  session.pop('pending_title', None)
    }
    if not pending['spec'] or not pending['file_id']:
        flash("Nothing to save.", "error")
        return redirect(url_for('routes.generate_graph'))

    # 1) Save the Chart record (including graph_type in spec)
    spec_for_db = pending['spec'].copy()
    chart = Chart(
        name     = pending['title'],
        owner_id = session['user_id'],
        file_id  = pending['file_id'],
        spec     = json.dumps(spec_for_db)
    )
    db.session.add(chart)
    db.session.commit()

    # 2) Reload the CSV
    folder = current_app.config['UPLOADS_FOLDER']
    file = File.query.get(pending['file_id'])
    suffix = f"_{file.name}"
    fn = next(fn for fn in os.listdir(folder) if fn.endswith(suffix))
    data = pd.read_csv(os.path.join(folder, fn))

    # 3) Prepare args for the plot function
    spec_for_plot = spec_for_db.copy()
    graph_type    = spec_for_plot.pop('graph_type')   # <-- remove this!
    spec_for_plot['source'] = data

    # 4) Regenerate and save the figure
    fig = registry.functions[graph_type].function(**spec_for_plot)
    path = save_figure_to_file(fig, chart.id)
    chart.image_path = path
    db.session.commit()
    close(fig)

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

    # capture file before deleting chart
    file = chart.file
    file_name = file.name
    uploads_folder = current_app.config['UPLOADS_FOLDER']
    pattern = f"_{file_name}"

    # delete the chart’s image from disk
    if chart.image_path:
        image_path = os.path.join(
            current_app.root_path,
            'static', 'chart_images',
            os.path.basename(chart.image_path)
        )
        if os.path.exists(image_path):
            os.remove(image_path)

    # remove the Chart record
    db.session.delete(chart)
    db.session.commit()

    # now delete the File record + any on‐disk CSV if it’s no longer used
    if not file.charts:
        for fname in os.listdir(uploads_folder):
            if fname.endswith(pattern):
                try:
                    os.remove(os.path.join(uploads_folder, fname))
                except Exception as e:
                    current_app.logger.warning(f"Failed to delete file {fname}: {e}")
        db.session.delete(file)
        db.session.commit()

    flash("Chart and associated file (if unused) deleted successfully.", "success")
    return redirect(url_for('routes.dashboard'))


@bp.context_processor
def inject_notifications():
    if 'user_id' in session:
        notifs = Notification.query.filter_by(
            user_id=session['user_id']
        ).order_by(Notification.created_at.desc()).limit(10).all()
        unread_count = Notification.query.filter_by(
            user_id=session['user_id'],
            is_read=False
        ).count()
        return dict(notifications=notifs, unread_count=unread_count)
    return dict(notifications=[], unread_count=0)


@bp.route('/notifications/read', methods=['POST'])
@login_required
def mark_notifications_read():
    Notification.query.filter_by(
        user_id=session['user_id'],
        is_read=False
    ).update({'is_read': True})
    db.session.commit()
    return '', 204

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