<!-- # food-website-main -->


<b> Installation - </b>

pip install -r requirements.txt

Before starting the website please delete the old testdb.db file.
<b>python main.py</b>
this should create a fresh new db also executing the main script but if not created please execute db.py this will create the database with necessary tables

also please change the the following in the main.py

app.run(host='192.168.10.4', port=80, debug=True)
to 
app.run()
or 
change the host to the ipv4 of the device 
you can do it by running command prompt and ipconfig

IPv4 Address. . . . . . . . . . . : 192.168.10.5

app.run()
 
<b>About</b>

Simple flask website to display food recipies. 


<b>API - https://themealdb.com/</b>

<b>LIVE STATIC design (Only HTML, CSS, JS) - https://dbfood.netlify.app/</b>
