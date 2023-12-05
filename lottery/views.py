# IMPORTS

from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import current_user

from app import db, required_roles
from lottery.forms import DrawForm
from models import Draw
from sqlalchemy.orm import make_transient

# CONFIG
lottery_blueprint = Blueprint('lottery', __name__, template_folder='templates')


@required_roles('user')
def decrypt_draws(draws):
    for draw in draws:
        make_transient(draw)
        # # For symmetric encryption
        # draw.view_draw(current_user.secret_key)
        # For asymmetric encryption
        draw.view_draw(current_user.private_key)


# VIEWS
# view lottery page
@lottery_blueprint.route('/lottery')
@required_roles('user')
def lottery():
    return render_template('lottery/lottery.html',
                           name=current_user.firstname)


# view all draws that have not been played
@lottery_blueprint.route('/create_draw', methods=['POST'])
@required_roles('user')
def create_draw():
    form = DrawForm()

    if form.validate_on_submit():
        submitted_numbers = (str(form.number1.data) + ' '
                             + str(form.number2.data) + ' '
                             + str(form.number3.data) + ' '
                             + str(form.number4.data) + ' '
                             + str(form.number5.data) + ' '
                             + str(form.number6.data))
        # # create a new draw with the form data. # Symmetric encryption
        # new_draw = Draw(user_id=current_user.id,
        #                 numbers=submitted_numbers,
        #                 master_draw=False,
        #                 lottery_round=0,
        #                 secret_key=current_user.secret_key)
        # create a new draw with the form data. # asymmetric encryption
        new_draw = Draw(user_id=current_user.id,
                        numbers=submitted_numbers,
                        master_draw=False,
                        lottery_round=0,
                        secret_key=current_user.public_key)
        # add the new draw to the database
        db.session.add(new_draw)
        db.session.commit()

        # re-render lottery.page
        flash('Draw %s submitted.' % submitted_numbers)
        return redirect(url_for('lottery.lottery'))

    return render_template('lottery/lottery.html',
                           name=current_user.firstname,
                           form=form)


# view all draws that have not been played
@lottery_blueprint.route('/view_draws', methods=['POST'])
@required_roles('user')
def view_draws():
    # get all draws that have not been played [played=0]
    # And only get the draws made by the current user
    playable_draws = Draw.query.filter_by(been_played=False, user_id=current_user.id).all()

    # if playable draws exist
    if len(playable_draws) != 0:
        # Decrypt our draws
        decrypt_draws(playable_draws)

        # re-render lottery page with playable draws
        return render_template('lottery/lottery.html',
                               playable_draws=playable_draws,
                               name=current_user.firstname)
    else:
        flash('No playable draws.')
        return lottery()


# view lottery results
@lottery_blueprint.route('/check_draws', methods=['POST'])
@required_roles('user')
def check_draws():
    # get played draws
    # And only get the draws made by the current user
    played_draws = Draw.query.filter_by(been_played=True, user_id=current_user.id).all()

    # if played draws exist
    if len(played_draws) != 0:

        return render_template('lottery/lottery.html',
                               results=played_draws,
                               played=True,
                               name=current_user.firstname)

    # if no played draws exist [all draw entries have been played therefore wait for next lottery round]
    else:
        flash("Next round of lottery yet to play. Check you have playable draws.")
        return lottery()


# delete all played draws
@lottery_blueprint.route('/play_again', methods=['POST'])
@required_roles('user')
def play_again():
    # Again, only delete draws made by current user
    Draw.query.filter_by(been_played=True, master_draw=False, user_id=current_user.id).delete(synchronize_session=False)
    db.session.commit()

    flash("All played draws deleted.")
    return lottery()
