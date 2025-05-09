from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models.voucher import Vouchers
from instance.database import db
from datetime import datetime
from shared.auth import role_required
from models.order import Orders

voucher_bp = Blueprint("voucher_bp", __name__)

@voucher_bp.route("/vouchers/me", methods=["GET"])
@jwt_required()
@role_required("vendor")
def get_my_vouchers():
    vendor_id = int(get_jwt_identity())
    vouchers = Vouchers.query.filter_by(vendor_id=vendor_id).all()
    return jsonify([
        {
            "id": v.id,
            "code": v.code,
            "discount_percent": float(v.discount_percent) if v.discount_percent else None,
            "discount_amount": float(v.discount_amount) if v.discount_amount else None,
            "is_active": v.is_active,
            "expires_at": v.expires_at.isoformat() if v.expires_at else None,
            "vendor_id": v.vendor_id,
            "vendor_name": v.vendor.username if v.vendor else None
        }
        for v in vouchers
    ])

@voucher_bp.route("/vouchers/<int:voucher_id>", methods=["GET"])
@jwt_required()
@role_required("vendor")
def get_voucher(voucher_id):
    vendor_id = int(get_jwt_identity())
    voucher = db.session.get(Vouchers, voucher_id)
    if not voucher or voucher.vendor_id != vendor_id:
        return jsonify({"msg": "Voucher not found or unauthorized"}), 404
    return jsonify({
        "id": voucher.id,
        "code": voucher.code,
        "discount_percent": float(voucher.discount_percent) if voucher.discount_percent else None,
        "discount_amount": float(voucher.discount_amount) if voucher.discount_amount else None,
        "is_active": voucher.is_active,
        "expires_at": voucher.expires_at.isoformat() if voucher.expires_at else None,
        "vendor_id": voucher.vendor_id,
        "vendor_name": voucher.vendor.username if voucher.vendor else None
    })

@voucher_bp.route("/vouchers", methods=["POST"])
@jwt_required()
@role_required("vendor")
def create_voucher():
    vendor_id = int(get_jwt_identity())
    data = request.get_json()
    voucher = Vouchers(
        code=data["code"],
        discount_percent=data.get("discount_percent"),
        discount_amount=data.get("discount_amount"),
        is_active=data.get("is_active", True),
        vendor_id=vendor_id,
        expires_at=datetime.fromisoformat(data["expires_at"]) if data.get("expires_at") else None
    )
    db.session.add(voucher)
    db.session.commit()
    return jsonify({"msg": "Voucher created", "id": voucher.id}), 201

@voucher_bp.route("/vouchers/<int:voucher_id>", methods=["PUT"])
@jwt_required()
@role_required("vendor")
def update_voucher(voucher_id):
    vendor_id = int(get_jwt_identity())
    voucher = db.session.get(Vouchers, voucher_id)
    if not voucher or voucher.vendor_id != vendor_id:
        return jsonify({"msg": "Voucher not found or unauthorized"}), 404

    data = request.get_json()
    voucher.code = data.get("code", voucher.code)
    voucher.discount_percent = data.get("discount_percent", voucher.discount_percent)
    voucher.discount_amount = data.get("discount_amount", voucher.discount_amount)
    voucher.is_active = data.get("is_active", voucher.is_active)
    if "expires_at" in data:
        voucher.expires_at = datetime.fromisoformat(data["expires_at"]) if data["expires_at"] else None

    db.session.commit()
    return jsonify({"msg": "Voucher updated"}), 200

@voucher_bp.route("/vouchers/<int:voucher_id>", methods=["DELETE"])
@jwt_required()
@role_required("vendor")
def delete_voucher(voucher_id):
    vendor_id = int(get_jwt_identity())
    voucher = db.session.get(Vouchers, voucher_id)
    if not voucher or voucher.vendor_id != vendor_id:
        return jsonify({"msg": "Voucher not found or unauthorized"}), 404

    order_exists = Orders.query.filter_by(voucher_id=voucher_id).first()
    if order_exists:
        return jsonify({"msg": "Cannot delete voucher — it is still used in existing orders"}), 400

    db.session.delete(voucher)
    db.session.commit()
    return jsonify({"msg": "Voucher deleted"}), 200

@voucher_bp.route("/vouchers/<int:voucher_id>/deactivate", methods=["PATCH"])
@jwt_required()
@role_required("vendor")
def deactivate_voucher(voucher_id):
    vendor_id = int(get_jwt_identity())
    voucher = db.session.get(Vouchers, voucher_id)
    if not voucher or voucher.vendor_id != vendor_id:
        return jsonify({"msg": "Voucher not found or unauthorized"}), 404

    voucher.is_active = False
    db.session.commit()
    return jsonify({"msg": f"Voucher '{voucher.code}' deactivated"}), 200

@voucher_bp.route("/vouchers/code/<string:code>", methods=["GET"])
@jwt_required()
@role_required("customer")
def get_voucher_by_code(code):
    voucher = Vouchers.query.filter_by(code=code, is_active=True).first()
    if not voucher or (voucher.expires_at and voucher.expires_at < datetime.utcnow()):
        return jsonify({"msg": "Voucher not found or expired"}), 404

    return jsonify({
        "code": voucher.code,
        "discount_percent": voucher.discount_percent,
        "discount_amount": str(voucher.discount_amount),
        "expires_at": voucher.expires_at.isoformat() if voucher.expires_at else None,
        "vendor_id": voucher.vendor_id,
        "vendor_name": voucher.vendor.username if voucher.vendor else None
    })
