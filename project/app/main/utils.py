from datetime import datetime, date, time, timedelta
import networkx as nx
from app.models import StationLine, Station, Line
from collections import defaultdict

def timedelta_to_time(td):
    if td is None:
        return None
    """将 timedelta 转换为时间格式"""
    total_seconds = int(td.total_seconds())
    hours, remainder = divmod(total_seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    return time(hours, minutes, seconds).isoformat()


def build_station_graph():
    # 创建一个无向图
    graph = nx.Graph()
    
    # 查询所有站点关系
    station_lines = StationLine.query.order_by(StationLine.line_name, StationLine.station_code).all()

    # 构建图结构
    line_stations = defaultdict(list)

    for station_line in station_lines:
        line_stations[station_line.line_name].append((station_line.station_code, station_line.station_name))

    for line_name, stations in line_stations.items():
        # 按照 station_code 排序
        stations.sort()
        for i in range(len(stations) - 1):
            current_station = stations[i][1]
            
            next_station = stations[i + 1][1]
            
            graph.add_node(current_station)
            graph.add_node(next_station)
            graph.add_edge(current_station, next_station)
            
    return graph,line_stations