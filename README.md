# Food Website

This is a simple Flask website that displays food recipes. It fetches data from [TheMealDB API](https://themealdb.com), and you can see a live static design of the website [here](https://dbfood.netlify.app).

## Installation

To run this project locally, follow these steps:

1. Install the required dependencies using pip:

pip install -r requirements.txt

2. Before starting the website, delete the old `testdb.db` file. You can do this manually or by executing the following command:

python main.py

This command should create a fresh new database. If the database is not created, execute `db.py` to create the database with the necessary tables.

3. Modify the following lines in `main.py` to control the host and port where your website will be running:

Change this line:

```python
app.run(host='192.168.10.2', port=80, debug=True)

to either:

app.run()

or change the host to the IPv4 address of your device. You can find your device's IPv4 address by running the command ipconfig in the command prompt:

IPv4 Address. . . . . . . . . . . : 192.168.10.5

Update the app.run() line accordingly.

Now, you are ready to run the website locally.

Usage
You can access the website by opening your web browser and navigating to the address where the website is hosted.

Contributing
If you'd like to contribute to this project, please open an issue or submit a pull request. We welcome your contributions and ideas!

License
This project is open-source and available under the MIT License.