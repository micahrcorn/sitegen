from htmlnode import HTMLNode
import unittest

class TestHTMLNode(unittest.TestCase):
    def test_initialization(self):
        """Test that HTMLNode initializes with correct attributes"""
        node = HTMLNode(
            tag="div",
            value="Hello",
            children=[HTMLNode(tag="p", value="World")],
            props={"class": "container", "id": "main"}
        )
        
        self.assertEqual(node.tag, "div")
        self.assertEqual(node.value, "Hello")
        self.assertEqual(len(node.children), 1)
        self.assertEqual(node.children[0].tag, "p")
        self.assertEqual(node.props, {"class": "container", "id": "main"})

    def test_props_to_html(self):
        """Test that props_to_html correctly formats HTML attributes"""
        node = HTMLNode(
            tag="a",
            props={"href": "https://www.google.com", "target": "_blank"}
        )
        
        expected = ' href="https://www.google.com" target="_blank"'
        self.assertEqual(node.props_to_html(), expected)
        
        # Test with empty props
        empty_node = HTMLNode(tag="div")
        self.assertEqual(empty_node.props_to_html(), '')

    def test_to_html_not_implemented(self):
        """Test that to_html raises NotImplementedError"""
        node = HTMLNode(tag="div")
        
        with self.assertRaises(NotImplementedError):
            node.to_html()

if __name__ == '__main__':
    unittest.main()