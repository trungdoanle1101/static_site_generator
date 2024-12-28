import os
from utils import *

def generate_page(from_path, template_path, dest_path):
    if not os.path.isfile(from_path):
        raise(f"{from_path} is not a file")

    if not os.path.isfile(template_path):
        raise(f"{template_path} is not a file")

    print(f"Generate page from {from_path} to {dest_path} using {template_path}")
    from_f = open(from_path, "r")
    template_f = open(template_path, "r")

    markdown = from_f.read()
    template = template_f.read()
    node = markdown_to_html_node(markdown)
    content = node.to_html()
    title = extract_title(markdown)
    output = template.replace("{{ Title }}", title).replace("{{ Content }}", content)

    os.makedirs(os.path.dirname(dest_path), exist_ok=True)
    dest_f = open(dest_path, "w")
    dest_f.write(output)

    dest_f.close()
    template_f.close()
    from_f.close()


def generate_pages_recursive(dir_path_content, template_path, dest_dir_path):
    entries = os.listdir(dir_path_content)
    for entry in entries:
        content_path = os.path.join(dir_path_content, entry)
        if os.path.isfile(content_path) and entry.endswith(".md"):
            dest_path = os.path.join(dest_dir_path, entry[:-3] + ".html")
            generate_page(content_path, template_path, dest_path)
        elif os.path.isdir(content_path):
            child_dest_dir_path = os.path.join(dest_dir_path, entry)
            generate_pages_recursive(content_path, template_path, child_dest_dir_path)
        
