import os
import shutil
import logging
from textutils import generate_pages_recursive

def copy_directory_recursive(src_dir, dest_dir):
    logging.basicConfig(level=logging.INFO, 
                       format='%(asctime)s - %(message)s',
                       datefmt='%Y-%m-%d %H:%M:%S')
    
    if not os.path.exists(src_dir):
        raise FileNotFoundError(f"Source directory '{src_dir}' does not exist")
    
    if os.path.exists(dest_dir):
        logging.info(f"Cleaning destination directory: {dest_dir}")
        shutil.rmtree(dest_dir)
    
    logging.info(f"Creating destination directory: {dest_dir}")
    os.mkdir(dest_dir)
    
    for item in os.listdir(src_dir):
        sp = os.path.join(src_dir, item)
        dp = os.path.join(dest_dir, item)
        
        if os.path.isfile(sp):
            logging.info(f"Copying file: {sp} -> {dp}")
            shutil.copy(sp, dp)
        else:
            logging.info(f"Copying directory: {sp} -> {dp}")
            copy_directory_recursive(sp, dp)


dir_path_static = "./static"
dir_path_public = "./public"
dir_path_content = "./content"
template_path = "./template.html"

def main():
    copy_directory_recursive(dir_path_static, dir_path_public)

    print("Generating page...")
    
    generate_pages_recursive(dir_path_content, template_path, dir_path_public)

main()