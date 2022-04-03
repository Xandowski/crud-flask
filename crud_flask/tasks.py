import json

from flask import Blueprint, render_template, request, session

from .auth import requires_auth
from .model import Task, User, db

bp_tasks = Blueprint("tasks", __name__)


@bp_tasks.route("/user/<nickname>", methods=["GET"])
@requires_auth
def user(nickname):
    user = User.query.filter_by(nickname=f"{nickname}").first()
    tasks = Task.query.filter_by(user_id=f"{user.id}").all()
    return render_template(
        "user.html",
        userinfo=session["user"],
        userinfo_pretty=json.dumps(session["jwt_payload"], indent=4),
        tasks=tasks,
        user=user
    )


@bp_tasks.route("/task/create/<int:id>", methods=["POST"])
def create(id):
    task = Task(user_id=id, name=request.form["create-task"], create_date=request.form["create-date"])
    print(task.user_id)
    db.session.add(task)
    db.session.commit()
    response = f"""
    <tr>
        <td>{task.name}</td>
        <td>{task.create_date}</td>
        <td>
            <span
                hx-get='/task/{task.id}/edit'
                hx-trigger="edit"
                id='clickableAwesomeFont'
                _="on click
                    if .editing is not empty
                    Swal.fire({{title: 'Already Editing', 
                                showCancelButton: true,
                                confirmButtonText: 'Yep, Edit This Row!',
                                text:'Hey!  You are already editing a row!  Do you want to cancel that edit and continue?'}})
                    if the result's isConfirmed is false
                        halt
                    end
                    send cancel to .editing
                    end
                    trigger edit"
                >
                    <i class='fas fa-edit fa-lg' name='edit' hx-get='/task/{task.id}/edit' hx-target='closest tr' hx-swap='outerHTML swap:1s'></i>
            </span hx-delete='/task/delete/{task.id}'>
            <span><i class='fas fa-trash fa-lg' name='a' hx-delete='/task/delete/{task.id}' hx-target='closest tr' hx-swap='outerHTML swap:1s'></i></span>
        </td>
    <tr/>
    """
    return response


@bp_tasks.route("/task/delete/<int:id>", methods=["DELETE"])
def delete(id):
    task = Task.query.get(id)
    db.session.delete(task)
    db.session.commit()
    print(f"{task.name} removed")
    return ""


@bp_tasks.route("/task/<int:id>/edit", methods=["GET"])
def enable_edit(id):
    task = Task.query.get(id)
    print(task.id)
    response = f"""
    <tr hx-trigger='cancel' class='editing' hx-get="/task/{task.id}">
        <td><input type="text" name='create-task' value='{task.name}'></td>
        <td><input type="date" name='create-date' value='{task.create_date}'></td>
        <td>
            <span hx-put="/task/{task.id}" hx-include="closest tr">
                <i class='fas fa-square-check fa-lg'></i>
            </span>
            <span hx-get="/task/{task.id}">
                <i class='fas fa-rectangle-xmark fa-lg'></i>
            </span>
        </td>
        
    </tr>
    """
    return response


@bp_tasks.route("/task/<int:id>", methods=["GET", "PUT"])
def edit(id):
    task = Task.query.get(id)

    if request.method == "PUT":
        task.name = request.form["create-task"]
        task.create_date = request.form["create-date"]
        db.session.commit()

    response = f"""
    <tr>
        <td>{task.name}</td>
        <td>{task.create_date}</td>
        <td>
            <span"
                hx-get='/task/edit/{{task.id}}'
                hx-trigger="edit" hx-swap='outerHTML swap:1s'
                _="on click
                    if .editing is not empty
                    Swal.fire({{title: 'Already Editing', 
                                showCancelButton: true,
                                confirmButtonText: 'Yep, Edit This Row!',
                                text:'Hey!  You are already editing a row!  Do you want to cancel that edit and continue?'}})
                    if the result's isConfirmed is false
                        halt
                    end
                    send cancel to .editing
                    end
                    trigger edit"
            >
                <i class='fas fa-edit fa-lg' 
                name='edit' hx-get='/task/{task.id}/edit' hx-target='closest tr' hx-swap='outerHTML swap:1s'>
                </i>
            </span hx-delete='/task/delete/{task.id}'>
            <span><i class='fas fa-trash fa-lg' name='delete' hx-delete='/task/delete/{task.id}' hx-target='closest tr' hx-swap='outerHTML swap:1s'></i></span>        
        </td>
    </tr>
    """
    print(f"{task.name} edited")

    return response
