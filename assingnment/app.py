from flask import Flask, render_template, request, flash
import boto3
from botocore.exceptions import ClientError
from decouple import config

app = Flask(__name__)
app.config['SECRET_KEY'] = config('aws_secret_access_key')
app.config['ACCESS_KEY'] = config('aws_access_key')
s3 = boto3.client("s3")
s3_resource = boto3.resource('s3')




@app.route('/')
def main_page():
    return render_template('index.html')


##########################     LIST BUCKETS    ################################


@app.route('/list')
def list_buckets():
    listbuck = []
    for buck in s3_resource.buckets.all():
        listbuck.append(buck.name)
    if len(listbuck) == 0:
        flash("No Buckets Available ! !")
    return render_template('list.html', listOfBuckets=listbuck)


########################   CREATE OR DELETE BUCKET    ##########################

@app.route('/bucket')
def bucket_form():
    return render_template('bucket.html')


############################   CREATE BUCKET     ####################################


@app.route('/create_bucket', methods=['POST'])
def create_bucket():
    bucket_name = request.form.get('bucket_name')
    try:
        s3.create_bucket(Bucket=bucket_name)
        flash(f'Bucket {bucket_name} is Created')
    except ClientError as e:
        flash("Bucket already exists, Try another name!!")
    return render_template('bucket.html')


###############################    DELETE BUCKET     #################################



@app.route('/delete_bucket', methods=['POST'])
def delete_bucket():
    bucket_name = request.form.get('bucket_name')
    try:
        s3.delete_bucket(Bucket=bucket_name)
        flash(f'Bucket {bucket_name} is Deleted')
    except ClientError as e:
        flash(e)
    return render_template('bucket.html')

#########################   CREATE OR DELETE FOLDER     ####################################


@app.route('/folder')
def folder_form():
    return render_template('folder.html')


##########################    CREATE FOLDER   #########################################

@app.route('/create_folder', methods=['POST'])
def create_folder():
    bucket_name = request.form.get('bucket_name')
    folder_name = request.form.get('folder_name')
    try:
        bucket = s3_resource.Bucket(bucket_name)
        bucket.put_object(Key=folder_name)
        for obj in bucket.objects.all():
            if obj.key == folder_name:
                flash(f'Folder was {folder_name} created succcessfuly!!!!')
    except ClientError as e:
        flash(e)
    return render_template('folder.html')

##############################       DELETE FOLDER       #############################################

@app.route('/delete_folder', methods=['POST'])
def delete_folder():
    bucket_name = request.form.get('bucket_name')
    folder_name = request.form.get('folder_name')
    try:
        objects = s3.list_objects(Bucket=bucket_name, Prefix=folder_name)
        files_list = objects["Contents"]
        files_to_delete = []
        for f in files_list:
            files_to_delete.append({"Key": f["Key"]})
        s3.delete_objects(Bucket=bucket_name, Delete={
                          "Objects": files_to_delete})
        flash('Folder Deleted!!!')
    except ClientError:
        flash('No such bucket!!')
    except KeyError:
        flash('No such folder!!')
    return render_template('folder.html')



#################################    UPLOAD FOLDER    #################################


@app.route('/files')
def upload_file():
    return render_template('files.html')


@app.route('/upload', methods=['POST'])
def upload():
    bucket_name = request.form.get('bucket')
    file = request.files['file']
    print(file)
    try:
        file_name = file.filename
        s3.upload_fileobj(file, bucket_name, file_name)
        flash("Uploaded!!!")
    except ClientError as e:
        flash("No bucket found!!!")
    return render_template('files.html')


#####################################    LIST FILE  ##########################################

@app.route('/list_file')
def list_file():
    return render_template('fileList.html')


@app.route('/file_list', methods=['POST'])
def file_list():
    bucket_name = request.form.get('bucket_name')
    files_list=[]
    try:
        response = s3.list_objects_v2(Bucket=bucket_name)
    except ClientError as e:
        flash('No bucket Found')

    if response['KeyCount'] == 0:
        flash('No files Present')
        return render_template('listFile.html')
    else:
        for files in response['Contents']:
            files_list.append(files['Key'])
    return render_template('listFile.html',listOfFiles=files_list)


###############################     DELETE FILE     ###########################################

@app.route('/delete_file')
def delete_file():
    return render_template('delete.html')


@app.route('/delete', methods=['POST'])
def delete():
    bucket_name = request.form.get('bucket_name')
    file_name = request.form.get('file_name')
    try:
        s3.delete_object(Bucket=bucket_name, Key=file_name)
        flash(f'File {file_name} is  Deleted')
    except ClientError as e:
        flash('No such Bucket!!!')
    return render_template('delete.html')


#############################    MOVE OR COPY FILE     ########################################


@app.route('/moveorcopy')
def move_copy():
    return render_template('moveForm.html')


#################################      MOVE FILE      #############################################


@app.route('/move', methods=['POST'])
def move():
    source_bucket_name = request.form.get('source_bucket_name')
    file_name = request.form.get('source_file_name')
    dest_bucket_name = request.form.get('dest_bucket_name')
    try :
        copy_s = {
            'Bucket' : source_bucket_name, 'Key' : file_name
        }
        s3_resource.meta.client.copy(copy_s,dest_bucket_name,file_name)
        s3.delete_object(Bucket=source_bucket_name, Key=file_name)
        flash(f'Moved {file_name} from {source_bucket_name} to {dest_bucket_name} !!!!! ')
    except ClientError as e:
        flash('Wrong Details')
    return render_template('moveForm.html')



###########################     COPY FILE     ###########################################



@app.route('/copy', methods=['POST'])
def copy_file():
    source_bucket_name = request.form.get('source_bucket_name')
    file_name = request.form.get('source_file_name')
    dest_bucket_name = request.form.get('dest_bucket_name')
    try :
        copy_s = {
            'Bucket' : source_bucket_name, 'Key' : file_name
        }
        s3_resource.meta.client.copy(copy_s,dest_bucket_name,file_name)
        flash(f'Copied {file_name} from {source_bucket_name} to {dest_bucket_name} !!!!! ')
    except ClientError as e:
        flash('Wrong Details')
    return render_template('moveForm.html')



if __name__ == "__main__":
    app.run(debug=True)
