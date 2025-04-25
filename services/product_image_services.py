from repo import product_image_repo as product_image_repo

def add_images(product_id, data):
    return product_image_repo.create_product_images(
        product_id,
        image1=data.get("image1_url"),
        image2=data.get("image2_url"),
        image3=data.get("image3_url")
    )

def get_images(product_id):
    return product_image_repo.get_product_images(product_id)

def update_images(product_id, data):
    return product_image_repo.update_product_images(product_id, data)

def delete_images(product_id):
    return product_image_repo.delete_product_images(product_id)
