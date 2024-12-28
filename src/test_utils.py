import unittest
from textnode import TextNode, TextType
from utils import *

class TestUtils(unittest.TestCase):
    def test_split_node(self):
        node = TextNode("This is text with a `code block` word", TextType.TEXT)
        new_nodes = split_nodes_delimiter([node], "`", TextType.CODE)
        results = [
            TextNode("This is text with a ", TextType.TEXT),
            TextNode("code block", TextType.CODE),
            TextNode(" word", TextType.TEXT),
        ]
        self.assertListEqual(new_nodes, results)
            
    
    def test_split_node1(self):
        node = TextNode("This is text with a *italic block* word", TextType.TEXT)
        new_nodes = split_nodes_delimiter([node], "*", TextType.ITALIC)
        results = [
            TextNode("This is text with a ", TextType.TEXT),
            TextNode("italic block", TextType.ITALIC),
            TextNode(" word", TextType.TEXT),
        ]
        self.assertListEqual(new_nodes, results)
    
    def test_split_node2(self):
        node = TextNode("This is text with a **bold block** word", TextType.TEXT)
        new_nodes = split_nodes_delimiter([node], "**", TextType.BOLD)
        results = [
            TextNode("This is text with a ", TextType.TEXT),
            TextNode("bold block", TextType.BOLD),
            TextNode(" word", TextType.TEXT),
        ]
        self.assertListEqual(new_nodes, results)
    
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
    
    def test_split_nodes_link(self):
        node = TextNode(
            "This is text with a link [to boot dev](https://www.boot.dev) and [to youtube](https://www.youtube.com/@bootdotdev)",
            TextType.TEXT,
        )
        actual = split_nodes_link([node])
        expected = [
            TextNode("This is text with a link ", TextType.TEXT),
            TextNode("to boot dev", TextType.LINK, "https://www.boot.dev"),
            TextNode(" and ", TextType.TEXT),
            TextNode(
                "to youtube", TextType.LINK, "https://www.youtube.com/@bootdotdev"
            ),
        ]
        self.assertListEqual(actual, expected)
    
    def test_split_nodes_image(self):
        node = TextNode(
            "This is text with a ![rick roll](https://i.imgur.com/aKaOqIh.gif) and ![obi wan](https://i.imgur.com/fJRm4Vk.jpeg)",
            TextType.TEXT
        )
        actual = split_nodes_image([node])
        expected = [
            TextNode("This is text with a ", TextType.TEXT),
            TextNode("rick roll", TextType.IMAGE, "https://i.imgur.com/aKaOqIh.gif"),
            TextNode(" and ", TextType.TEXT),
            TextNode("obi wan", TextType.IMAGE, "https://i.imgur.com/fJRm4Vk.jpeg"),
        ]
        self.assertListEqual(actual, expected)
    
    def test_split_nodes_image_and_link(self):
        node = TextNode(
            "This is text with a ![rick roll](https://i.imgur.com/aKaOqIh.gif) and [to youtube](https://www.youtube.com/@bootdotdev)",
            TextType.TEXT
        )
        actual = split_nodes_image([node])
        actual = split_nodes_link(actual)
        expected = [
            TextNode("This is text with a ", TextType.TEXT),
            TextNode("rick roll", TextType.IMAGE, "https://i.imgur.com/aKaOqIh.gif"),
            TextNode(" and ", TextType.TEXT),
            TextNode(
                "to youtube", TextType.LINK, "https://www.youtube.com/@bootdotdev"
            ),
        ]
        self.assertListEqual(actual, expected)

        actual = split_nodes_link([node])
        actual = split_nodes_image(actual)
        self.assertListEqual(actual, expected)

    def test_extract_markdown_images(self):
        text = "This is text with a ![rick roll](https://i.imgur.com/aKaOqIh.gif) and ![obi wan](https://i.imgur.com/fJRm4Vk.jpeg)"
        actual = extract_markdown_images(text)
        expected = [("rick roll", "https://i.imgur.com/aKaOqIh.gif"), ("obi wan", "https://i.imgur.com/fJRm4Vk.jpeg")] 
        self.assertListEqual(actual, expected)
    
    def test_extract_markdown_links(self):
        text = "This is text with a link [to boot dev](https://www.boot.dev) and [to youtube](https://www.youtube.com/@bootdotdev)"
        actual = extract_markdown_links(text)
        expected = [("to boot dev", "https://www.boot.dev"), ("to youtube", "https://www.youtube.com/@bootdotdev")]
        self.assertListEqual(actual, expected)

    def test_text_to_textnodes(self):
        text = "This is **text** with an *italic* word and a `code block` and an ![obi wan image](https://i.imgur.com/fJRm4Vk.jpeg) and a [link](https://boot.dev)"
        actual = text_to_textnodes(text)
        expected = [
            TextNode("This is ", TextType.TEXT),
            TextNode("text", TextType.BOLD),
            TextNode(" with an ", TextType.TEXT),
            TextNode("italic", TextType.ITALIC),
            TextNode(" word and a ", TextType.TEXT),
            TextNode("code block", TextType.CODE),
            TextNode(" and an ", TextType.TEXT),
            TextNode("obi wan image", TextType.IMAGE, "https://i.imgur.com/fJRm4Vk.jpeg"),
            TextNode(" and a ", TextType.TEXT),
            TextNode("link", TextType.LINK, "https://boot.dev"),
        ]
        self.assertListEqual(actual, expected)
    
    def test_markdown_to_blocks(self):
        markdown = """# This is a heading

This is a paragraph of text. It has some **bold** and *italic* words inside of it.

* This is the first list item in a list block
* This is a list item
* This is another list item"""
        actual = markdown_to_blocks(markdown)
        expected = ["# This is a heading",
                    "This is a paragraph of text. It has some **bold** and *italic* words inside of it.",
                    """* This is the first list item in a list block
* This is a list item
* This is another list item""",
                    ]
        return self.assertListEqual(actual, expected)
    
    def test_markdown_to_blocks_newlines(self):
        md = """
This is **bolded** paragraph




This is another paragraph with *italic* text and `code` here
This is the same paragraph on a new line

* This is a list
* with items
"""
        blocks = markdown_to_blocks(md)
        self.assertListEqual(
            blocks,
            [
                "This is **bolded** paragraph",
                "This is another paragraph with *italic* text and `code` here\nThis is the same paragraph on a new line",
                "* This is a list\n* with items",
            ],
        )

    def test_block_to_block_type_heading(self):
        blocks = ["# head", "## head", "### head",
                  "#### head", "##### head", "###### head"]
        actual = [block_to_block_type(block) for block in blocks]
        expected = [BlockType.HEADING] * len(blocks)
        self.assertListEqual(actual, expected)

        wrong_blocks = ["####### a21", "#123", "#head"]
        actual = [block_to_block_type(block) for block in wrong_blocks]
        for block in actual:
            self.assertNotEqual(block, BlockType.HEADING)
        
    
    def test_block_to_block_type_code(self):
        blocks = ["```hello```", "```\nhello```", "```\nhello\n```"]
        actual = [block_to_block_type(block) for block in blocks]
        expected = [BlockType.CODE] * len(blocks)
        self.assertListEqual(actual, expected)

        wrong_blocks = ["```hello", "`hello", "hello```", "hello```hello```"]
        actual = [block_to_block_type(block) for block in wrong_blocks]
        for block in actual:
            self.assertNotEqual(block, BlockType.CODE)
    
    def test_block_to_block_type_quote(self):
        blocks = ["> quote", ">quote", ">>quote", """>quote1\n>quote2"""]
        actual = [block_to_block_type(block) for block in blocks]
        expected = [BlockType.QUOTE] * len(blocks)
        self.assertListEqual(actual, expected)

        wrong_blocks = ["<noquote", "noquote", "quote<", """>quote\nnoquote"""]
        actual = [block_to_block_type(block) for block in wrong_blocks]
        for block in actual:
            self.assertNotEqual(block, BlockType.QUOTE)
        
    def test_block_to_block_type_unordered_list(self):
        blocks = ["- item", "* item", """- item\n- item2""",
                  """* item\n* item""", """- item\n* item""",
                  """* item\n- item"""]
        actual = [block_to_block_type(block) for block in blocks]
        expected = [BlockType.UNORDERED_LIST] * len(blocks)
        self.assertListEqual(actual, expected)

        wrong_blocks = ["-item", "*item", "-* item",
                        """* item\n*item""", """*item\n- item"""]
        actual = [block_to_block_type(block) for block in wrong_blocks]
        for block in actual:
            self.assertNotEqual(block, BlockType.UNORDERED_LIST)
    
    def test_block_to_block_type_ordered_list(self):
        blocks = ["1. first item", """1. first item\n2. second item\n3. third item"""]
        actual = [block_to_block_type(block) for block in blocks]
        expected = [BlockType.ORDERED_LIST] * len(blocks)
        self.assertListEqual(actual, expected)

        wrong_blocks = ["1.nospace", "0. start with zero", "2. second item",
                        """1. first\n3. no continuity""", "1- how about this"]
        actual = [block_to_block_type(block) for block in wrong_blocks]
        for block in actual:
            self.assertNotEqual(block, BlockType.ORDERED_LIST)

    def test_block_to_block_type_paragraph(self):
        blocks = ["block", "-item", "*item",
                  """```code``""", """``code``""",
                  """####### not a header"""]
        actual = [block_to_block_type(block) for block in blocks]
        expected = [BlockType.PARAGRAPH] * len(blocks)
        self.assertListEqual(actual, expected)
    
    def test_paragraph(self):
        md = """
This is **bolded** paragraph
text in a p
tag here

"""

        node = markdown_to_html_node(md)
        html = node.to_html()
        self.assertEqual(
            html,
            "<div><p>This is <b>bolded</b> paragraph text in a p tag here</p></div>",
        )
    
    def test_paragraphs(self):
        md = """
This is **bolded** paragraph
text in a p
tag here

This is another paragraph with *italic* text and `code` here

"""

        node = markdown_to_html_node(md)
        html = node.to_html()
        self.assertEqual(
            html,
            "<div><p>This is <b>bolded</b> paragraph text in a p tag here</p><p>This is another paragraph with <i>italic</i> text and <code>code</code> here</p></div>",
        )

    def test_lists(self):
        md = """
- This is a list
- with items
- and *more* items

1. This is an `ordered` list
2. with items
3. and more items

"""

        node = markdown_to_html_node(md)
        html = node.to_html()
        self.assertEqual(
            html,
            "<div><ul><li>This is a list</li><li>with items</li><li>and <i>more</i> items</li></ul><ol><li>This is an <code>ordered</code> list</li><li>with items</li><li>and more items</li></ol></div>",
        )

    def test_headings(self):
        md = """
# this is an h1

this is paragraph text

## this is an h2
"""

        node = markdown_to_html_node(md)
        html = node.to_html()
        self.assertEqual(
            html,
            "<div><h1>this is an h1</h1><p>this is paragraph text</p><h2>this is an h2</h2></div>",
        )

    def test_blockquote(self):
        md = """
> This is a
> blockquote block

this is paragraph text

"""

        node = markdown_to_html_node(md)
        html = node.to_html()
        self.assertEqual(
            html,
            "<div><blockquote>This is a blockquote block</blockquote><p>this is paragraph text</p></div>",
        )
    
    def test_extract_title(self):
        markdown = "#  Hello   "
        actual = extract_title(markdown)
        self.assertEqual(actual, "Hello")
        
        markdown = "Something here first\n# then here's the header "
        actual = extract_title(markdown)
        self.assertEqual(actual, "then here's the header")

        markdown = "This is gona raise"
        self.assertRaises(Exception, extract_title, markdown)

if __name__ == "__main__":
    unittest.main()