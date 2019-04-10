# Catalog Web App
An Udacity Full Stack Web Developer Nanodegree project developed by Tremaine Kirkman.

## About
This web application provides an interface to browse, update, and delete items from a catalog organized by category. Authentication is provided via the Google Sign-in API, and user CRUD access is limited to their own catalog items.

### Features
- User Registration via Google Sign-in API.
- CRUD (Create, Read, Update, Delete) functions using SQLAlchemy and Flask.
- REST API providing access to database items and categories, provided as JSON.

## Steps to run this project

### 1. Install Python 2.7
Download can be found [here](https://www.python.org/downloads/)

### 2. Install Virtual Box
VirtualBox is software that runs the Virtual Machine (VM) that will be used to run this program. Download [here](https://www.virtualbox.org/wiki/Downloads), and install the platform package. Note: you do not need the extension pack, SDK or to launch the program

### 3. Install Vagrant
Vagrant configures the VM and establishes a shared directory between the VM and your local filesystem. Download [here](https://www.vagrantup.com/downloads.html), then Clone or download the Vagrant VM configuration file from [here](https://github.com/udacity/fullstack-nanodegree-vm). Open the directory and navigate to the `vagrant/` sub-directory and then run

    vagrant up

to set up the VM. Note: this process should take a while. 

When finished run

    vagrant ssh

to log in to the virtual machine. For more information, see the Vagrant documentation [here](https://www.vagrantup.com/docs/).

### 4. Clone Repo
Type `cd /vagrant/` to navigate to the shared repository, and then download or clone this repo.

### 5. Install Flask
    sudo python3 -m pip install --upgrade flask
    
### 6. Setup The Database
To setup the database run:

     python3 database_setup.py 
    
Next, populate the database with starter values:

    python3 catalog_database.py

### 7. Run The Application
Run:`python3 app.py`, and then open `http://localhost:5000/` in a Web browser, and enjoy!

## Troubleshooting
In case the app doesn't run, double check a few things:
- You have run `python catalog_database.py` before running the application. This is an essential step.
- You have at least python 2.7 installed.
- The latest version of Flask is installed.

## API
This project implements a basic REST API that exposes several JSON endpoints to return category & item data from the database. Below is a list of all API endpoints included in the project.

### 1. All Items
This endpoint returns a list of all the item objects in the catalog database. Found at: 

    /api/catalog.json

### 2. Specific Item
Returns a specific item object from the database. Requires the correct catalog_id & item_id parameters

    /api/categories/<int:category_id>/item/<int:item_id>.json
    
### 3. All Categories
Returns a list of all category objects in the database

    /api/categories.json


---

## License
[MIT](https://choosealicense.com/licenses/mit/)
