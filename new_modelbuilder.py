import json
import gptc
import sys

with open('model_work.json') as f:
    workspace = json.load(f)

if 'compile' in sys.argv:
    with open('compiled_model.json', 'w+') as f:
        json.dump(gptc.compile(workspace['model']), f)
    sys.exit(0)

try:
    if 'import' in sys.argv:
        spam_log = [] 
        with open('spamLog.json') as f:
            lines = f.readlines()
            for line in lines:
                try:
                    spam_log.append(json.loads(line.replace(',\n', ''))["message"])
                except:
                    pass
        workspace["messages"] += spam_log
        print('imported')

    while workspace['messages']:
        message = workspace['messages'].pop(0)
        if message.startswith('[') and '>' in message:
            message = message.split('>', 1)[1]
        message = message.strip()
        if not message:
            continue
        print(message)
        response = '________'
        while not response in 'sgu':
            response = input('[S]pam/[G]ood/[U]nknown/[Ctrl-C] Exit: ').strip().lower()[0]
        if response == 's':
            workspace['model'].append({"category": "spam", "text": message})
        elif response == 'g':
            workspace['model'].append({"category": "good", "text": message})
except KeyboardInterrupt:
    pass

with open('model_work.json', 'w+') as f:
    json.dump(workspace, f)
