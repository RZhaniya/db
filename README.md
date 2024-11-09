### Prerequisites

Before getting started, ensure that the following are installed on your system:

- Python (version 3.7 or higher)
- pip (Python package manager)
- MongoDB (version 4.0 or higher)
- Git

### Step 1: Clone the Repository

Clone the project from GitHub using the command below:

```bash
https://github.com/RZhaniya/db.git
```

After cloning, navigate into the project directory:

```bash
cd db-master
```

### Step 2: Set Up a Virtual Environment

It is recommended to create a virtual environment to manage dependencies in isolation. Run the following commands:

```bash
python -m venv venv
.\venv\Scripts\activate
```

### Step 3: Install Required Packages

Install the necessary packages using the `requirements.txt` file:

```bash
pip install -r requirement.txt
```

This will install Django, Djongo (for MongoDB integration), and any other dependencies listed.

### Step 4: Configure MongoDB

Ensure that MongoDB is running on your system. You can start it with:

```bash
mongod
```

Next, open the Django project’s settings file (typically `settings.py`) and configure the MongoDB database settings if not already done. The configuration should look like this:

```python
DATABASES = {
    'default': {
        'ENGINE': 'djongo',
        'NAME': '<database_name>',
        'HOST': 'localhost',
        'PORT': 27017,
    }
}
```

Replace `<database_name>` with the name of the MongoDB database you wish to use.

### Step 5: Apply Migrations

Since MongoDB is used with Djongo, Django migrations may be handled differently depending on your project. To apply any pending migrations, run:

```bash
python manage.py migrate
```

### Step 6: Start the Django Development Server

To start the Django development server, use:

```bash
python manage.py runserver
```

The server will be accessible at http://127.0.0.1:8000/. You can now open the project in a web browser by visiting that address.
