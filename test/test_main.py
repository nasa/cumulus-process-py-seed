import os
import sys
import json
import logging
import unittest
from cumulus_modis import MODIS as Process

logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)

# quiet these loggers
logging.getLogger('boto3').setLevel(logging.CRITICAL)
logging.getLogger('botocore').setLevel(logging.CRITICAL)


class Test(unittest.TestCase):
    """ Testing class for testing process outputs """

    path = os.path.dirname(__file__)
    payloads = [
        os.path.join(path, 'payload.json'),
    ]

    def get_payloads(self):
        """ Get Payload classes of test payloads """
        payloads = []
        for p in self.payloads:
            with open(p) as f:
                payloads.append(json.loads(f.read()))
        return payloads

    def test_init(self):
        """ Test initialization of class """
        for pl in self.get_payloads():
            granule = Process(path=self.path, **pl)
            self.assertTrue(granule.gid)

    def test_process(self):
        """ Process input files """
        for pl in self.get_payloads():
            process = Process(path=self.path, **pl)
            process.process()
            self.assertTrue(len(process.output) > 1)
            for f in process.output:
                self.assertTrue(os.path.exists(f))
            process.clean_output()
