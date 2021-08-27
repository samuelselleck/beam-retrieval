# Installation 

```sh
pip install LightPipes numpy matplotlib PyQt5
```

* Run beam_retrieval/gui.py

# Create executable

Download pyinstaller and run

```sh
pyinstaller beam_retrieval/gui.py -y --noconsole --add-data="mainwindow.ui;."
```