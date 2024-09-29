import os
import sys
import math

from PIL import Image, ExifTags

def get_cmd_args():
    origin_dir = "."
    target_dir = "./out"
    name_format = "ymd_i"

    if len(sys.argv) >= 2:
        origin_dir = sys.argv[1]

    if len(sys.argv) >= 3:
        target_dir = sys.argv[2]

    if len(sys.argv) >= 4:
        name_format = sys.argv[3]

    return (origin_dir, target_dir, name_format)


def get_date_taken(path):
    exif_info = Image.open(path).getexif()
    if not exif_info:
        raise Exception('Image {0} does not have EXIF data.'.format(path))
    
    exif_ifd = exif_info.get_ifd(ExifTags.IFD.Exif)
    if not exif_ifd:
        raise Exception('Image {0} does not have EXIF IFD data.'.format(path))
    
    return exif_ifd[0x9003]  # Retrieves the DateTimeOriginal property


def extract_date(exif_str: str):
    date = exif_str.split(" ")[0].split(":")
    return (date[0], date[1], date[2]) # order: year, month, day


def date_to_string(year, month, day, index, name_format: str):
    return name_format \
        .replace("y", year) \
        .replace("m", month) \
        .replace("d", day) \
        .replace("i", str(index))


def compare_first_element(e):
    return e[0]


def get_sorted_list(dir_path: str):
    file_dict = []
    for file in os.listdir(dir_path):
        try:
            if file.lower().endswith("jpeg") or file.lower().endswith("jpg"):
                file_path = os.path.join(dir_path, file)
                file_datetime = str(get_date_taken(file_path))
                file_dict.append((file_datetime, file_path))
        except:
            print(f"Could not extract exif data from {file_path}.")
    file_dict.sort(key=compare_first_element)
    return file_dict


def get_next_index(date, date_dict):
    if date not in date_dict.keys():
        date_dict[date] = 0
    else:
        date_dict[date] += 1
    return date_dict[date]


if __name__ == "__main__":
    (origin_dir, target_dir, name_format) = get_cmd_args()


    print(f"{origin_dir}, {target_dir}, {name_format}")

    if not os.path.isdir(origin_dir):
        print("Origin is not a directory.")
        exit(0)

    os.makedirs(target_dir, exist_ok=True)
    
    if not os.path.isdir(target_dir):
        print("Could not create target dir")
        exit(0)

    date_dict = {}
    print("Sorting images...")
    image_list = get_sorted_list(origin_dir)
    
    print(f"Images to copy: {len(image_list)}")
    print("Creating copies...")
    written = 0
    length = len(image_list)
    for image_entry in image_list:
        date = extract_date(image_entry[0])
        index = get_next_index(date, date_dict)
        file_name = date_to_string(date[0], date[1], date[2], index, name_format)
        file_path = os.path.join(target_dir, file_name)

        image_path = image_entry[1]
        image = Image.open(image_path)
        image.save(f"{file_path}.jpeg", "JPEG", exif=image.info["exif"])

        print(f"Progress: {math.ceil(written / length * 100)}%\r", end="")
        written += 1
    print()
