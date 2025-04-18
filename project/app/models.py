from .extensions import db



class Passenger(db.Model):
    id_number = db.Column(db.String(18), primary_key=True, unique=True, nullable=False)
    name = db.Column(db.String(255), nullable=False)
    phone_number = db.Column(db.BigInteger, nullable=False)
    gender = db.Column(db.String(50), nullable=False)
    district = db.Column(db.String(255), nullable=False)

    def __repr__(self):
        return f'<Passenger {self.id_number}>'

class Card(db.Model):
    code = db.Column(db.BigInteger, primary_key=True, unique=True, nullable=False)
    money = db.Column(db.Numeric(10, 2), nullable=False)
    create_time = db.Column(db.Time, nullable=False)
    create_date = db.Column(db.Date, nullable=False)

    def __repr__(self):
        return f'<Card {self.code}>'
class Station(db.Model):
    chinese_name = db.Column(db.String(255), primary_key=True)
    english_name = db.Column(db.String(255), unique=True, nullable=False)
    district = db.Column(db.String(255), nullable=False)
    intro = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(255), nullable=False, default='运营中')

    def __repr__(self):
        return f'<Station {self.english_name},>'

class Line(db.Model):
    line_name = db.Column(db.String(255), primary_key=True, unique=True, nullable=False)
    start_time = db.Column(db.Time, nullable=False)
    end_time = db.Column(db.Time, nullable=False)
    intro = db.Column(db.Text, nullable=False)
    mileage = db.Column(db.Numeric(10, 2), nullable=False)
    color = db.Column(db.String(50), nullable=False)
    first_opening = db.Column(db.Date, nullable=False)
    url = db.Column(db.String(255), nullable=False)

    def __repr__(self):
        return f'<Line {self.line_name}>'

class StationLine(db.Model):
    station_name = db.Column(db.String(255), db.ForeignKey('station.english_name'), primary_key=True)
    line_name = db.Column(db.String(255), db.ForeignKey('line.line_name'), primary_key=True)
    station_code = db.Column(db.Integer, nullable=False)

    def __repr__(self):
        return f'<StationLine {self.station_name}, {self.line_name}>'

class PassengerRide(db.Model):
    user = db.Column(db.String(18), db.ForeignKey('passenger.id_number'), primary_key=True)
    start_time = db.Column(db.Time, primary_key=True)
    start_date = db.Column(db.Date, primary_key=True)
    end_time = db.Column(db.Time)
    end_date = db.Column(db.Date)
    price = db.Column(db.Integer)
    start_station = db.Column(db.String(255), db.ForeignKey('station.english_name'), nullable=False)
    end_station = db.Column(db.String(255), db.ForeignKey('station.english_name'))

    def __repr__(self):
        return f'<PassengerRide {self.user}, {self.start_station}>'

class CardRide(db.Model):
    user = db.Column(db.BigInteger, db.ForeignKey('card.code'), primary_key=True)
    start_time = db.Column(db.Time, primary_key=True)
    start_date = db.Column(db.Date, primary_key=True)
    end_time = db.Column(db.Time)
    end_date = db.Column(db.Date)
    price = db.Column(db.Integer)
    start_station = db.Column(db.String(255), db.ForeignKey('station.english_name'), nullable=False)
    end_station = db.Column(db.String(255), db.ForeignKey('station.english_name'))

    def __repr__(self):
        return f'<CardRide {self.user}, {self.start_station}>'

class StationChukou(db.Model):
    station_name = db.Column(db.String(255), db.ForeignKey('station.english_name'), primary_key=True)
    chukou_name = db.Column(db.String(255), primary_key=True)
    chukou_id = db.Column(db.Integer, unique=True)

    def __repr__(self):
        return f'<StationChukou {self.station_name}, {self.chukou_name}>'

class Textt(db.Model):
    textt_name = db.Column(db.String(255), primary_key=True, unique=True)

    def __repr__(self):
        return f'<Textt {self.textt_name}>'

class ChukouTextt(db.Model):
    textt_name = db.Column(db.String(255), db.ForeignKey('textt.textt_name'), primary_key=True)
    chukou_id = db.Column(db.Integer, db.ForeignKey('station_chukou.chukou_id'), primary_key=True)

    def __repr__(self):
        return f'<ChukouTextt {self.textt_name}, {self.chukou_id}>'

class BusStation(db.Model):
    bus_station_name = db.Column(db.String(255), primary_key=True, unique=True)

    def __repr__(self):
        return f'<BusStation {self.bus_station_name}>'

class BusStationChukou(db.Model):
    bus_station_name = db.Column(db.String(255), db.ForeignKey('bus_station.bus_station_name'), primary_key=True)
    chukou_id = db.Column(db.Integer, db.ForeignKey('station_chukou.chukou_id'), primary_key=True)

    def __repr__(self):
        return f'<BusStationChukou {self.bus_station_name}, {self.chukou_id}>'

class BusLine(db.Model):
    bus_line_name = db.Column(db.String(255), primary_key=True, unique=True)

    def __repr__(self):
        return f'<BusLine {self.bus_line_name}>'

class BusStationLine(db.Model):
    bus_line_name = db.Column(db.String(255), db.ForeignKey('bus_line.bus_line_name'), primary_key=True)
    bus_station_name = db.Column(db.String(255), db.ForeignKey('bus_station.bus_station_name'), primary_key=True)

    def __repr__(self):
        return f'<BusStationLine {self.bus_line_name}, {self.bus_station_name}>'

class StationPrice(db.Model):
    start_station = db.Column(db.String(255), db.ForeignKey('station.chinese_name'), primary_key=True)
    end_station = db.Column(db.String(255), db.ForeignKey('station.chinese_name'), primary_key=True)
    price = db.Column(db.Integer, nullable=False)

    def __repr__(self):
        return f'<StationPrice {self.start_station} to {self.end_station}>'
