import os
from repo import product_image_repo as product_image_repo
from werkzeug.utils import secure_filename
from instance.database import db

UPLOAD_FOLDER = "uploads"


def save_uploaded_image(product_id, file):
    try:
        filename = secure_filename(file.filename)

        os.makedirs(UPLOAD_FOLDER, exist_ok=True)
        file_path = os.path.join(UPLOAD_FOLDER, filename)
        file.save(file_path)

        # Save filename into the database
        images = product_image_repo.save_uploaded_filename(product_id, filename)
        db.session.commit()

        return {"filename": filename, "url": f"/uploads/{filename}"}
    except Exception as e:
        db.session.rollback()
        print(f"Error saving uploaded image: {str(e)}")
        return None


def add_images(product_id, data):
    try:
        result = product_image_repo.create_product_images(
            product_id,
            image1=data.get("image1_url"),
            image2=data.get("image2_url"),
            image3=data.get("image3_url"),
        )
        db.session.commit()
        return result
    except Exception:
        db.session.rollback()
        raise


def get_images(product_id):
    return product_image_repo.get_product_images(product_id)


def update_images(product_id, data):
    try:
        result = product_image_repo.update_product_images(product_id, data)
        db.session.commit()
        return result
    except Exception:
        db.session.rollback()
        raise


def delete_images(product_id):
    try:
        result = product_image_repo.delete_product_images(product_id)
        db.session.commit()
        return result
    except Exception:
        db.session.rollback()
        raise
