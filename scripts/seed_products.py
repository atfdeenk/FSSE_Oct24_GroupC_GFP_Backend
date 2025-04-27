import os
from dotenv import load_dotenv
from instance.database import db
from models.product import Product
from app import create_app

dotenv_path = os.path.join(os.path.dirname(__file__), '..', '.env')
load_dotenv(dotenv_path)

app = create_app()

with app.app_context():
    products = [
        Product(
            name="Sumatra Mandheling",
            slug="sumatra-mandheling",
            description="Rich, syrupy body with low acidity.",
            currency="IDR",
            price=90000.0,
            stock_quantity=30,
            unit_quantity="250g",
            image_url="fallback.png",
            vendor_id=15,
            featured=False,
            flash_sale=False
        ),
        Product(
            name="Sulawesi Kalosi",
            slug="sulawesi-kalosi",
            description="Bold, earthy, and smoky aroma.",
            currency="IDR",
            price=89000.0,
            stock_quantity=25,
            unit_quantity="250g",
            image_url="fallback.png",
            vendor_id=19,
            featured=True,
            flash_sale=False
        ),
        Product(
            name="Papua Wamena",
            slug="papua-wamena",
            description="Mild body with bright acidity.",
            currency="IDR",
            price=98000.0,
            stock_quantity=20,
            unit_quantity="250g",
            image_url="fallback.png",
            vendor_id=18,
            featured=False,
            flash_sale=False
        ),
        Product(
            name="Lampung Robusta",
            slug="lampung-robusta",
            description="Strong and bold robusta beans.",
            currency="IDR",
            price=75000.0,
            stock_quantity=70,
            unit_quantity="250g",
            image_url="fallback.png",
            vendor_id=15,
            featured=False,
            flash_sale=True
        ),
        Product(
            name="Bengkulu Robusta",
            slug="bengkulu-robusta",
            description="Earthy robusta flavor with deep aroma.",
            currency="IDR",
            price=73000.0,
            stock_quantity=65,
            unit_quantity="250g",
            image_url="fallback.png",
            vendor_id=16,
            featured=False,
            flash_sale=False
        ),
        Product(
            name="Toraja Sapan",
            slug="toraja-sapan",
            description="Spicy, earthy, and full-bodied.",
            currency="IDR",
            price=94000.0,
            stock_quantity=35,
            unit_quantity="250g",
            image_url="fallback.png",
            vendor_id=16,
            featured=True,
            flash_sale=False
        ),
        Product(
            name="Java Arabica",
            slug="java-arabica",
            description="Smooth body with chocolate hints.",
            currency="IDR",
            price=88000.0,
            stock_quantity=45,
            unit_quantity="250g",
            image_url="fallback.png",
            vendor_id=19,
            featured=False,
            flash_sale=True
        ),
        Product(
            name="Bali Pupuan",
            slug="bali-pupuan",
            description="Floral with soft citrus notes.",
            currency="IDR",
            price=94000.0,
            stock_quantity=55,
            unit_quantity="250g",
            image_url="fallback.png",
            vendor_id=18,
            featured=False,
            flash_sale=False
        ),
        Product(
            name="Sidikalang Arabica",
            slug="sidikalang-arabica",
            description="Strong, heavy-bodied, unique aroma.",
            currency="IDR",
            price=91000.0,
            stock_quantity=40,
            unit_quantity="250g",
            image_url="fallback.png",
            vendor_id=15,
            featured=True,
            flash_sale=False
        ),
        Product(
            name="Malabar Preanger",
            slug="malabar-preanger",
            description="Delicate sweet and floral aroma.",
            currency="IDR",
            price=93000.0,
            stock_quantity=50,
            unit_quantity="250g",
            image_url="fallback.png",
            vendor_id=16,
            featured=False,
            flash_sale=True
        ),
    ]

    for product in products:
        existing_product = Product.query.filter_by(slug=product.slug).first()
        if existing_product:
            print(f"⚠️ Product '{product.slug}' already exists. Skipping.")
        else:
            db.session.add(product)
            print(f"✅ Product '{product.slug}' added.")

    db.session.commit()
    print("✅ Seeding completed without deleting anything!")
