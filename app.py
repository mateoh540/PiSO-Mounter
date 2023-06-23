from flask import Flask, session, request, render_template, make_response, url_for, redirect, flash
import os
from flask_restful import Resource, Api
from simplepam import authenticate
import cgi
import shutil
from flask_login import LoginManager
import subprocess
import pyudev

app = Flask(__name__)
api = Api(app)
form = cgi.FieldStorage

# Acess Control
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = '/login'
app.config['SECRET_KEY'] = 'wqkjfhkwqjehf827f2gfkiu'
app.config['MESSAGE_FLASHING_OPTIONS'] = {'duration': 5}

@login_manager.user_loader
def load_user(user_id):
    return User.get(user_id)

# ---FUNCTIONS---

# Function converts bytes to useful units (MB, GB, etc.)
def convert_bytes(num):
    for x in ['bytes', 'KB', 'MB', 'GB', 'TB']:
        if num < 1024.0:
            return "%3.1f %s" % (num, x)
        num /= 1024.0

# ---API'S---

# API to list the Files of the System Storage Directory
class files(Resource):
    def get(self):

        # If username is not in session, redirect to the login page

        if 'username' in session:

            # Image Library Listing

            imagedirectory = '/home/flask-app/files'  # Replace with the desired directory path
            isofiles = os.listdir(imagedirectory) 
            isofiles_with_size= [ (file_name, convert_bytes(os.stat(os.path.join(imagedirectory, file_name)).st_size))
                        for file_name in isofiles  ]
            
            # IP address

            ip_address = subprocess.call('hostname -I', shell=True)
            
            #ip_address = '10.12.8.190'

            # Mounted File(s)
            
            mounteddirectory = '/mnt/usb_share'
            mountedfiles = os.listdir(mounteddirectory)

            return make_response(render_template('files.html', isofiles=isofiles_with_size, mountedfiles=mountedfiles, ipaddress=ip_address))
        return redirect(url_for('login'))
    

# API to Log in the Current User
class login(Resource):
    def post(self):
        username = request.form['username']
        password = request.form['password']
        if authenticate(str(username), str(password)):
            session['username'] = request.form['username']
            return redirect(url_for('files'))
        else:
            flash('Incorrect Login')
            return redirect(url_for('login'))
    def get(self):
        return make_response(render_template('login.html'))


# API to Logout the Current User
class logout(Resource):
    def get(self):
        session.pop('username', None)
        return redirect(url_for('login'))


# API to Mount a Selected File
class mount(Resource):
    def post(self):
        if 'username' in session:    

            path = '/mnt/usb_share'


            # Converting the form data into the name of the file

            data = request.form
            filename = next(iter(data))
            file = os.path.join('/home/flask-app/files', filename)

            # default name is filename so this means that no file was selected, return to homepage

            if filename == 'filename':
                flash("No file selected!", 'error')
                return redirect(url_for('files'))
            

            # eject the usb drive

            # subprocess.run('sudo modrpobe -r g_mass_storage', shell=True)
            
            # Attach the conatiner file to a loop device, save the return code

            #subprocess.run('sudo losetup --show -fP /home/asteralabs/usb.img', shell=True)

            #assignedloop = '/dev/loop0'

            # Mount the Partition onto the Filesystem

            #subprocess.run("sudo mount -v " + assignedloop + " /mnt/usb_share", shell=True)

            # remove current files in /mnt/usb_share

            subprocess.run('sudo rm -rf /mnt/usb_share/*', shell=True)

            # copy file to /mnt/usb_share

            subprocess.run("sudo cp -v " + file + " /mnt/usb_share", shell=True)

            # Unmount the file system

            #subprocess.run('sudo umount /mnt/usb_share', shell=True)

            # Detach the container file from the loop device

            #subprocess.run('sudo losetup -D', shell=True)

            #  Recconect the USB drive

                #subprocess.run('sudo modprobe g_mass_storage file=/home/asteralabs/usb.img removable=1', shell=True)



            

            # Once mounting is done, flash that the file has mounted
            flash("'" + filename + "' has succesfully mounted!", 'info')
            return redirect(url_for('files'))
        return redirect(url_for('login'))

# API to Unmount the Selected File
class unmount(Resource):
    def get(self):
        if 'username' in session:  

            # No file present


            
            # Remove all contents of the filesystem

            filename= 'file'
            subprocess.run('sudo rm -rf /mnt/usb_share/*', shell=True)
            flash("'" + filename + "' has succesfully unmounted!", 'info')
            return redirect(url_for('files'))
        return redirect(url_for('login'))



# API to Delete the Selected File    
class delete(Resource):
    def post(self):
        if 'username' in session:
            # Converting the form data into the name of the file
            data = request.form
            filename = next(iter(data))
            if filename == 'filename':
                flash("No file selected!", 'error')
                return redirect(url_for('files'))
            os.remove(os.path.join('/home/flask-app/files', filename))
            flash("'" + filename + "' has been deleted." , 'info')
            return redirect(url_for('files'))
        return redirect(url_for('login'))

# API to Connect the Pi USB to the System
class connect(Resource):
    def get(self):
        if 'username' in session:   
            #subprocess.run('sudo modprobe g_mass_storage file=/home/asteralabs/usb.img removable=1', shell=True)
            flash("Succesfully connected!", 'info')
            return redirect(url_for('files'))
        return redirect(url_for('login'))
    
# API to Connect the Pi USB to the System
class eject(Resource):
    def get(self):
        if 'username' in session:   
            # subprocess.run('sudo modrpobe -r g_mass_storage', shell=True)
            flash("Succesfully ejected!", 'info')
            return redirect(url_for('files'))
        return redirect(url_for('login'))
    

# API to Upload Files to the System Storage Directory
class upload(Resource): 
    directory = '/home/flask-app/files' # Define the Upload Directory
    app.config['directory'] = directory
    def post(self):
        if 'username' in session:  
            file = request.files['file']
            if file:
                filename = file.filename
                file.save(os.path.join(self.directory, filename))
                return redirect(url_for('files'))
        return redirect(url_for('login'))
    def get(self):
        if 'username' in session:  
            return make_response(render_template('upload.html'))
        return redirect(url_for('login'))
    
# API to display the connected system
class connected(Resource):
    def post(self):
        

        return

# ---RESOURCE URL'S ---

api.add_resource(files, '/')
api.add_resource(mount, '/mount') # Mounting: __(filename)__ Progress bar, checkmark when uploaded, received?, cancel?, return to file list
api.add_resource(connect, '/connect')
api.add_resource(upload, '/upload')
api.add_resource(login, '/login')
api.add_resource(logout, '/logout')
api.add_resource(delete, '/delete')
api.add_resource(unmount, '/unmount')
api.add_resource(eject, '/eject')

if __name__ == '__main__':
    app.config['TEMPLATES_AUTO_RELOAD'] = True
    app.run(debug=True)
