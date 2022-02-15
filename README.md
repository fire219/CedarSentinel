![Cedar Sentinel](/readme_files/logo_sm.png)
## A Discord/IRC bot for automated spam detection

### About

**CedarSentinel** is a Python bot for your Discord and/or IRC servers to
automatically detect spam messages *(or any sort of message you don't like!)*.
It can alert your moderators instantly, allowing them to take action faster.
It also has support for
[**Matterbridge**](https://github.com/42wim/matterbridge/)-type chat bridges,
allowing it to also handle messages from many more chat platforms!

### How to install

```bash
git clone https://github.com/fire219/CedarSentinel.git
cd CedarSentinel
pip install pyyaml discord.py irc git+https://git.kj7rrv.com/kj7rrv/gptc@master
cp exampleconfig_<irc|discord>.yaml config.yaml
# edit the config file with your editor of choice!
```

After doing this, Cedar Sentinel can be executed in the same way as any other
Python script.

#### Configuring for use with OCR

CedarSentinel can be optionally configured to do [Optical character recognition](https://en.wikipedia.org/wiki/Optical_character_recognition) (also known as OCR) on all images. This system requires many additional Python modules to be installed:

```bash
pip install opencv-python pytesseract numpy # this command is unnecessary if you don't want image OCR functionality
# change the value of "ocrEnable" in your config.yaml file to "true" to enable OCR
```

If any of the above modules are missing, CedarSentinel will alert you at startup, but otherwise will work normally (albeit with OCR disabled).

### Using CedarSentinel

In a sense, CedarSentinel is easy to set up. Once you have the config file set
how you want it, there are no commands to fiddle with in-chat. CedarSentinel
is immediately watching for spam as soon as you start it for the first time.
It comes pre-configured with a model trained on messages from the Pine64 Chat
Network.

However, it may not be trained properly for the type of spam that *you* have
to deal with. If it's not detecting your spam, or if it's detecting messages
that *aren't* spam, check out the ***How to train models*** section below.

### How to train models

As previously mentioned, CedarSentinel comes with a model trained for the
Pine64 Chat Network. If this model just isn't working for you, then it is
time to check out the **modelbuilder.py** tool included with CedarSentinel.

The Model Builder is designed to intake spam logs that CedarSentinel itself
creates *(assuming you have it enabled in the config!)* and convert them into
GPTC models that CedarSentinel makes its decisions based on. 

As a starting point, **empty_model.json** is included for use in training from
scratch. If you wish to do so, configure CedarSentinel to use this model. If
you want to build on the existing data, leave it with the default model. Now,
let it sit running in your chat for a while. Assuming you haven't dramatically
changed `script.txt` (see "CedarScript" below), it should start logging
messages in your server. *(If you used the empty_model, it will likely log all
messages!)*. After an indeterminate amount of time (up to you, but more
messages are better!), it's time to use the Model Builder.

First, run it as `modelbuilder.py import`. This will import the messages from
your "spam" log into its workspace. It should then show you a message and ask
you if it is Good, Spam, or Unknown. Answer accordingly, and then hit enter.
It will then give you the next message, and so on. Take your time, and make
sure you label messages correctly. CedarSentinel relies on this data to make
its decisions. If you need to stop at any time, hit Ctrl+C, and it will save
your progress and exit. Remember to delete `spam_log.json` after
`modelbuilder.py import`! When its time to start labeling the messages again,
simply run `modelbuilder.py` without arguments, and it will start back where
you left off.

Once you have labeled all messages in your log, you now need to compile the
model. You can do this by simply running `modelbuilder.py compile`. At this
point, your new model (at **compiled_model.json**) is ready for use in
CedarSentinel! Go ahead and delete your existing spam log, set CedarSentinel
to use this model in the config, and restart it! If you've followed these
instructions properly, CedarSentinel should now be trained to work on your
server.

As time goes on, you may refine the model by continuing to use the logs
CedarSentinel creates. You can follow these instructions again from
`modelbuilder.py import`, and as long as you have not deleted the workspace
file (**model_work.json**), it will build on your existing model. ***It will
take time to get CedarSentinel fully acclimated with your server, so don't be
alarmed if the first few iterations aren't very effective!*** As the model
improves, so will the detection rate.

### CedarScript

CedarSentinel's responses to messages are defined by `script.txt`. Note that a
syntax error in `script.txt` will likely result in an error message that
appears to be caused by a bug in CedarSentinel. (If you do get an error,
please submit an issue anyway, just in case it is a CedarSentinel bug. If you
have changed `script.txt`, please include your modified version.)

#### `if ... end`

    if ...
        ...
    end

#### `if ... else ... end`

    if ...
        ...
    else
        ...
    end

#### Comparisons

CedarScript's comparison syntax is different from that of most programming
languages. The following are some simple comparisons:

    <0.5 confidence>
    [20 length]
    {5 reputation}
    /5 reputation\

The syntax is an opening comparator, a space-separated list of values, and a
closing comparator. The following comparators are defined:

| Comparators | Python equivalent |
|-------------|-------------------|
| `<...>`     | `<`               |
| `[...]`     | `<=`              |
| `{...}`     | `==`              |
| `/...\`     | `!=`              |

Items in a comparison are compared in order, left to right. For `{...}` and
`/...\`, order is not significant, but it is for `<...>` and `[...]`. The
example comparisons listed above translate to the following in Python:

    0.5 < confidence
    20 <= length
    5 == reputation
    5 != reputation

Comparisons are not limited to two values, although having more than three is
rarely, if ever, useful. `<0.4 confidence 0.6>` translates to `0.4 <
confidence < 0.6`.

##### Conjunctions, grouping, and order of operations.

CedarSentinel's conjunctions (`and`, `or`) and grouping (with parenthesis)
work the same as Python's. Any difference is a bug that should be reported.

#### Inputs

Inputs are values provided to the script by CedarSentinel. The following are
available:

| Name         | Meaning                             |
|--------------|-------------------------------------|
| `confidence` | Confidence that the message is spam |
| `reputation` | The message's author's reputation   |
| `length`     | The length of the message           |

#### Actions

Actions are how the script tells CedarSentinel what to do in respone to
the message. The following are available:

| Name                 | Meaning                                   |
|----------------------|-------------------------------------------|
| `flag`               | Flag the message as spam                  |
| `log`                | Log the message for manual classification |
| `increasereputation` | Increase the author's reputation          |
| `decreasereputation` | Decrease the author's reputation          |

### Contributors

**CedarSentinel** is primarily developed by Matthew Petry (fireTwoOneNine) and
Samuel Sloniker (kj7rrv). Feel free to fork it and push your improvements
and/or bugfixes upstream!

### License
MIT License

```
Copyright 2021 Matthew Petry (fireTwoOneNine) and Samuel Sloniker (kj7rrv)
Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"),  to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense,  and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```
