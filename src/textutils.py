from leafnode import LeafNode
from textnode import TextType, TextNode
import re
from typing import List
import os

from parentnode import ParentNode
from pathlib import Path


block_type_paragraph = "paragraph"
block_type_heading = "heading"
block_type_code = "code"
block_type_quote = "quote"
block_type_olist = "ordered_list"
block_type_ulist = "unordered_list"

def block_to_html_node(block):
    block_type = block_to_block_type(block)
    if block_type == block_type_paragraph:
        return paragraph_to_html_node(block)
    if block_type == block_type_heading:
        return heading_to_html_node(block)
    if block_type == block_type_code:
        return code_to_html_node(block)
    if block_type == block_type_olist:
        return olist_to_html_node(block)
    if block_type == block_type_ulist:
        return ulist_to_html_node(block)
    if block_type == block_type_quote:
        return quote_to_html_node(block)
    raise ValueError("Invalid block type")


def text_to_children(text):
    text_nodes = text_to_textnodes(text)
    children = []
    for text_node in text_nodes:
        html_node = text_node_to_html_node(text_node)
        children.append(html_node)
    return children


def paragraph_to_html_node(block):
    lines = block.split("\n")
    paragraph = " ".join(lines)
    children = text_to_children(paragraph)
    return ParentNode("p", children)


def heading_to_html_node(block):
    level = 0
    for char in block:
        if char == "#":
            level += 1
        else:
            break
    if level + 1 >= len(block):
        raise ValueError(f"Invalid heading level: {level}")
    text = block[level + 1 :]
    children = text_to_children(text)
    return ParentNode(f"h{level}", children)


def code_to_html_node(block):
    if not block.startswith("```") or not block.endswith("```"):
        raise ValueError("Invalid code block")
    text = block[4:-3]
    children = text_to_children(text)
    code = ParentNode("code", children)
    return ParentNode("pre", [code])


def olist_to_html_node(block):
    items = block.split("\n")
    html_items = []
    for item in items:
        text = item[3:]
        children = text_to_children(text)
        html_items.append(ParentNode("li", children))
    return ParentNode("ol", html_items)


def ulist_to_html_node(block):
    items = block.split("\n")
    html_items = []
    for item in items:
        text = item[2:]
        children = text_to_children(text)
        html_items.append(ParentNode("li", children))
    return ParentNode("ul", html_items)


def quote_to_html_node(block):
    lines = block.split("\n")
    new_lines = []
    for line in lines:
        if not line.startswith(">"):
            raise ValueError("Invalid quote block")
        new_lines.append(line.lstrip(">").strip())
    content = " ".join(new_lines)
    children = text_to_children(content)
    return ParentNode("blockquote", children)

def markdown_to_html_node(markdown):
    blocks = markdown_to_blocks(markdown)
    children = []
    for block in blocks:
        html_node = block_to_html_node(block)
        children.append(html_node)
    return ParentNode("div", children, None)

def text_node_to_html_node(text_node):
    if text_node.text_type == TextType.TEXT.value:
        return LeafNode(None, text_node.text)
    if text_node.text_type == TextType.BOLD.value:
        return LeafNode("b", text_node.text)
    if text_node.text_type == TextType.ITALIC.value:
        return LeafNode("i", text_node.text)
    if text_node.text_type == TextType.CODE.value:
        return LeafNode("code", text_node.text)
    if text_node.text_type == TextType.LINK.value:
        return LeafNode("a", text_node.text, {"href": text_node.url})
    if text_node.text_type == TextType.IMAGE.value:
        return LeafNode("img", "", {"src": text_node.url, "alt": text_node.text})
    raise ValueError(f"Invalid text type: {text_node.text_type}")

def split_nodes_delimiter(old_nodes, delimiter, text_type):
    new_nodes = []
    for old_node in old_nodes:
        if old_node.text_type != TextType.TEXT.value:
            new_nodes.append(old_node)
            continue
        split_nodes = []
        sections = old_node.text.split(delimiter)
        if len(sections) % 2 == 0:
            raise ValueError("Invalid markdown, formatted section not closed")
        for i in range(len(sections)):
            if sections[i] == "":
                continue
            if i % 2 == 0:
                split_nodes.append(TextNode(sections[i], TextType.TEXT))
            else:
                split_nodes.append(TextNode(sections[i], text_type))
        new_nodes.extend(split_nodes)
    return new_nodes


def extract_markdown_images(text: str):
    pattern = r'!\[(.*?)\]\((.*?)\)'
    matches = re.findall(pattern, text)
    
    return matches

def extract_markdown_links(text: str):
    pattern = r'\[(.*?)\]\((.*?)\)'
    matches = re.findall(pattern, text)
    
    return matches

def split_nodes_image(old_nodes):
    new_nodes = []
    for old_node in old_nodes:
        if old_node.text_type != TextType.TEXT.value:
            new_nodes.append(old_node)
            continue
        original_text = old_node.text
        images = extract_markdown_images(original_text)
        if len(images) == 0:
            new_nodes.append(old_node)
            continue
        for image in images:
            sections = original_text.split(f"![{image[0]}]({image[1]})", 1)
            if len(sections) != 2:
                raise ValueError("Invalid markdown, image section not closed")
            if sections[0] != "":
                new_nodes.append(TextNode(sections[0], TextType.TEXT))
            new_nodes.append(
                TextNode(
                    image[0],
                    TextType.IMAGE,
                    image[1],
                )
            )
            original_text = sections[1]
        if original_text != "":
            new_nodes.append(TextNode(original_text, TextType.TEXT))
    return new_nodes

def split_nodes_link(nodes: List[TextNode]) -> List[TextNode]:
    result = []
    
    for node in nodes:
        if node.text_type != TextType.TEXT.value:
            result.append(node)
            continue
            
        # Find all markdown links in the text
        pattern = r'\[(.*?)\]\((.*?)\)'
        splits = []
        curr_index = 0
        
        for match in re.finditer(pattern, node.text):
            # Add text before the link if any
            if match.start() > curr_index:
                splits.append((
                    node.text[curr_index:match.start()],
                    TextType.TEXT,
                    None
                ))
            
            # Add the link
            splits.append((
                match.group(1),  # Link text
                TextType.LINK,
                match.group(2)   # URL
            ))
            
            curr_index = match.end()
        
        # Add remaining text after last link if any
        if curr_index < len(node.text):
            splits.append((
                node.text[curr_index:],
                TextType.TEXT,
                None
            ))
        
        # Create TextNode objects from splits
        result.extend([
            TextNode(text, text_type, url)
            for text, text_type, url in splits
        ])
    
    return result

def text_to_textnodes(text):
    nodes = [TextNode(text, TextType.TEXT)]
    nodes = split_nodes_delimiter(nodes, "**", TextType.BOLD)
    nodes = split_nodes_delimiter(nodes, "*", TextType.ITALIC)
    nodes = split_nodes_delimiter(nodes, "`", TextType.CODE)
    nodes = split_nodes_image(nodes)
    nodes = split_nodes_link(nodes)
    return nodes

def markdown_to_blocks(markdown):
    blocks = [block.strip() for block in markdown.split('\n\n')]
    
    blocks = [block for block in blocks if block]
    
    return blocks

def block_to_block_type(block):
    """
    Determine the type of a markdown block.
    
    Args:
        block (str): A string containing a single markdown block
        
    Returns:
        str: One of: 'paragraph', 'heading', 'code', 'quote', 
             'unordered_list', 'ordered_list'
    """
    if not block:
        return "paragraph"
        
    # Split into lines for multi-line analysis
    lines = block.split('\n')
    first_line = lines[0]
    
    # Check for heading (# followed by space)
    if first_line.startswith(('#', '##', '###', '####', '#####', '######')):
        parts = first_line.split(' ', 1)
        if len(parts) > 1 and len(parts[0]) <= 6:
            return "heading"
            
    # Check for code block (starts and ends with ```)
    if block.startswith('```') and block.endswith('```'):
        return "code"
        
    # Check for quote block (every line starts with >)
    if all(line.startswith('>') for line in lines):
        return "quote"
        
    # Check for unordered list (every line starts with * or -)
    if all(line.strip().startswith(('* ', '- ')) for line in lines):
        return "unordered_list"
        
    # Check for ordered list (lines start with 1. 2. 3. etc)
    if all(line.strip() and line.strip()[0].isdigit() for line in lines):
        expected_number = 1
        for line in lines:
            stripped = line.strip()
            if not stripped.startswith(f"{expected_number}. "):
                break
            expected_number += 1
        else:
            return "ordered_list"
            
    # Default to paragraph
    return "paragraph"

def extract_title(md):
    lines = md.split("\n")
    for line in lines:
        if line.startswith("# "):
            return line[2:]
    raise ValueError("No title found")


def generate_page(from_path, template_path, dest_path):
    print(f" * {from_path} {template_path} -> {dest_path}")
    from_file = open(from_path, "r")
    markdown_content = from_file.read()
    from_file.close()

    template_file = open(template_path, "r")
    template = template_file.read()
    template_file.close()

    node = markdown_to_html_node(markdown_content)
    html = node.to_html()

    title = extract_title(markdown_content)
    template = template.replace("{{ Title }}", title)
    template = template.replace("{{ Content }}", html)

    dest_dir_path = os.path.dirname(dest_path)
    if dest_dir_path != "":
        os.makedirs(dest_dir_path, exist_ok=True)
    to_file = open(dest_path, "w")
    to_file.write(template)

def generate_pages_recursive(dir_path_content, template_path, dest_dir_path):
    for filename in os.listdir(dir_path_content):
        from_path = os.path.join(dir_path_content, filename)
        dest_path = os.path.join(dest_dir_path, filename)
        if os.path.isfile(from_path):
            dest_path = Path(dest_path).with_suffix(".html")
            generate_page(from_path, template_path, dest_path)
        else:
            generate_pages_recursive(from_path, template_path, dest_path)



