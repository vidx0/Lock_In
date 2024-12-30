import os
import datetime
from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify, Response
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from .models import *
from . import db
from flask import Response
import json




views = Blueprint('views', __name__)




@views.route('/', methods=['GET', 'POST'])
@login_required
def home():
    if request.method == 'POST': 
        note = request.form.get('note')#Gets the note from the HTML 

        if len(note) < 1:
            flash('Note is too short!', category='error') 
        else:
            new_note = Note(data=note, user_id=current_user.id)  #providing the schema for the note 
            db.session.add(new_note) #adding the note to the database 
            db.session.commit()
            flash('Note added!', category='success')

    return render_template("home.html", user=current_user)


@views.route('/delete-note', methods=['POST'])
def delete_note():  
    note = json.loads(request.data) # this function expects a JSON from the INDEX.js file 
    noteId = note['noteId']
    note = Note.query.get(noteId)
    if note:
        if note.user_id == current_user.id:
            db.session.delete(note)
            db.session.commit()

    return jsonify({})
# all code above works

@views.route('/forum', methods=['GET','POST'])
@login_required
def forum():
    default_categories = ["Science", "Math", "History", "Programming", "Languages"]

# Check if the categories already exist to avoid duplicates
    for name in default_categories:
        if not Category.query.filter_by(name=name).first():
            category = Category(name=name)
            db.session.add(category)
    db.session.commit()
    categories = Category.query.all()
    category_id = request.args.get('category')
    sort_by = request.args.get('sort', 'newest')

    if category_id:
        questions = Question.query.filter_by(category_id=category_id)
    else:
        questions = Question.query

    if sort_by == 'votes':
        questions = questions.order_by(Question.upvotes.desc())
    else:
        questions = questions.order_by(Question.id.desc())

    questions = questions.all()

    return render_template('forum.html', questions=questions, categories=categories, user=current_user)

@views.route('/ask-question', methods=['GET', 'POST'])
@login_required
def ask_question():
    if request.method == 'POST':
        title = request.form.get('title')
        print(title)
        description = request.form.get('description')
        print(description)
        category_id = request.form.get('category')
        
        points = int(request.form.get('wagered_points'))

        if points < 0:
            flash('Points must be a positive number.', 'error')
            return redirect(url_for('views.ask_question'))

        # Create a new question
        question = Question(
            title=title,
            description=description,
            category_id=category_id,
            wagered_points=points,
            user_id=current_user.id
        )
        db.session.add(question)
        db.session.commit()

        flash('Your question has been posted!', 'success')
        return redirect(url_for('views.forum'))

    # Fetch all categories for the dropdown
    categories = Category.query.all()
    return render_template('ask_question.html', categories=categories, user=current_user)


@views.route('/answer/<int:question_id>', methods=['GET', 'POST'])
@login_required
def answer_question_view(question_id):
    question = Question.query.get_or_404(question_id)

    if request.method == 'POST':
        # Get the answer from the form
        answer = request.form.get('answer')

        # Ensure the answer is not empty
        if not answer.strip():
            flash("Answer cannot be empty.", "error")
            return redirect(url_for('answer_question_view', question_id=question_id))

        # Check if the question has already been answered
        if question.is_answered:
            flash("This question has already been answered.", "error")
            return redirect(url_for('views.forum'))

        # Save the answer and update the question status
        question.answer = answer
        question.answered_by = current_user.id  # Assuming `current_user` represents the logged-in user
        question.is_answered = True

        # Award points to the current user
        current_user.points += question.wagered_points

        # Commit changes to the database
        db.session.commit()

        flash("Your answer has been submitted, and points have been awarded!", "success")
        return redirect(url_for('views.forum'))

    return render_template('answer.html', question=question, user=current_user)

@views.route('/vote/<int:question_id>/<string:vote_type>', methods=['POST'])
@login_required
def vote(question_id, vote_type):
    question = Question.query.get_or_404(question_id)
    if vote_type == "upvote":
        question.upvotes += 1
    elif vote_type == "downvote":
        question.downvotes += 1
    db.session.commit()
    return redirect(url_for('views.forum'))



@views.route("/timer", methods = ["GET","POST"])
@login_required
def timer():
    if request.method == 'POST':
        time_spent = int(request.json.get('time_spent', 0))
        current_user.time_spent += time_spent
        current_user.points += time_spent * 5
        db.session.commit()
        
    return render_template("timer.html", user=current_user)
# Define the allowed file extensions
ALLOWED_EXTENSIONS = {'mp4', 'avi', 'mov', 'mkv'}

def allowed_file(filename):
    # Check if the file has a valid extension
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@views.route('/upload', methods=['GET', 'POST'])
@login_required
def upload():
    if request.method == 'POST':
        video_file = request.files['video']
        description = request.form.get('description', '')

        if video_file and allowed_file(video_file.filename):
            # Read video content as binary
            video_content = video_file.read()
            filename = secure_filename(video_file.filename)

            # Store video metadata and content in the database
            new_video = Video(
                filename=filename,
                description=description,
                content=video_content
            )
            db.session.add(new_video)
            db.session.commit()

            flash("Video uploaded successfully!", "success")
            return redirect(url_for('views.video_list'))  # Redirect to the video list page

        flash("Invalid file type. Only video files are allowed.", "error")

    return render_template('upload.html', user=current_user)

@views.route('/videos', methods=['GET'])
@login_required
def video_list():
    videos = Video.query.all()
    return render_template('video_list.html', user=current_user, videos=videos)




@views.route('/video/<int:video_id>', methods=['GET'])
@login_required
def watch_video(video_id):
    video = Video.query.get_or_404(video_id)
    return Response(video.content, mimetype="video/mp4")


@views.route('/api/videos', methods=['GET'])
@login_required
def get_videos():
    page = request.args.get('page', 1, type=int)
    per_page = 5  # Number of videos per page
    videos = Video.query.paginate(page, per_page, False)
    data = [
        {
            "id": video.id,
            "filename": video.filename,
            "description": video.description,
        }
        for video in videos.items
    ]
    return jsonify({
        "videos": data,
        "has_next": videos.has_next,
        "has_prev": videos.has_prev
    })

