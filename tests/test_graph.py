# test_graph.py
import unittest
import os
import tempfile
from src.graph import KnowledgeGraph

class TestKnowledgeGraph(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.data_path = os.path.join(self.temp_dir, "test.json")
        self.kg = KnowledgeGraph(self.data_path)

    def test_add_correction(self):
        self.kg.add_correction("Error A", "Solution A")
        self.assertEqual(len(self.kg.graph['nodes']), 2)

    def test_search_by_text(self):
        self.kg.add_correction("ImportError: foo", "pip install foo")
        results = self.kg.search_by_text("ImportError")
        self.assertEqual(len(results), 1)

    def tearDown(self):
        import shutil
        shutil.rmtree(self.temp_dir)

if __name__ == "__main__":
    unittest.main()