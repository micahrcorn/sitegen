from leafnode import LeafNode
import unittest

class TestLeafNode(unittest.TestCase):
    def test_initialization(self):
        """Test that LeafNode initializes with correct attributes"""
        node = LeafNode(
            tag="b",
            value="Hello",
        )
        
        self.assertEqual(node.tag, "b")
        self.assertEqual(node.value, "Hello")

    def test_props_to_html(self):
        """Test that props_to_html correctly formats HTML attributes"""
        node = LeafNode(
            tag="b",
            value="word"
        )
        
        expected = '<b>word</b>'
        self.assertEqual(node.to_html(), expected)
        

if __name__ == '__main__':
    unittest.main()