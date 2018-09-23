from repESP.esp_util import EspData, parse_gaussian_esp
from repESP.types import *
from repESP.resp_util import run_resp
from repESP.respin_util import Respin

from my_unittest import TestCase

class TestResp(TestCase):

    def setUp(self) -> None:
        with open("data/methane/methane_mk.esp", 'r') as f:
            self.esp_data = EspData.from_gaussian(parse_gaussian_esp(f))

        # First stage RESP
        self.respin = Respin(
            title="File generated for unit tests only (can been removed).",
            cntrl=Respin.Cntrl(
                nmol=1,
                ihfree=1,
                ioutopt=1,
                qwt=0.0005,
            ),
            wtmol=1.0,
            subtitle="Resp charges for organic molecule",
            charge=0,
            iuniq=5,
            atomic_numbers=[6, 1, 1, 1, 1],
            ivary_numbers=[0, 0, 0, 0, 0]
        )

        self.result_charges = run_resp(
            self.esp_data,
            self.respin
        )

    def test_resp_charges(self) -> None:
        self.assertListsAlmostEqual(
            self.result_charges,
            # Expected values from resp calculations done a while back
            [-0.407205, 0.101907, 0.101695, 0.101695, 0.101907]
        )