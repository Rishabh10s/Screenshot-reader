# Screenshot Reader
A python script to detect text from screenshots using OCR tool tesseract.
The script will generate html files in 'reports' directory. The html files will contain the image, image path and the text. 
User can use text search commands like grep to search text from those html files.

## Installation

1. Download and install tessaract for windows from here. During installation, copy the tesseract installation directory path. We will need to set it later.

       https://github.com/UB-Mannheim/tesseract/wiki

2. Setup python environment.

        pip install -r requirements.txt

3. Edit the script to set the path of screenshots directory and tessaract.

       a) Change SCREENSHOTS_PATH to your screenshot directory.
       b) Change TESSERACT_EXE to the tesseract executable which can be found in the installation directory of tesseract.


## Usage

```bash
python screenshot_reader.py
```
