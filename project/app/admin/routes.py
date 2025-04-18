from flask import request, current_app, jsonify,g, send_file
import networkx as nx
from sqlalchemy import text
from app.extensions import db
from app.models import Station, Line, StationLine
from app.main.utils import build_station_graph
from . import bp
import itertools
import xlsxwriter
from io import BytesIO
from sqlalchemy import and_


@bp.route("/get_station_by_position", methods=["POST"])
def get_station_by_position():
    data = request.get_json()
    station_name = data.get("station_name")
    line_name = data.get("line_name")
    n = data.get("n")

    if not station_name or not line_name or not isinstance(n, int):
        return jsonify({"error": "Invalid input"}), 400

    try:
        # 查询当前站点的位置
        current_station = StationLine.query.filter_by(station_name=station_name, line_name=line_name).first()
        if not current_station:
            return jsonify({"error": "Station not found in the specified line"}), 404
        
        current_position = current_station.station_code
        
        # 查询向前数第n站
        forward_station = StationLine.query.filter(
            and_(
                StationLine.line_name == line_name,
                StationLine.station_code == current_position - n
            )
        ).first()
        
        # 查询向后数第n站
        backward_station = StationLine.query.filter(
            and_(
                StationLine.line_name == line_name,
                StationLine.station_code == current_position + n
            )
        ).first()
        
        result = {
            "forward_station": forward_station.station_name if forward_station else "Not found",
            "backward_station": backward_station.station_name if backward_station else "Not found"
        }
        
        return jsonify(result), 200
    except Exception as e:
        print(f"Error querying station by position: {e}")
        return jsonify({"error": str(e)}), 500



@bp.route("/station_graph", methods=["GET"])
def station_graph():
    try:
        graph, line_stations = build_station_graph()  # 获取包含线路名的图结构
        
        # 创建一个 BytesIO 对象来存储 Excel 文件
        output = BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        
        # 为每条线路创建一个工作表
        for line_name, stations in line_stations.items():
            worksheet = workbook.add_worksheet(line_name)
            worksheet.write(0, 0, "Station Code")
            worksheet.write(0, 1, "Station Name")
            
            for row_num, (station_code, station_name) in enumerate(stations, start=1):
                worksheet.write(row_num, 0, station_code)
                worksheet.write(row_num, 1, station_name)
        
        workbook.close()
        output.seek(0)
        
        return send_file(output, download_name="station_graph.xlsx", as_attachment=True), 200
    except Exception as e:
        print(f"Error building station graph: {e}")
        return jsonify({"error": str(e)}), 500
    


@bp.route("/shortest_path", methods=["POST"])
def shortest_path():
    try:
        data = request.get_json()
        source = data.get("source")
        target = data.get("target")
        graph = g.station_graph  # 获取全局变量中的图
        
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

        # 获取路径中站点的状态并添加标注
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
    
def get_station_position(station_name, line_name):
    try:
        station_line = StationLine.query.filter_by(station_name=station_name, line_name=line_name).first()
        if station_line:
            return station_line.station_code
        else:
            return "No data found"
    except Exception as e:
        print(f"Error searching data: {e}")
        return jsonify({"error": str(e)}), 500

def get_position_station(position, line_name):
    try:
        station_line = StationLine.query.filter_by(station_code=position, line_name=line_name).first()
        if station_line:
            return station_line.station_name
        else:
            return "No data found"
    except Exception as e:
        print(f"Error searching data: {e}")
        return jsonify({"error": str(e)}), 500

@bp.route("/get_position", methods=["POST"])
def get_position():
    data = request.get_json()
    english_name = data.get("english_name")
    line_name = data.get("line_name")
    position = get_station_position(english_name, line_name)
    if position == "No data found":
        return jsonify({"error": position}), 404
    else:
        return jsonify({"position": position}), 200

@bp.route("/get_station", methods=["POST"])
def get_station():
    data = request.get_json()
    station_name = data.get("english_name")
    line_name = data.get("line_name")
    position = get_station_position(station_name, line_name)
    direction = data.get("direction")
    english_name = get_position_station(position + direction, line_name)
    if english_name == "No data found":
        return jsonify({"error": english_name}), 404
    else:
        return jsonify({"station_name": english_name}), 200

@bp.route("/relation_insert", methods=["POST"])
def relation_insert():
    data = request.get_json()
    station_name_list = data.get("english_name_list")
    line_name = data.get("line_name")
    after_name = data.get("after_name")
    position = 1 if after_name == "SPECIAL" else get_station_position(after_name, line_name) + 1

    try:
        max_position = db.session.query(db.func.max(StationLine.station_code)).filter_by(line_name=line_name).scalar() or 0

        for station_name in station_name_list:
            db.session.query(StationLine).filter(
                StationLine.line_name == line_name,
                StationLine.station_code >= position
            ).update({"station_code": StationLine.station_code + 1})

            new_station_line = StationLine(station_name=station_name, line_name=line_name, station_code=position)
            db.session.add(new_station_line)
            position += 1
            max_position += 1

        db.session.commit()
        g.station_graph,lines_stations = build_station_graph()
        return jsonify({"message": "Relation inserted successfully"}), 201
    except Exception as e:
        db.session.rollback()
        print(f"Error inserting data: {e}")
        return jsonify({"error": str(e)}), 500

@bp.route("/relation_insert_at_position", methods=["POST"])
def relation_insert_at_position():
    data = request.get_json()
    station_name_list = data.get("english_name_list")
    line_name = data.get("line_name")
    insert_position = data.get("position")
    update_code = data.get("update_code", True)  # 默认更新code

    if not station_name_list or not isinstance(station_name_list, list):
        return jsonify({"error": "Invalid station name list"}), 400

    try:
        if update_code:
            # 更新station_code以腾出插入位置
            db.session.query(StationLine).filter(
                StationLine.line_name == line_name,
                StationLine.station_code >= insert_position
            ).update({"station_code": StationLine.station_code + len(station_name_list)})

        for station_name in station_name_list:
            new_station_line = StationLine(station_name=station_name, line_name=line_name, station_code=insert_position)
            db.session.add(new_station_line)
            insert_position += 1

        db.session.commit()
        g.station_graph,lines_stations  = build_station_graph()
        return jsonify({"message": "Relation inserted at position successfully"}), 201
    except Exception as e:
        db.session.rollback()
        print(f"Error inserting data: {e}")
        return jsonify({"error": str(e)}), 500



@bp.route("/relation_delete", methods=["POST"])
def relation_delete():
    data = request.get_json()
    station_name = data.get("english_name")
    line_name = data.get("line_name")
    position = get_station_position(station_name, line_name)

    if position == "No data found":
        return jsonify({"error": position}), 404

    try:
        db.session.query(StationLine).filter(
            StationLine.line_name == line_name,
            StationLine.station_name == station_name
        ).delete()

        db.session.query(StationLine).filter(
            StationLine.line_name == line_name,
            StationLine.station_code > position
        ).update({"station_code": StationLine.station_code - 1})

        db.session.commit()
        g.graph,lines_stations  = build_station_graph()
        return jsonify({"message": "Relation deleted successfully"}), 200
    except Exception as e:
        db.session.rollback()
        print(f"Error deleting data: {e}")
        return jsonify({"error": str(e)}), 500

@bp.route("/line_insert", methods=["POST"])
def line_insert():
    data = request.get_json()
    try:
        new_line = Line(
            line_name=data.get("line_name"),
            start_time=data.get("start_time"),
            end_time=data.get("end_time"),
            intro=data.get("intro"),
            mileage=data.get("mileage"),
            color=data.get("color"),
            first_opening=data.get("first_opening"),
            url=data.get("url")
        )
        db.session.add(new_line)
        db.session.commit()
        g.graph,lines_stations  = build_station_graph()
        return jsonify({"message": "Line inserted successfully"}), 201
    except Exception as e:
        db.session.rollback()
        print(f"Error inserting data: {e}")
        return jsonify({"error": str(e)}), 500

@bp.route("/line_delete", methods=["POST"])
def line_delete():
    data = request.get_json()
    line_name = data.get("line_name")

    try:
        Line.query.filter_by(line_name=line_name).delete()
        db.session.commit()
        g.graph,lines_stations  = build_station_graph()
        return jsonify({"message": "Line deleted successfully"}), 200
    except Exception as e:
        db.session.rollback()
        print(f"Error deleting data: {e}")
        return jsonify({"error": str(e)}), 500

@bp.route("/line_update", methods=["POST"])
def line_update():
    params = request.json
    old_name = params.get("old_name")
    update_params = {}

    for key in ['line_name', 'start_time', 'end_time', 'intro', 'mileage', 'color', 'first_opening', 'url']:
        if params.get(key):
            update_params[key] = params.get(key)

    if not update_params:
        return jsonify({"message": "No update parameters provided"}), 400

    try:
        Line.query.filter_by(line_name=old_name).update(update_params)
        db.session.commit()
        return jsonify({"message": "Line updated successfully"}), 200
    except Exception as e:
        db.session.rollback()
        print(f"Error updating data: {e}")
        return jsonify({"error": str(e)}), 500

@bp.route("/station_delete", methods=["POST"])
def station_delete():
    data = request.get_json()
    chinese_name = data.get("chinese_name")
    english_name = data.get("english_name")

    try:
        Station.query.filter(
            (Station.chinese_name == chinese_name) | 
            (Station.english_name == english_name)
        ).delete()
        db.session.commit()
        g.graph,lines_stations  = build_station_graph()
        return jsonify({"message": "Station deleted successfully"}), 200
    except Exception as e:
        db.session.rollback()
        print(f"Error deleting data: {e}")
        return jsonify({"error": str(e)}), 500

@bp.route("/station_insert", methods=["POST"])
def station_insert():
    data = request.get_json()

    try:
        new_station = Station(
            chinese_name=data.get("chinese_name"),
            english_name=data.get("english_name"),
            district=data.get("district"),
            intro=data.get("intro"),
            status = data.get("status")
        )
        db.session.add(new_station)
        db.session.commit()
        g.graph,lines_stations  = build_station_graph()
        return jsonify({"message": "Station added successfully"}), 201
    except Exception as e:
        db.session.rollback()
        print(f"Error inserting data: {e}")
        return jsonify({"error": str(e)}), 500

@bp.route("/station_update", methods=["POST"])
def station_update():
    params = request.json
    old_english_name = params.get("old_english_name")
    update_params = {}

    for key in ['chinese_name', 'english_name', 'district', 'intro', 'status']:
        if params.get(key):
            update_params[key] = params.get(key)

    if not update_params:
        return jsonify({"message": "No update parameters provided"}), 400

    try:
        Station.query.filter_by(english_name=old_english_name).update(update_params)
        db.session.commit()
        g.graph,lines_stations  = build_station_graph()
        return jsonify({"message": "Station updated successfully"}), 200
    except Exception as e:
        db.session.rollback()
        print(f"Error updating data: {e}")
        return jsonify({"error": str(e)}), 500
