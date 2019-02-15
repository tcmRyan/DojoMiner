# Dojo Miner
[![Build Status](https://travis-ci.org/joemccann/dillinger.svg?branch=master)](https://travis-ci.org/joemccann/dillinger)

Dojo Miner is a tool intended for Code Ninjas Franchisees to address some of the short comings in the existing tooling.  It is intended to download data from the dojo api.

  - Extensible DojoRequest class to make requests at any API
  - Page Object for grabbing data from the Dojo Grading page
  - Application to make downloading the spreadsheet easy

# New Features!

  - Dojo grades downloaded to spreadsheet
  - Ninja belt levels downloaded to spreadsheets


> The DojoMiner makes it easy to get access 
> to the dojo and GDP data that you need to make
> decisions. Python is an easy script language 
> that lets you manipulate the data to gain
> the insights you need.

### Tech

Dillinger uses a number of open source projects to work properly:

* [PyQt5] - GUI for python applications
* [Requests] - Python Http requests for humans
* [PyInstaller] - Easily package python applications
* [BrowserCookie3] - Use browser cookies in python requests


### Installation

Running the application is easy if you are on Windows.  Just double click the exe file to run the app.
If you are on another operating system you will need to build the application first.  Python3 is required for this 
application

On Linux or Mac
```sh
$ pip install virtualenv
$ git clone https://github.com/tcmRyan/DojoMiner.git
$ cd DojoMiner
$ virtualenv venv
$ sh venv/bin/activate
$ pip install -r requirements.txt
$ pyinstaller dojo.py
$ cp gui.ui dist/dojo
$ cp config.yaml dist/dojo
```
You should not have an executable that works in `dist/dojo/` named `dojo`
You have also setup the environment for developement and can run the app with by running 
```sh
$ python dojo.py
```

### Updating the GUI

In Windows run 
```sh
$ venv/Scripts/designer.exe
```
In Linux/OSx:
```sh
$ venv/bin/designer
```

This will run the [PyQt5 designer tool](https://www.tutorialspoint.com/pyqt/pyqt_using_qt_designer.html) This tool will generate the XML that gets used in the app.  Open `gui.ui` to modify the UI.  The XML is loaded in the MainWindow class, which is why that class references widgets that have not been declared in the class.

### Extending the DojoRequests

The DojoMiner works by making HTTP requests to the GDP and Dojo APIs by using the cookies in you browser.  The DojoRequests library does this automatically so that you do not have to worry about it.

GDP - The Game Development Platform is a server-side rendered application.  This means that the webpage is fully rendered on the server before it gets sent you your browser.  This means that in order to get the data you will need to parse the HTML of the dojo.  See the `GradingPage` class as an example.  

To begin exporing how to get the selectors:
* Right click on the html element that you want to interact with
* When the devtools open in your browser, right click the element and select Copy -> Copy Selector
* More documentation can be found here [requests-html](https://github.com/kennethreitz/requests-html)

Dojo/Franchizar - The Dojo makes AJAX requests to the server to populate the data.  This means that you can look at the XHR requests in your browser networking tab. Customize and Control Google Chrome -> More Tools -> Developer Tools -> Networking tab.

Look at the repsonse tab for each request to see if it has the data you want. You can copy and paste the json into a  tool like [JSonViewer](http://jsonviewer.stack.hu/) to see the structure of the data better. See `fetch_students` in `lib/belt_scripts.py` as an example.
