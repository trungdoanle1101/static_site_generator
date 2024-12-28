import os
import shutil
from copy_file import copy_from_source_to_dest
from generate import generate_pages_recursive
from textnode import TextType, TextNode
from htmlnode import HTMLNode, LeafNode, ParentNode
from utils import *


def main():
    dir_path_static = "./static"
    dir_path_public = "./public"
    content_path = "./content"
    template_path = "./template.html"
    # output_path = f"{dir_path_public}/index.html"


    if os.path.isdir(dir_path_public):
        shutil.rmtree(dir_path_public)
    copy_from_source_to_dest(dir_path_static, dir_path_public)
    generate_pages_recursive(content_path, template_path, dir_path_public)

    
if __name__ == "__main__":
    main()
