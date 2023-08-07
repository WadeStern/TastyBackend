import requests
import json
import mysql.connector
from urllib.request import urlopen
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import xml.etree.ElementTree as ET
import unittest
import xmlrunner

# Parse the XML configuration file
tree = ET.parse('staging_test_config.xml')
root = tree.getroot()

# Retrieve the values from the XML
frontendurl = root.find('frontendurl').text
backendurl = root.find('backendurl').text
dbHost = root.find('dbHost').text
dbPort = root.find('dbPort').text
dbName = root.find('dbName').text
dbUser = root.find('dbUser').text
dbPassword = root.find('dbPassword').text

#Frontend Check
class FrontendCheckTestCase(unittest.TestCase):
    def test_frontend(self):
        try:
            response = requests.get(frontendurl)
            self.assertEqual(response.status_code, 200, "Frontend returned an error.")
        except requests.exceptions.RequestException as e:
            self.fail("An error occurred for the Frontend: " + str(e))

class BackendCheckTestCase(unittest.TestCase):
    def test_backend(self):
        try:
            response = requests.get(backendurl + '/python')
            self.assertEqual(response.status_code, 200, "Backend returned an error.")
        except requests.exceptions.RequestException as e:
            self.fail("An error occurred for the Backend: " + str(e))

class DBCheckTestCase(unittest.TestCase):
    def test_db(self):
        try:
            conn = mysql.connector.connect(
                host=dbHost,
                port=dbPort,
                database=dbName,
                user=dbUser,
                password=dbPassword
            )
            self.assertTrue(conn.is_connected(), "Database is not running.")
            conn.close()
        except mysql.connector.Error as e:
            self.fail("An error occurred while connecting to the database: " + str(e))

class FrontendBackendCheckTestCase(unittest.TestCase):
    def setUp(self):
        self.driver = webdriver.Chrome()

    def tearDown(self):
        self.driver.quit()

    def test_frontend_backend(self):
        try:
            self.driver.get(frontendurl + '/pythontest')
            response_text = self.driver.page_source
            self.assertEqual(self.driver.execute_script('return document.readyState'), 'complete', "Frontend-Backend connection error.")
            self.assertIn("Hello", response_text, "Server returned an error or 'Hello world' was not returned.")
        except Exception as e:
            self.fail("An error occurred for the Frontend-Backend connection: " + str(e))

class BackendDBCheckTestCase(unittest.TestCase):
    def test_backend_db(self):
        try:
            response = requests.get(backendurl+'/recipes/num/1')
            self.assertEqual(response.status_code, 200, "Backend-DB returned an error.")
        except requests.exceptions.RequestException as e:
            self.fail("An error occurred for the Backend-DB connection: " + str(e))

if __name__ == '__main__':
    test_cases = [
        FrontendCheckTestCase,
        BackendCheckTestCase,
        DBCheckTestCase,
        FrontendBackendCheckTestCase,
        BackendDBCheckTestCase
    ]

    # Create a test suite
    test_suite = unittest.TestSuite()
    for test_case in test_cases:
        tests = unittest.TestLoader().loadTestsFromTestCase(test_case)
        test_suite.addTests(tests)

    # Run the test suite with the XMLTestRunner to generate JUnit XML reports
    runner = xmlrunner.XMLTestRunner(output='test-reports')
    runner.run(test_suite)