from pytest import raises
from unittest.mock import patch

from ruuvitag_sensor.ruuvi import RuuviTagSensor
from ruuvitag_sensor.ruuvitag import RuuviTag

# pylint: disable=line-too-long,no-self-use,unused-argument


class TestRuuviTagSensor():

    def get_first_data(self, mac, bt_device):
        # https://ruu.vi/#AjwYAMFc
        data = '043E2A0201030157168974A5F41E0201060303AAFE1616AAFE10EE037275752E76692F23416A7759414D4663CD'
        return data[26:]

    @patch('ruuvitag_sensor.adapters.nix_hci.BleCommunicationNix.get_first_data', get_first_data)
    @patch('ruuvitag_sensor.adapters.dummy.BleCommunicationDummy.get_first_data', get_first_data)
    def test_tag_update_is_valid(self):
        tag = RuuviTag('48:2C:6A:1E:59:3D')

        state = tag.state
        assert state == {}

        state = tag.update()
        assert state['temperature'] == 24
        assert state['pressure'] == 995
        assert state['humidity'] == 30

    def test_false_mac_raise_error(self):
        with raises(ValueError):
            RuuviTag('48:2C:6A:1E')

    def test_tag_correct_properties(self):
        org_mac = 'AA:2C:6A:1E:59:3D'
        tag = RuuviTag(org_mac)

        mac = tag.mac
        state = tag.state
        assert mac == org_mac
        assert state == {}

    def get_datas(self, blacklist=[], bt_device=''):
        datas = [
            ('AA:2C:6A:1E:59:3D', '1E0201060303AAFE1616AAFE10EE037275752E76692F23416A7759414D4663CD'),
            ('BB:2C:6A:1E:59:3D', 'some other device'),
            ('CC:2C:6A:1E:59:3D', '1E0201060303AAFE1616AAFE10EE037275752E76692F23416A7759414D4663CD'),
            ('DD:2C:6A:1E:59:3D', '1E0201060303AAFE1616AAFE10EE037275752E76692F23416A7759414D4663CD'),
            ('EE:2C:6A:1E:59:3D', '1F0201060303AAFE1716AAFE10F9037275752E76692F23416A5558314D417730C3'),
            ('FF:2C:6A:1E:59:3D', '1902010415FF990403291A1ECE1E02DEF94202CA0B5300000000BB'),
            # The following entry is invalid, the data is corrupted
            ('00:2C:6A:1E:59:3D', '1902010415FF990403291A1ECE1E02DEF94202CA0B53BB'),
            ('11:2C:6A:1E:59:3D', '1F0201061BFF99040512FC5394C37C0004FFFC040CAC364200CDCBB8334C884FC4'),
            # The following entry is invalid, it has no MAC
            (None, '1F0201061BFF99040512FC5394C37C0004FFFC040CAC364200CDCBB8334C884FC4'),
            # The following is a ruuvitag with firmware 3.x, sending a non
            # measurement advertisement
            ('CE:D6:05:F5:17:AA', '1E11079ECADC240EE5A9E093F3A3B50100406E0B0952757576692031374141CB'),
            # The following is a ruuvitag with firmware 3.x, sending a
            # measurement advertisement again
            ('CE:D6:05:F5:17:AA', '1F0201061BFF99040511F83B83CC5DFFFCFFFC03DCA7161427D2CED605F517AACB'),
        ]

        for data in datas:
            yield data

    @patch('ruuvitag_sensor.adapters.dummy.BleCommunicationDummy.get_datas',
           get_datas)
    @patch('ruuvitag_sensor.adapters.nix_hci.BleCommunicationNix.get_datas',
           get_datas)
    def test_find_tags(self):
        tags = RuuviTagSensor.find_ruuvitags()
        assert len(tags) == 8

    @patch('ruuvitag_sensor.adapters.dummy.BleCommunicationDummy.get_datas',
           get_datas)
    @patch('ruuvitag_sensor.adapters.nix_hci.BleCommunicationNix.get_datas',
           get_datas)
    def test_get_data_for_sensors(self):
        macs = ['CC:2C:6A:1E:59:3D', 'DD:2C:6A:1E:59:3D', 'EE:2C:6A:1E:59:3D']
        data = RuuviTagSensor.get_data_for_sensors(macs, 4)
        assert len(data) == 3
        assert 'CC:2C:6A:1E:59:3D' in data
        assert 'DD:2C:6A:1E:59:3D' in data
        assert data['CC:2C:6A:1E:59:3D']['temperature'] == 24.0
        assert data['EE:2C:6A:1E:59:3D']['temperature'] == 25.12
        assert data['EE:2C:6A:1E:59:3D']['identifier'] == '0'

    @patch('ruuvitag_sensor.adapters.dummy.BleCommunicationDummy.get_datas',
           get_datas)
    @patch('ruuvitag_sensor.adapters.nix_hci.BleCommunicationNix.get_datas',
           get_datas)
    def test_get_datas(self):
        datas = []
        RuuviTagSensor.get_datas(datas.append)
        assert len(datas) == 8

    @patch('ruuvitag_sensor.adapters.dummy.BleCommunicationDummy.get_datas',
           get_datas)
    @patch('ruuvitag_sensor.adapters.nix_hci.BleCommunicationNix.get_datas',
           get_datas)
    def test_get_datas_with_macs(self):
        datas = []
        macs = ['CC:2C:6A:1E:59:3D', 'DD:2C:6A:1E:59:3D']
        RuuviTagSensor.get_datas(datas.append, macs)
        assert len(datas) == 2
