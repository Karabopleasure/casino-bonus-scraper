# casino-bonus-scraper
A Python scraper that extracts casino bonus information and displays it on a webpage.

**Features**

1. Checks the source website's robots.txt before fetching the page.

2. Extracts welcome bonus, wagering requirement, minimum deposit, and source URL for three casinos.

3. Saves extracted records to docs/bonuses.json.

4. Displays the JSON data in a mobile-friendly webpage.

5. Uses GitHub Pages to publish the static website.

**Project structure**

casino-bonus-scraper/
├── scraper/
│   └── scraper.py
├── docs/
│   ├── index.html
│   ├── style.css
│   ├── app.js
│   └── bonuses.json
└── README.md

**Requirements**

1. Python 3
2. Internet connection
3. Python packages: requests and beautifulsoup4

**Setup**

Open a terminal in the project directory and install the dependencies: 
python -m pip install requests beautifulsoup4

**Run the scraper**

From the project root, run: 
python scraper/scraper.py

The script checks robots.txt, fetches the source page, extracts the available bonus data, and writes the results to:

docs/bonuses.json

Review the generated JSON and check that the extracted values are sensible.

**View the website locally**

From the project root, start a local web server:

python -m http.server 8000

Open this address in your browser:

http://localhost:8000/docs/

Keep the terminal open while testing. Press Ctrl+C to stop the server.

**Data source and responsible scraping**

Source: https://betproof.co.za/casino-bonuses-south-africa/sign-up-bonus-south-africa/

The scraper checks the source's robots.txt before requesting the page. It should be run responsibly, with appropriate request frequency. It must not bypass CAPTCHA challenges, login requirements, or access restrictions. Bonus terms can change, so extracted information should be verified against the source before being relied on.

**Publishing**
The website is published through GitHub Pages using the repository's main branch and /docs folder.

Live website: https://karabopleasure.github.io/casino-bonus-scraper/

