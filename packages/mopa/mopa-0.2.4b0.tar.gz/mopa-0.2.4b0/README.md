# mopa
Library for interactive multi-objective power amplifier design

# I. Installation
1. Download [Python](https://www.python.org/downloads/) and ensure you can run it from your terminal by running `$ python --version` 
2. Install the test verson of mopa using `$ pip install mopa`
3. To check that installation is successful `$ pip show mopa`

# II. Dashboard via Heroku
Mopa's dashboard is currently running on a free Heroku instance. The link to the website is [mopa-dashboard.herokuapp.com](https://mopa-dashboard.herokuapp.com/).
* If the website has not be accessed in a while, it automatically times out and will take a few minutes to reload.
* The website is being run with very little computing power, so analyses may take some time. 

# III. Dashboard on Local Machine
If you want to use your local computer's computing power, you can run the dashboard via command line:
1. Run Python on the command line by running `$ python`
2. Import mopa `>>> import mopa`
3. Create a dashboard `>>> app = mopa.app.create_dashboard()`
4. Run the dashboard `>>> app.run_server()`
