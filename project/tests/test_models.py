from datetime import date, time
from decimal import Decimal
import unittest
from uuid import uuid4

from app import create_app
from app.extensions import db
from app.models import Line, Station, StationLine


class StationLineTestCase(unittest.TestCase):
    def setUp(self):
        app = create_app("config_test.TestConfig")
        context = app.app_context()
        context.push()
        self.addCleanup(context.pop)
        self.addCleanup(db.session.rollback)
        db.create_all()

    def test_station_line_round_trip(self):
        suffix = uuid4().hex
        station = Station(
            chinese_name=f"测试站-{suffix}",
            english_name=f"TestStation-{suffix}",
            district="Test District",
            intro="Test fixture",
        )
        line = Line(
            line_name=f"TestLine-{suffix}",
            start_time=time(6),
            end_time=time(23),
            intro="Test fixture",
            mileage=Decimal("12.30"),
            color="blue",
            first_opening=date(2024, 1, 1),
            url="https://example.com",
        )
        db.session.add_all([station, line])
        db.session.flush()
        db.session.add(StationLine(
            station_name=station.english_name,
            line_name=line.line_name,
            station_code=1,
        ))
        db.session.flush()
        db.session.expire_all()

        association = db.session.get(StationLine, (station.english_name, line.line_name))
        self.assertIsNotNone(association)
        self.assertEqual(association.station_code, 1)
