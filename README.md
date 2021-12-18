# Installation and Setup Instruction

First, make sure you are in the right directory:
```
cd olympic_api
```
## File Structure

```
olympics_api

┌── server.py
├── venv
├── README.md
└── ln2sql
	├── docs
	├── components
	├── icons
	├── theme
	├── utils
	└── ln2sql
		├── ln2sql.py
		├── main.py
		├── parser.py
		├── database.py
		└── ...
```
## Setup

To setup, we recommend to use the virtual environment we provide with all the dependencies pre-installed. 

- Run virtual environment
```
. venv/bin/activate
```

If you cannot make use of the virtual environment due to some reason (e.g. Windows user could find themselves having a bad time setting up for venv), alternatively you can install the required libraries, including but not limited to flask and sqlalchemy. Follow the error prompt should be enough, but feel free to use pdb should you find it necessary.


- Install Flask 

```
pip install Flask
```
- Install SQLAlchemy

```
pip install SQLAlchemy
```

Next, activate the environment variables using the provided .env file.

- Setup Environment variable
```
source .env
```
Now you could launch the server.

- Run Server
```
python server.py
```
