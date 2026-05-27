import unittest

from fund_monitor.fund_data import parse_tiantian_jsonp


class FundDataTests(unittest.TestCase):
    def test_parses_tiantian_jsonp_snapshot(self):
        body = (
            'jsonpgz({"fundcode":"000001","name":"华夏成长混合",'
            '"jzrq":"2026-05-26","dwjz":"1.2340","gsz":"1.2100",'
            '"gszzl":"-1.95","gztime":"2026-05-27 14:40"});'
        )

        snapshot = parse_tiantian_jsonp(body)

        self.assertEqual(snapshot.code, "000001")
        self.assertEqual(snapshot.name, "华夏成长混合")
        self.assertEqual(snapshot.nav, 1.234)
        self.assertEqual(snapshot.estimate_nav, 1.21)
        self.assertEqual(snapshot.estimate_change_pct, -1.95)
        self.assertEqual(snapshot.estimate_time, "2026-05-27 14:40")


if __name__ == "__main__":
    unittest.main()
