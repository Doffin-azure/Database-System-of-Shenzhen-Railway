from flask import request, jsonify
from . import bp
from app.models import Card, Passenger, db
from datetime import datetime, date

@bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    register_type = data.get("register_type")

    if register_type == "card":
        max_code = db.session.query(db.func.max(Card.code)).scalar()
        code = str(int(max_code or 0) + 1).zfill(9)

        new_card = Card(
            code=code,
            money=data.get("money"),
            create_time=datetime.now().strftime("%H:%M:%S"),
            create_date=date.today().strftime("%Y-%m-%d")
        )

        try:
            db.session.add(new_card)
            db.session.commit()
            return jsonify({"message": f"Card registered successfully, code: {code}, money: {data.get('money')}"}), 201
        except Exception as e:
            db.session.rollback()
            return jsonify({"error": str(e)}), 500

    elif register_type == "passenger":
        new_passenger = Passenger(
            id_number=data.get("id_number"),
            name=data.get("name"),
            phone_number=data.get("phone_number"),
            gender=data.get("gender"),
            district=data.get("district")
        )

        try:
            db.session.add(new_passenger)
            db.session.commit()
            return jsonify({"message": "Passenger registered successfully"}), 201
        except Exception as e:
            db.session.rollback()
            return jsonify({"error": str(e)}), 500

    else:
        return jsonify({"error": "Invalid register type"}), 400

@bp.route("/recharge", methods=["POST"])
def card_recharge():
    data = request.get_json()
    code = data.get("code")
    money = data.get("money")

    card = Card.query.get(code)
    if not card:
        return jsonify({"error": "Card not found"}), 404

    card.money += money

    try:
        db.session.commit()
        return jsonify({"message": "Card recharged successfully", "new_money": card.money}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500
