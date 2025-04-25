from instance.database import db
from models.product_image import ProductImages

def create_product_images(product_id, image1=None, image2=None, image3=None):
    image_entry = ProductImages(
        product_id=product_id,
        image1_url=image1,
        image2_url=image2,
        image3_url=image3
    )
    db.session.add(image_entry)
    db.session.commit()
    return image_entry

def get_product_images(product_id):
    return ProductImages.query.filter_by(product_id=product_id).first()

def update_product_images(product_id, data):
    images = ProductImages.query.filter_by(product_id=product_id).first()
    if not images:
        return None
    for field in ['image1_url', 'image2_url', 'image3_url']:
        if field in data:
            setattr(images, field, data[field])
    db.session.commit()
    return images

def delete_product_images(product_id):
    images = ProductImages.query.filter_by(product_id=product_id).first()
    if not images:
        return False
    db.session.delete(images)
    db.session.commit()
    return True
