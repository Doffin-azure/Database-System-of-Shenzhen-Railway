import unittest
from app import create_app
from app.extensions import db
from app.models import Station, Line, StationLine

class ExistingDataTestCase(unittest.TestCase):
    def setUp(self):
        """Set up test variables and initialize app."""
        self.app = create_app('config_test.TestConfig')
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_existing_station_lines(self):
        # 查询现有的 StationLine 数据
        station_lines = StationLine.query.all()
        print("StationLine data from database:")
        for sl in station_lines:
            print(f"Station: {sl.station_name}, Line: {sl.line_name}, Code: {sl.station_code}")
        
        # 断言数据库中是否有数据
        self.assertGreater(len(station_lines), 0, "No StationLine data found in the database.")
        
        # 进一步检查某些特定数据
        central_station_line = StationLine.query.filter_by(station_name='CentralStation', line_name='BlueLine').first()
        self.assertIsNotNone(central_station_line, "CentralStation on BlueLine not found in database.")
        self.assertEqual(central_station_line.station_code, 1, "Station code for CentralStation on BlueLine is incorrect.")

if __name__ == '__main__':
    unittest.main()
