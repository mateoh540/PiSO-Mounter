from flask import Flask, request, render_template, make_response
import os
from flask_restful import Resource, Api
import cgi
import subprocess


from flask_httpauth import HTTPTokenAuth
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import select
import random, string
import fileinput

app = Flask(__name__)
api = Api(app)
form = cgi.FieldStorage


app.config['SECRET_KEY'] = 'wqkjfhkwqjehf827f2gfkiu'
app.config['MESSAGE_FLASHING_OPTIONS'] = {'duration': 5}
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True


# -- USER DATABASE --

#  Database Initialization
db = SQLAlchemy(app)
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    bearer_token = db.Column(db.String(200), nullable=True)

# Reflect database to list and debug
with app.app_context():
    db.reflect()

# Token Verification
auth= HTTPTokenAuth(scheme='bearer')
@auth.verify_token
def verify_token(token):
    if db.one_or_404(db.select(User).filter_by(bearer_token=token)):
        user = db.session.execute(db.select(User).filter_by(bearer_token=token))
        for user_obj in user.scalars():
            username = f"{user_obj.username}"
        return username

# -- FUNCTIONS --

# Function converts bytes to useful units (MB, GB, etc.)
def convert_bytes(num):
    for x in ['bytes', 'KB', 'MB', 'GB', 'TB']:
        if num < 1024.0:
            return "%3.1f %s" % (num, x)
        num /= 1024.0


# -- ACCESS CONTROL --


# API to create a new user

class create_user(Resource): # curl -X POST -F 'username=' -F 'password=' http://127.0.0.1:5000/user/add
    def post(self):

        # Inputted Username and Password
        input_username=request.form['username']
        input_password=request.form['password']


        # Generating Bearer Token
        letters = string.ascii_lowercase
        generated_token = ''.join(random.choice(letters) for i in range(15))


        # Adding to Database
        user = User(
            username = str(input_username),
            password = str(input_password),
            bearer_token = generated_token,
        )
        db.session.add(user)
        db.session.commit()
        print(f"\n\n Your token is: {generated_token} \n\n")

# API to delete a user

class delete_user(Resource):
    @auth.login_required
    def post(self):

        User.query.delete()
        db.session.commit()

# API to regenerate a users token

class regenerate_token(Resource): # curl -X POST -H "Authorization: Bearer hgcrobsqzc" http://127.0.0.1:5000/user/regen
    @auth.login_required  
    def post(self):

        user = auth.current_user()

        # From the authorized bearer token, regnerate that users token

        print(user)

        input_username = user

        # Find the current username and password

        result = db.session.execute(db.select(User).filter_by(username=input_username))
        for user_obj in result.scalars():
            username=f"{user_obj.username}"
            password=f"{user_obj.password}"


        # Delete the current instance
        db.session.delete(db.one_or_404(db.select(User).filter_by(username=input_username)))
        db.session.commit()


        # Generate New Bearer Token
        letters = string.ascii_lowercase
        generated_token = ''.join(random.choice(letters) for i in range(15))

        # Add the new instance
        user = User(
            username = username,
            password = password,
            bearer_token = generated_token,
        )
        db.session.add(user)
        db.session.commit()

        # Print the new token to the user
        print(f"\n\n Your new token is: {generated_token} \n\n")

# API to list the user database

class get_user(Resource): # curl -X POST http://127.0.0.1:5000/user/get
    def post(self):
        result = db.session.execute(select(User))
        print(" \n \n User Database \n")
        for user_obj in result.scalars():
            print("-------------------------------------------------------------------")
            print(f"| {user_obj.id} |      {user_obj.username}       |       {user_obj.password}        | {user_obj.bearer_token} |")
        print("-------------------------------------------------------------------")
        print("\n\n") 
        

# -- FUNCTIONALITY --
        

# API to Mount a Selected File
class select_image(Resource): # curl -X "POST" -F "image_name=memtest86" -H "Authorization: Bearer cuxkamlekgyyurd" http://127.0.0.1:5000/select_image
    @auth.login_required
    def post(self):

        # Identify the image to be selected from the user input

        input_image_name = request.form['image_name']

        output = subprocess.run(f'ls /home/asteralabs/pisomounter/images | grep {input_image_name}', stdout=subprocess.PIPE, text=True, shell=True, check=True)

        image_name=output.stdout

        print(f'\n \nThe following image will be mounted: {image_name} \n \n')

        script_file_path = '/home/asteralabs/pisomounter/scripts/boot.sh'


        # Modify the boot.sh file to boot from the selected image

        # Old and new lines
        old_line = "sudo modprobe"

        # Specify and format the new line 
        new_line = f"sudo modprobe g_mass_storage file=/home/asteralabs/pisomounter/images/{image_name} cdrom=1 stall=0"
        new_line = new_line.strip()  
        new_line = new_line.replace('\r', '').replace('\n', '')  

        # Replace the old line with the new line
        with fileinput.FileInput(script_file_path, inplace=True) as file:
            for line in file:
                if old_line in line:
                    print(new_line)
                else:
                    print(line, end='')

       
# API to Connect the Pi USB to the System
class connect(Resource): # curl --request "POST" --header "Authorization: Bearer test" http://127.0.0.1:5000/connect
    @auth.login_required
    def post(self):
            #subprocess.run('sudo modprobe g_mass_storage file=/home/asteralabs/usb.img removable=1', shell=True)
            print(f'\n \n Succesfully Connected \n \n')
            
    
# API to Connect the Pi USB to the System
class eject(Resource): # curl --request "POST" --header "Authorization: Bearer test" http://127.0.0.1:5000/eject
    @auth.login_required
    def post(self):
            # subprocess.run('sudo modrpobe -r g_mass_storage', shell=True)
            print(f"\n \nSuccesfully ejected! \n \n")
    

class dummy(Resource): # curl --request "POST" --header "Authorization: Bearer cuxkamlekgyyurd" http://127.0.0.1:5000/dummy
    @auth.login_required
    def post(self):
           
            print(f"\n\n\n\n")


# -- WEB INTERFACE -- 

# API to list the Files of the System Storage Directory
class files(Resource):
    def get(self):

        # Image Library Listing
        imagedirectory = '/home/asteralabs/pisomounter/images'  # Replace with the desired directory path
        isofiles = os.listdir(imagedirectory) 
        isofiles_with_size= [ (file_name, convert_bytes(os.stat(os.path.join(imagedirectory, file_name)).st_size))
            for file_name in isofiles  ]
            
        # IP address

        #ip_address = subprocess.check_output('hostname -I', shell=True)
        ip_address = subprocess.run('hostname -I', capture_output=True, text=True, shell=True).stdout.strip("\n")

        # Mounted File(s)
            
        mounteddirectory = 'mountedfile/'
        mountedfiles = os.listdir(mounteddirectory)

        return make_response(render_template('files.html', isofiles=isofiles_with_size, mountedfiles=mountedfiles, ipaddress=ip_address))
    


# ---RESOURCE URL'S ---

# FUNCTIONALLITY 
api.add_resource(select_image, '/select_image')
api.add_resource(connect, '/connect')
api.add_resource(eject, '/eject')
# DATABASE
api.add_resource(create_user, '/user/add')
api.add_resource(delete_user, '/user/delete')
api.add_resource(get_user, '/user/get')
api.add_resource(regenerate_token, '/user/regen')
api.add_resource(dummy, '/dummy')
# WEB INTERFACE
api.add_resource(files, '/')



if __name__ == '__main__':
    app.config['TEMPLATES_AUTO_RELOAD'] = True
    app.run(debug=True)
