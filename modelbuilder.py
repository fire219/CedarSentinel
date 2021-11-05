# Tool for importing and tagging IRC logs for GPTC model
# see .txt files in /model_builder for guidance on expected log format

# Copyright (c) 2021 Samuel Sloniker (kj7rrv) and Matthew Petry
# (fireTwoOneNine)

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
#FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS
# IN THE SOFTWARE.

import os
import sys
import json

if (sys.argv[1]) : filename = sys.argv[1]
else: filename = 'log.txt' # Change this if needed
# Logs must consist only of messages from P64ProtocolBot, and cannot include <
# or > before the actual message sent by the bot

logs = []

with open(filename) as f:
    logs += [ i for i in f.readlines() if i.strip() ]

messages = [['', '', '']]

for log in logs:
    if "[D]" in log: pass
    log_clean = log[37:]
    header, message = log_clean.split('>', 1)
    username = header.split('<', 1)[1].replace('@', '').strip()
    message = message.strip() + '\n'
    if message.strip():
        if messages[-1][0] == username:
            messages[-1][1] += message
        else:
            messages.append([username, message, '[D]' in log])

def get_response(text):
    os.system('clear')
    print(text)
    response = '.'
    while not response in 'snu':
        response = input('[S]pam/[N]ot spam/[U]nknown: ').lower()

    return response

model = []

try:
    for message in messages:
        _, message, is_discord = message
        if is_discord:
            category = 'n'
        else:
            category = get_response(message)
        if category in 'sn':
            model.append({'text': message, 'category': {'s': 'spam', 'n': 'good'}[category]})
except KeyboardInterrupt:
    pass


with open('raw_model.json', 'w+') as f:
    json.dump(model, f)
