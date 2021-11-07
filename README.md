# Cedar Sentinel
## A Discord Bot for using trained models to detect spam

### How to install

```bash
git clone https://github.com/fire219/CedarSentinel.git
cd CedarSentinel
pip install pyyaml discord.py
cp exampleconfig.yaml config.yaml
# edit the config file with your editor of choice!
```
You must also install [**GPTC**](https://github.com/kj7rrv/gptc "GPTC") (as of Cedar Sentinel v0.2, the "algo2" branch of **GPTC** is required). Currently, this is not available in the PyPI repositories. Therefore, installing it manually to your Python packages directory is recommended.

After doing so, Cedar Sentinel can be executed in the same way as any other Python script.

### How to train models
An example model (and the training data used to create it) is included in this repository, and Cedar Sentinel is preconfigured to use this model. However, if you want to train your own, check out **modelbuilder.py** and the example training data to see how to create your own model. **modelbuilder.py** will in its current state create a *raw model* for GPTC. Before use, you *must* compile the model. Check the [**GPTC documentation**](https://github.com/kj7rrv/gptc "GPTC documentation") for how to do this. After compiling the model, edit **config.yaml** to point to your new model.

### Thanks

- Samuel Sloniker ([kj7rrv](https://github.com/kj7rrv "kj7rrv")) for creating **GPTC** and the **modelbuilder.py** file included in this repo.

### License
MIT License

```
Copyright 2021 Matthew Petry (fireTwoOneNine) and Samuel Sloniker (kj7rrv)
Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), 
to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, 
and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM,
DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE
OR OTHER DEALINGS IN THE SOFTWARE.
```
