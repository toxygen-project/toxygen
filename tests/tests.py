from src.settings import Settings


class TestSettings():
     
    def test_creation(self):
        s = Settings()
        assert s['ipv6_enabled'] is not None
        assert s['notifications'] is not None
