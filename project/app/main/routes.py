from flask import request, jsonify,  render_template
from . import bp
from app.models import PassengerRide, CardRide, StationPrice, db, Card
from datetime import datetime, date, time, timedelta
from sqlalchemy import text
from app.main.utils import timedelta_to_time
from app import g
import networkx as nx
import itertools
from app.models import Station



@bp.route('/')
def index():
    return render_template('index.html')

@bp.route("/shortest_path", methods=["POST"])
def shortest_path():
    try:
        data = request.get_json()
        source = data.get("source")
        target = data.get("target")
        graph = g.station_graph  # 获取全局变量中的图
       
        # 查找最短路径
        path = nx.shortest_path(graph, source=source, target=target)

        annotated_path = []
        for station in path:
            station_obj = Station.query.filter_by(english_name=station).first()
            if station_obj:
                status = station_obj.status
                if status in ["建设中", "关闭中"]:
                    station += f" ({status})"
                    if station == path[-1]:
                        return jsonify({"error": "The destination station is under construction or closed"}), 404
            annotated_path.append(station)
        
        
        return jsonify({"path": annotated_path}), 200
    except nx.NetworkXNoPath:
        return jsonify({"error": "No path found between the nodes"}), 404
    except Exception as e:
        print(f"Error finding shortest path: {e}")
        return jsonify({"error": str(e)}), 500
    
@bp.route("/alternative_paths", methods=["POST"])
def alternative_paths():
    try:
        data = request.get_json()
        source = data.get("source")
        target = data.get("target")
        graph = g.station_graph  # 获取全局变量中的图

        # 查找最多三条最短路径
        paths_generator = nx.shortest_simple_paths(graph, source=source, target=target)
        paths = list(itertools.islice(paths_generator, 10))
        
        # 去重
        unique_paths = []
        seen_paths = set()
        for path in paths:
            path_tuple = tuple(path)
            if path_tuple not in seen_paths:
                unique_paths.append(path)
                seen_paths.add(path_tuple)
            if len(unique_paths) >= 3:
                break
        
        if not unique_paths:
            return jsonify({"error": "No paths found between the nodes"}), 404

        
        annotated_paths = []
        for path in unique_paths:
            annotated_path = []
            for station in path:
                station_obj = Station.query.filter_by(english_name=station).first()
                if station_obj:
                    status = station_obj.status
                    if status in ["建设中", "关闭中"]:
                        station += f" ({status})"
                        if station == path[-1]:
                            return jsonify({"error": "The destination station is under construction or closed"}), 404
                    
                annotated_path.append(station)
            annotated_paths.append(annotated_path)

        return jsonify({
            "shortest_path": annotated_paths[0],
            "alternative_paths": annotated_paths
        }), 200
    except nx.NetworkXNoPath:
        return jsonify({"error": "No path found between the nodes"}), 404
    except Exception as e:
        print(f"Error finding alternative paths: {e}")
        return jsonify({"error": str(e)}), 500

@bp.route("/board", methods=["POST"])
def board_passenger():
    data = request.get_json()
    user = data.get("user")
    start_station = data.get("start_station")
    start_date = date.today().strftime("%Y-%m-%d")
    start_time = datetime.now().strftime("%H:%M:%S")

    print(f"Received data: {data}")

    ride = PassengerRide if len(user) > 10 else CardRide

    new_ride = ride(
        user=user,
        start_station=start_station,
        start_date=start_date,
        start_time=start_time
    )

    try:
        db.session.add(new_ride)
        db.session.commit()
        return jsonify({"message": "Passenger boarded successfully"}), 201
    except Exception as e:
        db.session.rollback()
        print(f"Error inserting data: {e}")
        return jsonify({"error": str(e)}), 500

@bp.route("/exit", methods=["POST"])
def exit_passenger():
    data = request.get_json()
    user = data.get("user")
    end_station = data.get("end_station")
    end_date = date.today().strftime("%Y-%m-%d")
    end_time = datetime.now().strftime("%H:%M:%S")
    bussiness_type = data.get("bussiness_type")

    ride = PassengerRide if len(user) > 10 else CardRide
    ride_query = ride.query.filter_by(user=user, end_time=None).first()

    if not ride_query:
        return jsonify({"error": "No boarding record found"}), 404

    start_station = ride_query.start_station
    price_query = StationPrice.query.filter_by(start_station=start_station, end_station=end_station).first()

    if not price_query:
        return jsonify({"error": "Price data not found"}), 404

    price = int(price_query.price)

    if bussiness_type == "True":
        price *= 2

    if len(user) < 10:
        card = Card.query.get(user)
        if not card or card.money < int(price):
            return jsonify({"error": "Insufficient balance"}), 400
        card.money -= price

    ride_query.end_station = end_station
    ride_query.end_date = end_date
    ride_query.end_time = end_time
    ride_query.price = price

    try:
        db.session.commit()
        return jsonify({"message": f"Passenger exited successfully, price: {price}"}), 200
    except Exception as e:
        db.session.rollback()
        print(f"Error updating data: {e}")
        return jsonify({"error": str(e)}), 500

@bp.route("/active_rides", methods=["GET"])
def get_active_rides():
    passenger_rides = PassengerRide.query.filter_by(end_time=None).all()
    card_rides = CardRide.query.filter_by(end_time=None).all()

    active_rides = [
        {
            "user": ride.user,
            "start_station": ride.start_station,
            "start_date": ride.start_date.strftime("%Y-%m-%d"),
            "start_time": ride.start_time.strftime("%H-%M-%S")
        }
        for ride in passenger_rides
    ] + [
        {
            "user": ride.user,
            "start_station": ride.start_station,
            "start_date": ride.start_date.strftime("%Y-%m-%d"),
            "start_time": ride.start_time.strftime("%H-%M-%S")
        }
        for ride in card_rides
    ]
    return jsonify({"active_rides": active_rides}), 200

@bp.route("/search_rides", methods=["POST"])
def search_rides():
    params = request.json
    conditions = []
    
    if params.get("user"):
        conditions.append(f"AND user = '{params['user']}'")
    if params.get("start_station"):
        conditions.append(f"AND start_station = '{params['start_station']}'")
    if params.get("end_station"):
        conditions.append(f"AND end_station = '{params['end_station']}'")
    if params.get("start_date"):
        conditions.append(f"AND start_date >= '{params['start_date']}'")
    if params.get("end_date"):
        conditions.append(f"AND end_date <= '{params['end_date']}'")

    if not conditions:
        return jsonify({"error": "No search criteria provided"}), 400

    where_clause = " ".join(conditions)

    passenger_rides_query = f"SELECT * FROM passenger_ride WHERE 1=1 {where_clause}"
    card_rides_query = f"SELECT * FROM card_ride WHERE 1=1 {where_clause}"

    passenger_rides = db.session.execute(text(passenger_rides_query)).fetchall()
    card_rides = db.session.execute(text(card_rides_query)).fetchall()

    rides = [
        {
            "user": ride[0],
            "start_station": ride[6],
            "end_station": ride[7],
            "start_date": ride[2],
            "end_date": ride[4],
            "start_time": timedelta_to_time(ride[1]),
            "end_time": timedelta_to_time(ride[3]),
            "price": ride[5],
        }
        for ride in passenger_rides
    ] + [
        {
            "user": ride[0],
            "start_station": ride[6],
            "end_station": ride[7],
            "start_date": ride[2],
            "end_date": ride[4],
            "start_time": timedelta_to_time(ride[1]),
            "end_time": timedelta_to_time(ride[3]),
            "price": ride[5],
        }
        for ride in card_rides
    ]
    total_count = len(rides)
    return jsonify({"rides": rides, "total_count": total_count}), 200

