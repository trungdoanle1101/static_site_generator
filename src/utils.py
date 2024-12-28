import re
from textnode import TextNode, TextType, BlockType
from htmlnode import LeafNode, HTMLNode, ParentNode


def text_node_to_html_node(text_node):
    match text_node.text_type:
        case TextType.TEXT:
            return LeafNode(None, text_node.text)
        case TextType.BOLD:
            return LeafNode("b", text_node.text)
        case TextType.ITALIC:
            return LeafNode("i", text_node.text)
        case TextType.CODE:
            return LeafNode("code", text_node.text)
        case TextType.LINK:
            return LeafNode("a", text_node.text, {"href": text_node.url})
        case TextType.IMAGE:
            return LeafNode("img", "", {"src": text_node.url, "alt": text_node.text})
        case _:
            raise Exception("unknown TextType from TextNode")


def split_nodes_delimiter(old_nodes, delimiter, text_type):
    if not ((delimiter == "`" and text_type == TextType.CODE)
        or (delimiter == "*" and text_type == TextType.ITALIC)
        or (delimiter == "**" and text_type == TextType.BOLD)):
        raise Exception(f"invalid delimiter {delimiter} for TextType {text_type.value}")
    
    new_nodes = []
    for old_node in old_nodes:
        if not isinstance(old_node, TextNode):
            raise Exception("old_nodes must be TextNode(s)")
        if old_node.text_type != TextType.TEXT:
            new_nodes.append(old_node)
            continue
        
        text = old_node.text
        count_delimiter = text.count(delimiter)
        if count_delimiter % 2 == 1:
            raise Exception("invalid text: need closing delimiter")


        split_texts = text.split(delimiter)
        nodes = []
        for i, text in enumerate(split_texts):
            if text == "":
                continue
            if i % 2 == 0:
                nodes.append(TextNode(text, TextType.TEXT))
            else:
                nodes.append(TextNode(text, text_type))
        new_nodes.extend(nodes)

    return new_nodes


def split_nodes_image(old_nodes):
    new_nodes = []
    for node in old_nodes:
        if not isinstance(node, TextNode):
            raise Exception("node must be a TextNode")

        if node.text_type != TextType.TEXT:
            new_nodes.append(node)
            continue
        
        text = node.text
        extracted_images = extract_markdown_images(text)
        for image_alt, image_link in extracted_images:
            sections = text.split(f"![{image_alt}]({image_link})", 1)
            if len(sections) != 2:
                raise ValueError("invalid markdown, image section not closed")
            if sections[0] != "":
                new_nodes.append(TextNode(sections[0], TextType.TEXT))
            new_nodes.append(TextNode(image_alt, TextType.IMAGE, image_link))
            text = sections[1]
        if text != "":
            new_nodes.append(TextNode(text, TextType.TEXT))

    return new_nodes


def split_nodes_link(old_nodes):
    new_nodes = []
    for node in old_nodes:
        if not isinstance(node, TextNode):
            raise Exception
        
        if node.text_type != TextType.TEXT:
            new_nodes.append(node)
            continue

        text = node.text
        extracted_links = extract_markdown_links(text)

        for link_text, link_url in extracted_links:
            sections = text.split(f"[{link_text}]({link_url})")
            if len(sections) != 2:
                raise ValueError("invalid markdown, link section not closed")
            if sections[0] != "":
                new_nodes.append(TextNode(sections[0], TextType.TEXT))
            new_nodes.append(TextNode(link_text, TextType.LINK, link_url))
            text = sections[1]
        if text != "":
            new_nodes.append(TextNode(text, TextType.TEXT))
    return new_nodes

def extract_markdown_images(text):
    image_regex = r"!\[([^\[\]]*)\]\(([^\(\)]*)\)"
    return re.findall(image_regex, text)


def extract_markdown_links(text):
    link_regex = r"(?<!!)\[([^\[\]]*)\]\(([^\(\)]*)\)"
    return re.findall(link_regex, text)


def text_to_textnodes(text):
    nodes = [TextNode(text, TextType.TEXT)]
    nodes = split_nodes_delimiter(nodes, "**", TextType.BOLD)
    nodes = split_nodes_delimiter(nodes, "*", TextType.ITALIC)
    nodes = split_nodes_delimiter(nodes, "`", TextType.CODE)
    nodes = split_nodes_image(nodes)
    nodes = split_nodes_link(nodes)
    return nodes


def markdown_to_blocks(markdown):
    blocks = markdown.split("\n\n")
    filtered_blocks = []
    for block in blocks:
        if block == "":
            continue
        block = block.strip()
        filtered_blocks.append(block)
    return filtered_blocks


def block_to_block_type(block):
    heading_regex = r"^#{1,6} .*"
    code_regex = r"^`{3}(.|\n)*`{3}$"
    quote_regex = r"^>.*"
    unordered_list_regex = r"^[\-\*] .*"
    lines = block.split("\n")
    
    if re.fullmatch(heading_regex, block):
        return BlockType.HEADING
    
    if re.fullmatch(code_regex, block):
        return BlockType.CODE

    if all(re.search(quote_regex, line) for line in lines):
        return BlockType.QUOTE
    
    if all([line.startswith(f"{i}. ") for i, line in enumerate(lines, 1)]):
        return BlockType.ORDERED_LIST
    
    if all(re.search(unordered_list_regex, line) for line in lines):
        return BlockType.UNORDERED_LIST
    
    ## Need ordered list regex
    return BlockType.PARAGRAPH


def text_to_children(text):
    text_nodes = text_to_textnodes(text)
    html_nodes = [text_node_to_html_node(node) for node in text_nodes]
    return html_nodes

def markdown_to_html_node(markdown):
    blocks = markdown_to_blocks(markdown)
    block_children = []
    for block in blocks:
        block_type = block_to_block_type(block)
        node = None
        match block_type:
            case BlockType.HEADING:
                searched = re.search(r"^#{1,6} ", block)
                if searched is None:
                    raise Exception("Invalid heading")
                searched = searched[0]
                level = len(searched) - 1
                tag = f"h{level}"
                text = block[level + 1: ]
                children = text_to_children(text)
                node = ParentNode(tag, children)
            case BlockType.PARAGRAPH:
                lines = block.split("\n")
                paragraph = " ".join(lines)
                children = text_to_children(paragraph)
                node = ParentNode("p", children)
            case BlockType.CODE:
                if not block.startswith("```") or not block.endswith("```"):
                    raise ValueError("Invalid code block")
                text = block[4:-3]
                children = text_to_children(text)
                node = ParentNode("pre", [ParentNode("code", children)])
            case BlockType.UNORDERED_LIST:
                item_strings = [line[2:] for line in block.split("\n")]
                item_nodes = []
                for item in item_strings:
                    item_children_nodes = text_to_children(item)
                    item_nodes.append(ParentNode("li", item_children_nodes))
                node = ParentNode("ul", children=item_nodes)
            case BlockType.ORDERED_LIST:
                item_strings = [line[3:] for line in block.split("\n")]
                item_nodes = []
                for item in item_strings:
                    item_children_nodes = text_to_children(item)
                    item_nodes.append(ParentNode("li", item_children_nodes))
                node = ParentNode("ol", children=item_nodes)
            case BlockType.QUOTE:
                item_strings = [line.lstrip(">").strip() for line in block.split("\n")]
                content = " ".join(item_strings)
                children = text_to_children(content)
                node = ParentNode("blockquote", children)
            case _:
                raise Exception(f"unknown BlockType {block_type}")
        block_children.append(node)
    
    return ParentNode("div", block_children)


def extract_title(markdown):
    lines = markdown.split("\n")
    for line in lines:
        if line.startswith("# "):
            return line[2:].strip()
    raise Exception("markdown has no h1 header")