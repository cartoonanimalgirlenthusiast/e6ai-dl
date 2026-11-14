A simple Python script for downloading all files containing a certain tag from E6AI.

Update: E6AI is no more, but the script can still be used to download files from sites that use the same API, such as floofgens.net or blep.art (the latter might not allow this yet). The default API URL has been changed to https://floofgens.net.

Installation
============
The only 3rd party library being used is ``requests``, so it's a bit overkill to create a virtual environment. Assuming you already have Python installed, just open ``cmd.exe`` (Windows) or ``Terminal`` (OSX/Linux) and run:

.. code-block:: bash

  $ python -m pip install requests

If you want to create a virtual environment:

.. code-block:: bash

  $ python -m pip venv venv
  $ ./venv/bin/pip install -r requirements.txt

Setup
=====
**Optional**

You can run the script directly without any additional configuration, however E6AI blocks URLs from anonymous access if they contain certain tags, such as ``young``, causing posts containing these tags to be skipped by the script. If you want to download everything, you'll need to provide your e6ai.net login name and an API key for your account. Note that the API key is NOT your account password. Even so, it can let people impersonate you, so don't share it with anyone.

To obtain an API key

* go to your user profile in E6AI
* click Settings at the top
* click the Apps tab
* click Manage API Keys
* confirm password
* click Create API Key
* set the name and expiration to whatever you want

The new API key will now be listed on the page. Copy the key (the string of random numbers and letters under the Key column).

Open ``config.txt`` from this repository, put your login name and API key on the corresponding lines, and save the file.

Usage
=====
**Standard Use**

Simply run the command

.. code-block:: bash

  $ python e6ai.py [tag]

(without the brackets)

If there are special characters such as parentheses in the tag, the tag must be surrounded by quotes. E.g.:

.. code-block:: bash

  $ python e6ai.py "pokemon_(species)"

The tag can be any kind of tag (artist, character, general, etc.). Since this script currently only supports one tag at a time, general tags are not recommended due to high likelihood of overlap. Artist or copyright tags are recommended.

The files will be downloaded into a subfolder named ``e6ai_downloads/[tag]``. Each file will be named after its MD5 hash (the same name it had on E6AI).

Alongside each image/video file will be a corresponding JSON file that contains all the info the file had on E6AI (tags, post date, source, description, etc.). 

**Download Everything**

If you run the script without specifying a tag, the script will gather a list of **all** directors/artists and download everything from all of them. Obviously this will take a long time, and you'll need plenty of free space for it (E6AI had about 560 GB of content by the time it was shut down).
