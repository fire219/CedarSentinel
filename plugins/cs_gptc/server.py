import asyncio
import sqlite3
import tornado.web, tornado.escape

def count_string(displayed_count, total_count):
    if total_count == 0:
        return "No messages in category"
    if displayed_count == total_count == 1:
        return "Showing only message in category"
    if displayed_count == total_count == 2:
        return "Showing both messages in category"
    if displayed_count == total_count:
        return f"Showing all {displayed_count} messages in category"
    return f"Showing {displayed_count} message{'' if displayed_count == 1 else 's'} out of {total_count} in category"

style = """\
* {
    font-family: sans-serif;
}

th {
    text-align: left;
}

table {
    border: 1px solid black;
    border-collapse: collapse;
    max-width: 100% !important;
}

th, td {
    border-left: 1px solid black;
    padding: 3px;
}

th.message, td.message {
    word-wrap: anywhere;
}

tbody tr:nth-child(even) {
    background-color: #DDF;
}

thead, tfoot {
    background-color: #333;
    color: white;
}

input[type="checkbox"] {
    height: 1.5em;
    width: 1.5em;
}
"""

script = """\
var is_submitting = false

document.querySelector("#switch_menu").addEventListener(
    "change",
    function() {
        document.querySelector("#switch_form").submit()
    }
)

document.querySelector("#recat_form").addEventListener(
    "submit",
    function() {
        is_submitting = true
    }
)

function has_changes() {
    let result = false
    document.querySelectorAll("input[type=checkbox]").forEach(
        function(checkbox) {
            if (checkbox.checked) {
                result = true
            }
        }
    )
    return result;
}

window.addEventListener(
    "beforeunload",
    function (e) {
        if (is_submitting || ! has_changes()) {
            return undefined
        } else {
            e.preventDefault()
            var confirmation_message = 'Are you sure? Your changes will not be saved.'
            (e || window.event).returnValue = confirmation_message
            return confirmation_message
        }
    }
)

"""


categories = {
    "good": "Known good",
    "probably_good": "Probably good",
    "unknown": "Unknown",
    "probably_spam": "Probably spam",
    "spam": "Known spam",
    "trash": "Trash",
}


class MainHandler(tornado.web.RequestHandler):
    def get(self):
        current = self.get_argument("category", "unknown")
        offset = int(self.get_argument("offset", "0"))
        options = "\n".join(
            [
                f'                <option value="{code}"{" selected" if code == current else ""}>{visible}</option>'
                for code, visible in categories.items()
            ]
        )
        current_user = categories[current]
        cursor = con.cursor()
        cursor.execute(
            "SELECT id, message FROM log WHERE category=?", (current,)
        )
        rows = ""
        data = cursor.fetchall()
        total_count = len(data)
        max_offset = total_count // 100 * 100
        offset = min(offset, max_offset)
        data = data[offset : offset + 100]
        for id, message in data:
            rows += f"""\
                    <tr>
                        <td class="checkbox"><input type="checkbox" name="check-{id}"></td>
                        <td class="message">{tornado.escape.xhtml_escape(message)}</td>
                    </tr>
"""

        self.write(
            f"""\
<!DOCTYPE html>
<html>
    <head>
        <title>CedarSentinel GPTC Trainer</title>
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <style>
{style}
        </style>
    </head>
    <body>
        <h1>CedarSentinel GPTC Trainer</h1>
        <h2>Category: {current_user}</h2>
        <p>If you would like to look at messages in a different category, use the dropdown menu below to select the desired category<noscript>, then click "Switch category</noscript>.<noscript>"</noscript></p>
        <nav><form method="GET" action="" id="switch_form">
            <select name="category" id="switch_menu">
{options}
            </select>
            <noscript><button>Switch category</button> Any changes you may have made on this page will not be saved!</noscript>
        </form></nav>
        <p>{count_string(len(data), total_count)}{"<!--" if len(data) == total_count else ""}, starting at {offset}{"-->" if len(data) == total_count else ""}.</p>
        {"<!--" if max_offset == 0 else ""}<form method="GET" action="">
            <p>Start at <input type="number" name="offset" min="0" max="{max_offset}" step="100" value="{offset}"> (0 to {max_offset}, increments of 100) instead?
            <button>Go</button>
            <noscript>Any changes you may have made on this page will not be saved!</noscript>
            <input type="hidden" name="category" value="{current}"></p>
        </form>{"-->" if max_offset == 0 else ""}
        {"<!--" if len(data) == 0 else ""}<form method="POST" action="" id="recat_form">
            <table>
                <thead>
                    <tr>
                        <th class="checkbox" id="header-check"></th>
                        <th class="message">Message</th>
                    </tr>
                </thead>
                <tbody>
{rows}
                </tbody>
                <tfoot>
                    <tr>
                        <th class="checkbox" id="footer-check"></th>
                        <th class="message">Message</th>
                    </tr>
                </tfoot>
            </table>
            <p>To move messages to a different category, select the check boxes next to the messages you want to move in the table above, select the desired category in the dropdown below, and click "Recategorize messages."</p>
            <select name="category">
{options}
            </select>
            <input type="hidden" name="current_category" value="{current}"><input type="hidden" name="offset" value="{offset}">
            <button>Recategorize messages</button>
        </form>{"-->" if len(data) == 0 else ""}
        <script>
{script}
        </script>
    </body>
</html>
"""
        )

    def post(self):
        messages = [
            int(i.split("-")[1])
            for i in self.request.body_arguments.keys()
            if i.startswith("check-")
        ]
        category = self.get_body_argument("category")
        cursor = con.cursor()
        for message in messages:
            cursor.execute(
                "UPDATE log SET category=? WHERE id=?", (category, message)
            )
        con.commit()
        self.redirect(
            "?category="
            + self.get_body_argument("current_category")
            + "&offset"
            + self.get_body_argument("offset")
        )


def make_app():
    return tornado.web.Application(
        [
            (r"/", MainHandler),
        ]
    )


async def main():
    app = make_app()
    app.listen(8888, address='127.0.0.1')
    await asyncio.Event().wait()


def run():
    global con
    con = sqlite3.connect(config["database"])
    asyncio.run(main())
