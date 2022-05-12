import cv2
import pytesseract
import os
import jinja2
import re
import json

# Change the screenshot path
SCREENSHOTS_PATH = r'C:\Users\LENOVO\Pictures\Screenshots'

CURRENT_DIR = os.path.dirname(os.path.abspath(__name__))
TEMPLATE_FILE_NAME = 'screenshot_template.html'
RESULTS_PATH = os.path.join(CURRENT_DIR, 'results')
META_FILE = os.path.join(CURRENT_DIR, 'meta.json')

try:
    pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
except:
    exit("Failed to load pytesseract library. Please ensure that you have install tesseract on your system.")

def init_dirs():
    """Initialize directory to store screenshot results."""
    try:
        if not os.path.isdir(RESULTS_PATH):
            os.mkdir(RESULTS_PATH)
    except:
        exit("Failed to initialize result dir. Please check the RESULTS_PATH is set correctly.")

def get_meta_data() -> dict:
    """Get json meta data from meta file"""
    data = {"images": []}
    if not os.path.isfile(META_FILE):
        return data
    try:
        with open(META_FILE, 'r') as f:
            data = json.load(f)
    except:
        print("Failed to load meta data json.")
    return data

# TODO: update metadata properly.
def dump_meta_data(data={}) -> None:
    """Dump the json data of screenshots and html files into meta file."""
    data['last_mod_time'] = os.path.getmtime(CURRENT_DIR)
    try:
        with open(META_FILE, 'w') as f:
            json.dump(data, f)
    except Exception as ex:
        print("Failed to dump meta data. Error: {}".format(ex))

def generate_html(img_file, text):
    """
    Write the image text into an html template.
    @param: img_file: File path of the image.
    @param: text: Text read form the image.

    @return: Returns html file path.
    """
    # Jinja template to create html files
    template = jinja2.Environment(
        loader=jinja2.FileSystemLoader(CURRENT_DIR)
    ).get_template(TEMPLATE_FILE_NAME)

    # remove new lines, tabs, extra spaces.
    text_out = re.sub('[ ]{2,}', ' ',re.sub('(\n|\t)', ' ', text))
    file_name = os.path.basename(img_file) + '.html'
    html_tmp_file = os.path.join(RESULTS_PATH, file_name)
    tokens = {}
    tokens['img_file'] = re.sub(' ','%20',img_file)
    tokens['text'] =  text_out
    with open(html_tmp_file, 'w') as f:
        f.write("{}".format(template.render(tokens)))
        f.flush()
    return html_tmp_file

def get_img_list(img_list, meta_data) -> list:
    """
    Returns list of image file paths, skip those which have same mod_time
    """
    final_list = []
    if not meta_data:
        return img_list
    for img in img_list:
        img_name = img.split('/')[-1]
        skip = False
        for image in meta_data.get('images'):
            skip = False
            if img_name == image['name']:
                if os.path.getmtime(img) == image.get('mod_time'):
                    skip = True
                    break
        if not skip and img not in final_list:
            final_list.append(img)
    return final_list


def read_images():
    """
    The process of reading starts here. The directory is scanned for searching image files.
    Once we get the list of images, the list is compared with a meta file containing history of previous runs.
    If any is found modified, a new html file will be generated which will have the text.
    """
    # Get list of images.
    img_list = [os.path.join(SCREENSHOTS_PATH, x) for x in os.listdir(SCREENSHOTS_PATH) if x.endswith('.png') or x.endswith('.jpg')]
    # Get history of images already converted to html.
    meta_data = get_meta_data()
    # Get final list of new images. 
    final_list = get_img_list(img_list, meta_data)
    if final_list:
        print("Changes Detected:")
        print(final_list)
    # Meta list for storing the metadata of new images.
    img_meta_list = []
    for img_file in final_list:
        img_name = img_file.split('/')[-1]
        img = cv2.imread(img_file, 0)
        result = pytesseract.image_to_string(img)
        out_html_file = generate_html(img_file, result)
        img_meta = {"name": img_name,
                    "file_path": img_file,
                    "mod_time": os.path.getmtime(img_file),
                    "html": out_html_file}
        img_meta_list.append(img_meta)
    if not meta_data.get('images'):
        meta_data['images'] = []

    meta_data['images'].extend(img_meta_list)
    dump_meta_data(meta_data)

init_dirs()
read_images()

### For scheduling it to run at some interval. Uncomment the below code.
# def schedule_reader():
#   while True:
#     read_images()
#     time.sleep(5)
# schedule_reader()
###