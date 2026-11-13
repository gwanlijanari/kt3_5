import unittest
import threading
import time
import urllib.request
import urllib.error
import json
import os
import tempfile

os.environ["ROLE"] = "api"
os.environ["DATA_DIR"] = tempfile.mkdtemp()
os.environ["PORT"] = "8080"

import app


class TestApp(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        os.makedirs(os.environ["DATA_DIR"], exist_ok=True)
        with app.connect() as db:
            db.execute(
                "CREATE TABLE IF NOT EXISTS requests (id INTEGER PRIMARY KEY AUTOINCREMENT, kind TEXT NOT NULL, created TEXT NOT NULL, request_key TEXT NOT NULL UNIQUE)"
            )

        cls.server = app.ThreadingHTTPServer(("127.0.0.1", 8080), app.Handler)
        cls.thread = threading.Thread(target=cls.server.serve_forever)
        cls.thread.daemon = True
        cls.thread.start()
        time.sleep(0.5)

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()

    def test_create_request(self):
        req = urllib.request.Request(
            "http://127.0.0.1:8080/api/requests",
            data=json.dumps({"kind": "screen", "key": "test-key-1"}).encode(),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(req) as response:
            self.assertEqual(response.status, 201)
