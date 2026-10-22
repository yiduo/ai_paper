import json
from pathlib import Path
import tempfile
import unittest

from ai_value.publication import publication_status


class PublicationStatusTest(unittest.TestCase):
    def test_preparation_and_unverified_claim_do_not_become_publication(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.assertFalse(publication_status(root)['published'])
            (root / 'state').mkdir()
            record = dict(state='published', public=True, repository_url='https://github.com/example/project')
            (root / 'state/publication.json').write_text(json.dumps(record))
            self.assertFalse(publication_status(root)['published'])

    def test_verified_publication_still_reports_incomplete_research(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / 'state').mkdir()
            record = dict(state='published', public=True, remote_verified=True,
                          verified_at='2026-10-22T03:00:00+00:00', verified_commit='a' * 40,
                          repository_url='https://github.com/example/project')
            (root / 'state/publication.json').write_text(json.dumps(record))
            status = publication_status(root)
            self.assertTrue(status['published'])
            self.assertIn('research incomplete', status['release_state'])
            record['verified_commit'] = None
            (root / 'state/publication.json').write_text(json.dumps(record))
            self.assertFalse(publication_status(root)['published'])
