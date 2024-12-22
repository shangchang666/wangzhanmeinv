import os
import re
import platform
import logging

def get_creation_time(file_path):
    """根据平台获取文件的创建时间或修改时间"""
    if platform.system() == 'Windows':
        return os.path.getctime(file_path)  # Windows 获取创建时间
    else:
        return os.path.getmtime(file_path)  # 非 Windows 获取最后修改时间

def find_missing_numbers(renamed_files):
    """找出文件名中缺失的编号"""
    # 提取所有已重命名文件的编号
    existing_numbers = sorted(
        int(re.match(r'^(\d+)', os.path.splitext(f)[0]).group(1)) 
        for f in renamed_files if re.match(r'^\d+\.jpg$', f, re.IGNORECASE)
    )
    
    # 找出缺失的编号
    missing_numbers = []
    for i in range(1, max(existing_numbers, default=0) + 1):
        if i not in existing_numbers:
            missing_numbers.append(i)
    
    return missing_numbers

def rename_images_in_directory(root_dir, verbose=False):
    """重命名指定目录下的图片，按创建时间顺序并累加编号，且将后缀统一为 .jpg"""
    
    for subdir, _, files in os.walk(root_dir):
        if subdir == root_dir:
            continue
        
        if verbose:
            print(f"Processing directory: {subdir}")
        
        # 按创建时间升序获取图片文件，忽略!small等后缀，并只保留标准扩展名
        images = sorted(
            [f for f in files if re.match(r'.*\.(jpg|jpeg|png|gif|webp)(!.*)?$', f, re.IGNORECASE)],
            key=lambda x: get_creation_time(os.path.join(subdir, x))
        )
        
        # 找出当前目录中已经重命名的文件
        renamed_files = {f for f in files if re.match(r'^\d+\.jpg$', f, re.IGNORECASE)}
        
        # 找到缺失的编号并按顺序使用
        missing_numbers = find_missing_numbers(renamed_files)
        
        # 获取当前的编号最大值，避免重命名冲突
        max_number = 0
        for name in renamed_files:
            # 提取已重命名文件的编号
            number_match = re.match(r'^(\d+)', os.path.splitext(name)[0])
            if number_match:
                number = int(number_match.group(1))
                if number > max_number:
                    max_number = number
        
        # 重命名未重命名过的文件
        for image in images:
            # 检查该文件是否已经重命名为 .jpg
            if re.match(r'^\d+\.jpg$', image, re.IGNORECASE):
                if verbose:
                    print(f"Skipping already renamed file: {image}")
                continue  # 跳过已经重命名的文件

            # 移除文件名中的!后缀部分，并统一将扩展名更改为 .jpg
            base_name, _ = os.path.splitext(image)
            new_ext = ".jpg"  # 统一更改为 .jpg

            # 生成新的文件名，优先使用缺失的编号
            if missing_numbers:
                new_number = missing_numbers.pop(0)  # 使用缺失的编号
            else:
                max_number += 1
                new_number = max_number
            
            new_name = f"{new_number}{new_ext}"
            
            old_file = os.path.join(subdir, image)
            new_file = os.path.join(subdir, new_name)

            try:
                os.rename(old_file, new_file)
                renamed_files.add(new_name)  # 将新名称加入已重命名集合
                if verbose:
                    print(f"Renamed: {old_file} -> {new_file}")
            except Exception as e:
                logging.error(f"Error renaming {old_file} to {new_file}: {e}")
                if verbose:
                    print(f"Error renaming {old_file} to {new_file}: {e}")

if __name__ == "__main__":
    # 配置日志记录错误信息
    logging.basicConfig(filename='rename_images.log', level=logging.ERROR)
    
    # 设置要重命名的根目录
    root_directory = r"F:\meituwangzhan\langnvbawangzhan\image"
    
    # 开始重命名操作，verbose=True 显示详细信息
    rename_images_in_directory(root_directory, verbose=True)
