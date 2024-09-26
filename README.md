
# Trippy - Travel Website

Trippy is a travel website built with Flask. This project includes user authentication, profile management, a wishlist feature, and destination pages. The site uses SQLite for the database, and various Flask extensions for functionality.

## Table of Contents

- [Features](#features)
- [Setup Instructions](#setup-instructions)
- [Running the Application](#running-the-application)
- [Contributing](#contributing)
- [License](#license)

## Features

- User registration and login
- Profile management and picture upload
- Wishlist functionality for destinations
- Display destinations from a JSON file
- Error handling and form validation

## Setup Instructions

Follow these steps to set up the project on your local machine:

### 1. Clone the Repository

First, clone the repository to your local machine:

```bash
git clone https://github.com/RaghavOG/Travel-FLask
cd trippy
```

### 2. Create a Virtual Environment

It's a good practice to use a virtual environment to manage project dependencies. Create a virtual environment using `venv`:

```bash
python -m venv venv
```

### 3. Activate the Virtual Environment

Activate the virtual environment:

- **Windows:**

  ```bash
  venv\Scripts\activate
  ```

- **macOS/Linux:**

  ```bash
  source venv/bin/activate
  ```

### 4. Install Dependencies

Install the required Python packages listed in `requirements.txt`:

```bash
pip install -r requirement.txt
```


### 5. Run the Application

Start the Flask application by running:

```bash
python app.py
```

The application will be available at `http://127.0.0.1:5000/`.

