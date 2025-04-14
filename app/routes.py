import os
from flask import Blueprint, render_template, redirect, url_for, current_app, request, flash, session
from werkzeug.utils import secure_filename
from .models import db, Pet
from .forms import PetForm
from sqlalchemy import desc

main = Blueprint('main', __name__)

@main.route('/')
def home():
    pet_type = request.args.get('type', 'All')
    search = request.args.get('search', '').strip().lower()
    sort_by = request.args.get('sort', 'newest')
    page = request.args.get('page', 1, type=int)

    query = Pet.query

    if pet_type and pet_type != 'All':
        query = query.filter(Pet.pet_type == pet_type)

    if search:
        query = query.filter(
            (Pet.name.ilike(f"%{search}%")) |
            (Pet.breed.ilike(f"%{search}%"))
        )

    if sort_by == 'age_asc':
        query = query.order_by(Pet.age.asc())
    elif sort_by == 'age_desc':
        query = query.order_by(Pet.age.desc())
    elif sort_by == 'price_asc':
        query = query.order_by(Pet.price.asc())
    elif sort_by == 'price_desc':
        query = query.order_by(Pet.price.desc())
    else:
        query = query.order_by(desc(Pet.id))

    pets = query.paginate(page=page, per_page=6)
    favorites = session.get('favorites', [])

    return render_template('index.html',
                           pets=pets,
                           selected_type=pet_type,
                           search_query=search,
                           sort_by=sort_by,
                           favorites=favorites)

@main.route('/add', methods=['GET', 'POST'])
def add_pet():
    form = PetForm()
    if form.validate_on_submit():
        image_filename = None
        if form.image.data:
            filename = secure_filename(form.image.data.filename)
            image_path = os.path.join('static/uploads', filename)
            form.image.data.save(os.path.join(current_app.root_path, image_path))
            image_filename = filename

        # ✅ Calculate age in months from years + months
        age_months_total = (form.age_years.data or 0) * 12 + (form.age_months.data or 0)

        pet = Pet(
            name=form.name.data,
            pet_type=form.pet_type.data,
            breed=form.breed.data,
            age=age_months_total,
            price=form.price.data,
            image=image_filename
        )
        db.session.add(pet)
        db.session.commit()
        flash("Pet added successfully!", "success")
        return redirect(url_for('main.home'))
    return render_template('add_pet.html', form=form)

@main.route('/edit/<int:pet_id>', methods=['GET', 'POST'])
def edit_pet(pet_id):
    pet = Pet.query.get_or_404(pet_id)
    form = PetForm(obj=pet)
    if request.method == 'POST' and form.validate_on_submit():
        pet.name = form.name.data
        pet.pet_type = form.pet_type.data
        pet.breed = form.breed.data
        pet.price = form.price.data

        # ✅ Recalculate age from separate fields
        pet.age = (form.age_years.data or 0) * 12 + (form.age_months.data or 0)

        if form.image.data:
            filename = secure_filename(form.image.data.filename)
            image_path = os.path.join('static/uploads', filename)
            form.image.data.save(os.path.join(current_app.root_path, image_path))
            pet.image = filename

        db.session.commit()
        flash("Pet updated successfully!", "success")
        return redirect(url_for('main.home'))
    return render_template('edit_pet.html', form=form, pet=pet)

@main.route('/delete/<int:pet_id>', methods=['POST'])
def delete_pet(pet_id):
    pet = Pet.query.get_or_404(pet_id)
    db.session.delete(pet)
    db.session.commit()
    flash("Pet deleted successfully!", "danger")
    return redirect(url_for('main.home'))

# ✅ Favorite / Unfavorite Toggle
@main.route('/favorite/<int:pet_id>', methods=['POST'])
def toggle_favorite(pet_id):
    favorites = session.get('favorites', [])
    if pet_id in favorites:
        favorites.remove(pet_id)
        flash("Removed from favorites.", "info")
    else:
        favorites.append(pet_id)
        flash("Added to favorites!", "success")
    session['favorites'] = favorites
    return redirect(request.referrer or url_for('main.home'))

# ✅ View All Favorites
@main.route('/favorites')
def favorites():
    favorite_ids = session.get('favorites', [])
    pets = Pet.query.filter(Pet.id.in_(favorite_ids)).all()
    return render_template('favorites.html', pets=pets)
