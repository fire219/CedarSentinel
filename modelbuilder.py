# Copyright (c) 2021 Samuel Sloniker (kj7rrv)

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to
# deal in the Software without restriction, including without limitation the
# rights to use, copy, modify, merge, publish, distribute, sublicense, and/or
# sell copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS
# IN THE SOFTWARE.

import json
import gptc
import sys
import os

try:
    with open("model_work.json") as f:
        workspace = json.load(f)
except FileNotFoundError:
    print("No existing model workspace found. Continuing fresh.")
    workspace = {"messages": [], "model": []}


if "compile" in sys.argv:
    with open("compiled_model.json", "w+") as f:
        json.dump(gptc.compile(workspace["model"]), f)
    sys.exit(0)

try:
    if "import" in sys.argv:
        spam_log = []
        with open("spamLog.json", encoding="utf-8") as f:
            lines = f.readlines()
            for line in lines:
                try:
                    spam_log.append(json.loads(line.replace(",\n", ""))["message"])
                except:
                    pass
        workspace["messages"] += spam_log
        response = input("imported. Would you like to clear the now-imported spam log? [Y/N]?").strip().lower()
        if "y" in response:
            with open("spamLog.json", "w", encoding="utf-8") as f:
                print("spam log cleared.")
    
    if "imageimport" in sys.argv:
        import pytesseract
        spam_log = []
        imageDir = input("What is the name of the folder containing spam images? ")
        os.chdir(imageDir)
        i = 0
        fileCount = len(os.listdir(os.getcwd()))
        for file in os.listdir(os.getcwd()):
            i = i + 1
            print("Please wait. Images processed: " + str(i) + " of " + str(fileCount))
            rawRead = pytesseract.image_to_string(file)
            try:
                spam_log.append(rawRead)
            except:
                pass
        workspace["messages"] += spam_log
        response = input("imported. Would you like to delete the now-imported spam images [Y/N]? ").strip().lower()
        if "y" in response:
            for file in os.listdir(os.getcwd()):
                os.remove(file)
            print("spam images cleared.")
        os.chdir("..")
        

    while workspace["messages"]:
        message = workspace["messages"].pop(0)
        if message.startswith("[") and ">" in message:
            message = message.split(">", 1)[1]
        message = message.strip()
        if not any((char == "'") or char.isalpha() for char in message):
            continue
        if not message:
            continue
        print(message)
        response = "________"
        while not response in "sgu":
            response = (
                input("[S]pam/[G]ood/[U]nknown/[Ctrl-C] Exit: ").strip().lower() + " "
            )[0]
        if response == "s":
            workspace["model"].append({"category": "spam", "text": message})
        elif response == "g":
            workspace["model"].append({"category": "good", "text": message})
except KeyboardInterrupt:
    pass

with open("model_work.json", "w+") as f:
    json.dump(workspace, f)
