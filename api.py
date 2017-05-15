import os
import argparse
from flask import Flask, request, jsonify
import random
import string
import json

from datetime import datetime

TEMP_FILE_FOLDER = 'temp/temp-files'
TEMP_INFO_FOLDER = 'temp/temp-infos'
FILE_FOLDER = 'files'

if not os.path.exists(TEMP_FILE_FOLDER):
    os.makedirs(TEMP_FILE_FOLDER)
if not os.path.exists(TEMP_INFO_FOLDER):
    os.makedirs(TEMP_INFO_FOLDER)

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 1024 * 1024 * 100 #100MB
app.debug = True

def random_generator(size=64, chars=string.ascii_lowercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))

def get_file_ext_name(fpath):
    filename, file_extension = os.path.splitext(fpath)
    return file_extension

@app.route('/file/upload', methods=['POST'])
def upload_file():

    if 'file' not in request.files:         
        return jsonify({'result': False, 'message': 'no file'})
              
    upload_file = request.files['file']
    if upload_file.filename == '':            
        return jsonify({'result': False, 'message': 'no file name'})

    # file info
    upload_filename = upload_file.filename
    upload_file_ext_name = get_file_ext_name(upload_filename)

    # form info
    tags = request.form.get('tags', '').split(",")    
    unzip_file = bool(request.form.get('unzip_file', 'true'))
    unzip_pwd = request.form.get('unzip_pwd', '')
    
    # save as file random name to avoid duplicate file name
    random_filename = random_generator(size=64)
    temp_path = os.path.join(TEMP_FILE_FOLDER, random_filename)
    
    upload_file.save(temp_path)
        
    # save file info
    with open(os.path.join(TEMP_INFO_FOLDER, random_filename), 'w') as infofile:
        fileinfo = {'upload_filename': upload_filename
                    , 'tags': tags
                    , 'unzip_pwd': unzip_pwd
                    , 'unzip_file': unzip_file
                    , 'file_ext': upload_file_ext_name
                    , 'upload_on': str(datetime.utcnow())}
        infofile.write(json.dumps(fileinfo))
          
    return jsonify({'result': True})

if __name__ == "__main__":
    parser = argparse.ArgumentParser()    
    parser.add_argument("-p", "--port", help="port", type=int, required=False, default=5000)
    parser.add_argument("-s", "--server", help="host", type=str, required=False, default='0.0.0.0')    
    
    args = parser.parse_args()       
    
    app.run(host=args.server, port=args.port)                                