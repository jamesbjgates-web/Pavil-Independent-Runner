import unittest


class EvidenceShapeTests(unittest.TestCase):
    def test_evidence_is_not_self_authorizing(self):
        self.assertNotEqual('SELF_TEST_ONLY', 'DEVELOPMENT_VERIFIED_DURABLE')

    def test_public_preflight_cannot_release(self):
        evidence = {'status': 'PASSED', 'release_eligible': False}
        self.assertFalse(evidence['release_eligible'])


if __name__ == '__main__':
    unittest.main()
