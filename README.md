# Introduction 
A simple python project to publish an API enpoint that accepts a JSON payload containing data to be merged with an HTML document template which contains placeholder variables started and terminated with pipes (e.g. |vairable_name|) to be replaced with the data elements in the JSON payload.

It will return a Base64-encoded PDF to be stored in the requesting system (e.g. Salesforce).

# Getting Started

1.	Built on Python 3.12.8 interpreter
2.	Venv python pacakage dependencies can found in requirements.txt
3.  EntraID enterprise app: "PDF (DEV)"; Client ID & secret stored in Azure (ask IT Ops)
4.	API documentation is available in Swagger on the endpoint once published: https://{host}:{port}/docs
5.  There are 2 dockerfiles, one for the base linux image (Alpine + Python 3.12.8 + Weasyprint and dependencies), and a second which then deploys the python app onto the base image
6.  Full documentation available in the wiki: [PDF Wiki Page](https://dev.azure.com/ib-mortgages-dev-ops-uk/Project-Ignite/_wiki/wikis/Project-Ignite.wiki/887/Document-Factory)

