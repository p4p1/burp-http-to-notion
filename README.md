burp-http-to-notion
====
*Upload http data to notion automatically*


![burp-http-to-notion](https://raw.githubusercontent.com/p4p1/burp-http-to-notion/main/assets/logo.png)

A BurpSuite extension to upload the 200 http requests to a notion database allowing
a better organization in which endpoints need to be tested. This tool was mainly
designed in helping for reconnaissance during Bug Bounty to assist in uploading to
notion a rough sketch of a website through a simple template organising main sub
URI's of a website in different cards with then each endpoints in a inline list.

## Screenshots:

#### The extension interface inside of BurpSuite
![extension-interface](https://raw.githubusercontent.com/p4p1/burp-http-to-notion/main/assets/extention_scot.png)

#### The root page created by notion inside of notion
![root-page](https://raw.githubusercontent.com/p4p1/burp-http-to-notion/main/assets/sitemap_scrot.png)

#### The root page created by notion inside of notion (with agile view)
![root-page](https://raw.githubusercontent.com/p4p1/burp-http-to-notion/main/assets/canban_scrot.png)

#### Individual page with requests
![individual-page](https://raw.githubusercontent.com/p4p1/burp-http-to-notion/main/assets/idividual_card.png)

## Installation

### Private (Internal)
Navigate to [https://www.notion.so/my-integrations](https://www.notion.so/my-integrations)
and create a new integration for the Burp Extension. After creating the extension
you will have access to a *Internal Integration Secret*. You then need to share
with your integration the different pages you want the Burp Extension to access.
To do so navigate to one of your notion pages and select the three dots on the top
right:

_TO NOTE THAT IF YOU DO NOT CONNECT YOUR INTEGRATION THE BURP SUITE EXTENSION
WILL NOT WORK, AND YOU NEED TO SPECIFICALLY SHARE A PAGE. IT WILL NOT WORK IF YOU
SHARE A DATABASE._

![three-dot-image](https://raw.githubusercontent.com/p4p1/burp-http-to-notion/main/assets/how_to.png)

After sharing paste your internal secret token inside of the burp extension and
click the "Save Token" button. In the panel under the text form your page should
appear. You can then start running a crawl or manually crawling the website. When
done you can click on "Export To Notion" to then upload everything.

_TO NOT NOTION DOES RATE LIMIT THE REQUESTS SO UPLOADING ALL OF THE LINKS MIGHT TAKE
SOME TIME AND CURRENTLY BURP WILL FREEZE WHILE IT IS DOING ALL OF THE REQUESTS_


## Todo
 - [x] Save token to disk
 - [ ] Public login method
 - [ ] Add parallel processing to not block UI during upload
