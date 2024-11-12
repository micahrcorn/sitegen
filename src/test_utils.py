import unittest
from textutils import (
    split_nodes_delimiter,
    extract_markdown_images,
    extract_markdown_links,
    split_nodes_link,
    text_to_textnodes,
    markdown_to_blocks,
    block_to_block_type,
    extract_title
)

from textnode import TextNode, TextType


class TestInlineMarkdown(unittest.TestCase):
    def test_delim_bold(self):
        node = TextNode("This is text with a **bolded** word", TextType.TEXT)
        new_nodes = split_nodes_delimiter([node], "**", TextType.BOLD)
        self.assertListEqual(
            [
                TextNode("This is text with a ", TextType.TEXT),
                TextNode("bolded", TextType.BOLD),
                TextNode(" word", TextType.TEXT),
            ],
            new_nodes,
        )

    def test_delim_bold_double(self):
        node = TextNode(
            "This is text with a **bolded** word and **another**", TextType.TEXT
        )
        new_nodes = split_nodes_delimiter([node], "**", TextType.BOLD)
        self.assertListEqual(
            [
                TextNode("This is text with a ", TextType.TEXT),
                TextNode("bolded", TextType.BOLD),
                TextNode(" word and ", TextType.TEXT),
                TextNode("another", TextType.BOLD),
            ],
            new_nodes,
        )

    def test_delim_bold_multiword(self):
        node = TextNode(
            "This is text with a **bolded word** and **another**", TextType.TEXT
        )
        new_nodes = split_nodes_delimiter([node], "**", TextType.BOLD)
        self.assertListEqual(
            [
                TextNode("This is text with a ", TextType.TEXT),
                TextNode("bolded word", TextType.BOLD),
                TextNode(" and ", TextType.TEXT),
                TextNode("another", TextType.BOLD),
            ],
            new_nodes,
        )

    def test_delim_italic(self):
        node = TextNode("This is text with an *italic* word", TextType.TEXT)
        new_nodes = split_nodes_delimiter([node], "*", TextType.ITALIC)
        self.assertListEqual(
            [
                TextNode("This is text with an ", TextType.TEXT),
                TextNode("italic", TextType.ITALIC),
                TextNode(" word", TextType.TEXT),
            ],
            new_nodes,
        )

    def test_delim_bold_and_italic(self):
        node = TextNode("**bold** and *italic*", TextType.TEXT)
        new_nodes = split_nodes_delimiter([node], "**", TextType.BOLD)
        new_nodes = split_nodes_delimiter(new_nodes, "*", TextType.ITALIC)
        self.assertListEqual(
            [
                TextNode("bold", TextType.BOLD),
                TextNode(" and ", TextType.TEXT),
                TextNode("italic", TextType.ITALIC),
            ],
            new_nodes,
        )

    def test_delim_code(self):
        node = TextNode("This is text with a `code block` word", TextType.TEXT)
        new_nodes = split_nodes_delimiter([node], "`", TextType.CODE)
        self.assertListEqual(
            [
                TextNode("This is text with a ", TextType.TEXT),
                TextNode("code block", TextType.CODE),
                TextNode(" word", TextType.TEXT),
            ],
            new_nodes,
        )

class TestExtractMarkdown(unittest.TestCase):
    def test_extract_markdown_images(self):
        # Test case 1: Basic example
        text1 = "This is text with a ![rick roll](https://i.imgur.com/aKaOqIh.gif) and ![obi wan](https://i.imgur.com/fJRm4Vk.jpeg)"
        assert extract_markdown_images(text1) == [
            ("rick roll", "https://i.imgur.com/aKaOqIh.gif"),
            ("obi wan", "https://i.imgur.com/fJRm4Vk.jpeg")
        ]
        
        # Test case 2: No images
        text2 = "This is a text with no images"
        assert extract_markdown_images(text2) == []
        
        # Test case 3: Empty alt text
        text3 = "Image with no alt text: ![](https://example.com/image.jpg)"
        assert extract_markdown_images(text3) == [
            ("", "https://example.com/image.jpg")
        ]

    def test_extract_markdown_links(self):
        # Test case 1: Basic example
        text1 = "This is text with a [rick roll](https://i.imgur.com/aKaOqIh.gif) and [obi wan](https://i.imgur.com/fJRm4Vk.jpeg)"
        assert extract_markdown_links(text1) == [
            ("rick roll", "https://i.imgur.com/aKaOqIh.gif"),
            ("obi wan", "https://i.imgur.com/fJRm4Vk.jpeg")
        ]
        
        # Test case 2: No images
        text2 = "This is a text with no images"
        assert extract_markdown_links(text2) == []
        
        # Test case 3: Empty alt text
        text3 = "Image with no alt text: [](https://example.com/image.jpg)"
        assert extract_markdown_links(text3) == [
            ("", "https://example.com/image.jpg")
        ]

class TestSplitLink(unittest.TestCase):
    def test_split_nodes_link(self):
        # Test case 1: Basic link splitting
        node1 = TextNode(
            "This is text with a link [to boot dev](https://www.boot.dev) and [to youtube](https://www.youtube.com/@bootdotdev)",
            TextType.TEXT,
        )
        expected1 = [
            TextNode("This is text with a link ", TextType.TEXT),
            TextNode("to boot dev", TextType.LINK, "https://www.boot.dev"),
            TextNode(" and ", TextType.TEXT),
            TextNode("to youtube", TextType.LINK, "https://www.youtube.com/@bootdotdev"),
        ]
        actual = split_nodes_link([node1])

        assert actual == expected1
        
        # Test case 2: No links
        node2 = TextNode("This is text with no links", TextType.TEXT)
        expected2 = [node2]
        assert split_nodes_link([node2]) == expected2
        
        # Test case 3: Multiple nodes including non-text nodes
        nodes3 = [
            TextNode("Text with [link](url)", TextType.TEXT),
            TextNode("Already a link", TextType.LINK, "http://example.com"),
        ]
        expected3 = [
            TextNode("Text with ", TextType.TEXT),
            TextNode("link", TextType.LINK, "url"),
            TextNode("Already a link", TextType.LINK, "http://example.com"),
        ]
        assert split_nodes_link(nodes3) == expected3

    def test_text_to_textnodes(self):
        nodes = text_to_textnodes(
            "This is **text** with an *italic* word and a `code block` and an ![image](https://i.imgur.com/zjjcJKZ.png) and a [link](https://boot.dev)"
        )
        self.assertListEqual(
            [
                TextNode("This is ", TextType.TEXT),
                TextNode("text", TextType.BOLD),
                TextNode(" with an ", TextType.TEXT),
                TextNode("italic", TextType.ITALIC),
                TextNode(" word and a ", TextType.TEXT),
                TextNode("code block", TextType.CODE),
                TextNode(" and an ", TextType.TEXT),
                TextNode("image", TextType.IMAGE, "https://i.imgur.com/zjjcJKZ.png"),
                TextNode(" and a ", TextType.TEXT),
                TextNode("link", TextType.LINK, "https://boot.dev"),
            ],
            nodes,
        )
class TestMarkdownToBlock(unittest.TestCase):
    def test_markdown_to_blocks(self):
        """Test the markdown_to_blocks function with various inputs"""
        
        # Test 1: Basic three-block markdown
        markdown1 = """# This is a heading

This is a paragraph of text. It has some **bold** and *italic* words inside of it.

* This is the first list item in a list block
* This is a list item
* This is another list item"""

        blocks1 = markdown_to_blocks(markdown1)
        assert len(blocks1) == 3
        assert blocks1[0] == "# This is a heading"
        assert blocks1[1] == "This is a paragraph of text. It has some **bold** and *italic* words inside of it."
        assert blocks1[2] == "* This is the first list item in a list block\n* This is a list item\n* This is another list item"

        # Test 2: Multiple consecutive newlines
        markdown2 = """First block


Second block



Third block"""

        blocks2 = markdown_to_blocks(markdown2)
        assert len(blocks2) == 3
        assert blocks2[0] == "First block"
        assert blocks2[1] == "Second block"
        assert blocks2[2] == "Third block"

        # Test 3: Leading and trailing whitespace
        markdown3 = """   
# Heading with space

* List with space
* Another item
"""

        blocks3 = markdown_to_blocks(markdown3)
        assert len(blocks3) == 2
        assert blocks3[0] == "# Heading with space"
        assert blocks3[1] == "* List with space\n* Another item"

        # Test 4: Empty input
        markdown4 = ""
        blocks4 = markdown_to_blocks(markdown4)
        assert len(blocks4) == 0

        # Test 5: Single block
        markdown5 = "Just one block"
        blocks5 = markdown_to_blocks(markdown5)
        assert len(blocks5) == 1
        assert blocks5[0] == "Just one block"

class TestBlockToBlock(unittest.TestCase):
    def test_block_to_block_type(self):
        """Test the block_to_block_type function with various inputs"""
        
        # Test headings
        assert block_to_block_type("# Heading 1") == "heading"
        assert block_to_block_type("## Heading 2") == "heading"
        assert block_to_block_type("### Heading 3") == "heading"
        assert block_to_block_type("###### Heading 6") == "heading"
        assert block_to_block_type("#NoSpace") == "paragraph"
        assert block_to_block_type("####### Too many #s") == "paragraph"
        
        # Test code blocks
        assert block_to_block_type("```\ncode here\n```") == "code"
        assert block_to_block_type("```python\ndef foo():\n    pass\n```") == "code"
        assert block_to_block_type("```\n```") == "code"
        assert block_to_block_type("``not code``") == "paragraph"
        
        # Test quote blocks
        assert block_to_block_type(">Single line quote") == "quote"
        assert block_to_block_type(">First line\n>Second line") == "quote"
        assert block_to_block_type("Not a >quote") == "paragraph"
        
        # Test unordered lists
        assert block_to_block_type("* Item 1\n* Item 2") == "unordered_list"
        assert block_to_block_type("- Item 1\n- Item 2") == "unordered_list"
        assert block_to_block_type("*No space") == "paragraph"
        
        # Test ordered lists
        assert block_to_block_type("1. First\n2. Second\n3. Third") == "ordered_list"
        assert block_to_block_type("1. Only item") == "ordered_list"
        assert block_to_block_type("1. First\n3. Wrong number") == "paragraph"
        assert block_to_block_type("2. Wrong start") == "paragraph"
        
        # Test paragraphs
        assert block_to_block_type("Just a normal paragraph") == "paragraph"
        assert block_to_block_type("Multiple\nlines\nof text") == "paragraph"
        assert block_to_block_type("") == "paragraph"

    
class TestExtractTitle(unittest.TestCase):
    def test_eq(self):
        actual = extract_title("# This is a title")
        self.assertEqual(actual, "This is a title")

    def test_eq_double(self):
        actual = extract_title(
            """
# This is a title

# This is a second title that should be ignored
"""
        )
        self.assertEqual(actual, "This is a title")

    def test_eq_long(self):
        actual = extract_title(
            """
# title

this is a bunch

of text

* and
* a
* list
"""
        )
        self.assertEqual(actual, "title")

    def test_none(self):
        try:
            extract_title(
                """
no title
"""
            )
            self.fail("Should have raised an exception")
        except Exception as e:
            pass


if __name__ == "__main__":
    unittest.main()