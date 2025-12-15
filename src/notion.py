import requests, json
from config.time_helpers import compute_week_from_due

class NotionApi:
    def __init__(
        self,
        notionToken=None,
        database_id=None,
        schoolAb=None,
        version="2021-08-16",
    ):
        self.database_id = database_id
        self.notionToken = notionToken
        self.schoolAb = schoolAb
        self.notionHeaders = {
            "Authorization": "Bearer " + notionToken,
            "Content-Type": "application/json",
            "Notion-Version": "2021-08-16",
        }

    def queryDatabase(self):
        readUrl = f"https://api.notion.com/v1/databases/{self.database_id}/query"

        res = requests.request("POST", readUrl, headers=self.notionHeaders)
        data = res.json()

        with open("./db.json", "w", encoding="utf8") as f:
            json.dump(data, f, ensure_ascii=False)

        return data

    def test_if_database_id_exists(self):
        res = requests.request(
            "GET",
            f"https://api.notion.com/v1/databases/{self.database_id}/",
            headers=self.notionHeaders,
        )

        return json.loads(res.text)["object"] != "error"

    # Creates a new database in page_id page built for Canvas assignments and returns it's database_id
    def createNewDatabase(self, page_id):
        newPageData = {
            "parent": {
                "type": "page_id",
                "page_id": page_id,
            },
            "icon": {"type": "emoji", "emoji": "🔖"},
            "cover": {
                "type": "external",
                "external": {"url": "https://website.domain/images/image.png"},
            },
            "title": [
                {
                    "type": "text",
                    "text": {
                        "content": "Canvas Assignments",
                        "link": None,
                    },
                }
            ],
            "properties": {
                "State": {
                    "formula": {
                        "expression": '(dateBetween(prop("Due Date"), now(), "days") == 0) ? "🟧" : ((dateBetween(prop("Due Date"), now(), "days") < 0) ? "🟥" : "🟩")'
                    }
                },
                "Assignment": {"title": {}},
                "Class": {
                    "type": "select",
                    "select": {"options": []},
                },
                "Due Date": {"date": {}},
                "URL": {"url": {}},
                "Notes": {"rich_text": {}},
                "Semester": {
                    "type": "select",
                    "select": {
                        "options": [
                            {
                                "name": "Y2S1",
                                "color": "blue"
                            },
                            {
                                "name": "Y2S2",
                                "color": "green"
                            },
                            {
                                "name": "Y3S1",
                                "color": "pink"
                            },
                            {
                                "name": "Y3S2",
                                "color": "yellow"
                            },
                            {
                                "name": "Y4S1",
                                "color": "purple"
                            },
                            {
                                "name": "Y4S2",
                                "color": "red"
                            }
                        ]
                    }
                },
                "Week": {
                    "name": "Week",
                    "type": "select",
                    "select": {
                        "options": [
                            {
                                "name": "Week 1",
                                "color": "pink"
                            },
                            {
                                "name": "Week 2",
                                "color": "green"
                            },
                            {
                                "name": "Week 3",
                                "color": "orange"
                            },
                            {
                                "name": "Week 4",
                                "color": "purple"
                            },
                            {
                                "name": "Week 5",
                                "color": "yellow"
                            },
                            {
                                "name": "Week 6",
                                "color": "blue"
                            },
                            {
                                "name": "Recess Week",
                                "color": "brown"
                            },
                            {
                                "name": "Week 7",
                                "color": "red"
                            },
                            {
                                "name": "Week 8",
                                "color": "orange"
                            },
                            {
                                "name": "Week 9",
                                "color": "pink"
                            },
                            {
                                "name": "Week 10",
                                "color": "blue"
                            },
                            {
                                "name": "Week 11",
                                "color": "yellow"
                            },
                            {
                                "name": "Week 12",
                                "color": "purple"
                            },
                            {
                                "name": "Week 13",
                                "color": "green"
                            },
                            {
                                "name": "Reading Week",
                                "color": "red"
                            },
                            {
                                "name": "Exam Week 1",
                                "color": "brown"
                            },
                            {
                                "name": "Exam Week 2",
                                "color": "blue"
                            }
                        ]
                    }
                }
            },
        }

        data = json.dumps(newPageData)

        res = requests.request(
            "POST",
            "https://api.notion.com/v1/databases",
            headers=self.notionHeaders,
            data=data,
        )

        print(res.text)

        newDbId = json.loads(res.text).get("id")

        return newDbId

    def createNewDatabaseItem(
        self,
        id,
        className,
        assignmentName,
        has_submitted=False,
        url=None,
        dueDate=None,
    ):
        # if status:
        #     status = "To do"
        # else:
        #     status = "Completed"

        createUrl = "https://api.notion.com/v1/pages"

        status_name = "Done" if has_submitted else "Not started"

        newPageData = {
            "parent": {"database_id": self.database_id},
            "properties": {
                "Status": {
                    "status": {
                        "name": status_name,
                    }
                },
                "Assignment": {
                    "type": "title",
                    "title": [
                        {
                            "text": {
                                "content": assignmentName,
                            },
                        }
                    ],
                },
                "Class": {
                    "select": {
                        "name": className,
                    }
                },
                "Due Date": {
                    "date": {
                        "start": dueDate,
                    },
                },
                "URL": {
                    "url": url,
                },
                "Week": {
                    "select": {
                        "name": compute_week_from_due(dueDate),
                    }
                }
            },
        }

        data = json.dumps(newPageData)

        res = requests.request("POST", createUrl, headers=self.notionHeaders, data=data)

        print(res.text)

        return res

    def parseDatabaseForAssignments(self):
        urls = []

        if self.queryDatabase().get("results") != None:
            for item in self.queryDatabase().get("results"):
                urls.append(item["properties"]["URL"]["url"])

        return urls
