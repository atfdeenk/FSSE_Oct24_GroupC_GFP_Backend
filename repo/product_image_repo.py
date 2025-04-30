from instance.database import db
from models.product_image import ProductImages


def create_product_images(product_id, image1=None, image2=None, image3=None):
    image_entry = ProductImages(
        product_id=product_id, image1_url=image1, image2_url=image2, image3_url=image3
    )
    db.session.add(image_entry)
    return image_entry


def save_uploaded_filename(product_id, filename):
    images = ProductImages.query.filter_by(product_id=product_id).first()
    if not images:
        # Create a new entry if not exists
        images = ProductImages(product_id=product_id)
        db.session.add(images)

    # Logic to fill first empty slot
    if not images.image1_url:
        images.image1_url = filename
    elif not images.image2_url:
        images.image2_url = filename
    elif not images.image3_url:
        images.image3_url = filename
    else:
        # All 3 slots are full, you can raise error or overwrite first one if you want
        images.image1_url = filename

    return images


def get_product_images(product_id):
    return ProductImages.query.filter_by(product_id=product_id).first()


def update_product_images(product_id, data):
    images = ProductImages.query.filter_by(product_id=product_id).first()
    if not images:
        return None
    for field in ["image1_url", "image2_url", "image3_url"]:
        if field in data:
            setattr(images, field, data[field])
    return images


def delete_product_images(product_id):
    images = ProductImages.query.filter_by(product_id=product_id).first()
    if not images:
        return False
    db.session.delete(images)
    return True
