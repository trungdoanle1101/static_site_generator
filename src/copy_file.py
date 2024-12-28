import os
import shutil

def copy_from_source_to_dest(source_dir, dest_dir):
    if not os.path.isdir(source_dir):
        raise Exception(f"Invalid source directory: {dest_dir}")
    
    if not os.path.exists(dest_dir):
        os.mkdir(dest_dir)

    for entry in os.listdir(source_dir):
        source_path = os.path.join(source_dir, entry)
        dest_path = os.path.join(dest_dir, entry)
        if os.path.isfile(source_path):
            shutil.copy(source_path, dest_path)
        else:
            copy_from_source_to_dest(source_path, dest_path)
