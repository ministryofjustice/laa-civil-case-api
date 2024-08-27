description = """
## Cases

* Create cases by posting to the /cases/ endpoint.
* Read all cases by sending a get request to the /cases/ endpoint.
* Read a given case by sending a get request to the /cases/{case_id} endpoint.
"""

config = {
    "title": "LAA Civil Case API",
    "description": description,
    "summary": "API used for holding information relating to civil legal aid cases.",
    "version": "0.0.1",
    "contact": {
        "name": "Civil Legal Advice",
        "email": "civil-legal-advice@digital.justice.gov.uk",
    },
    "license_info": {
        "name": "MIT Licence",
        "url": "https://github.com/ministryofjustice/laa-civil-case-api/blob/main/LICENSE",
    },
    "docs_url": "/",
}
