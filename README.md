# VasttraPi on Google Assistant
A simple Python web server, in Flask, which is interfaced with an Action on Google Assistant. The server reuses code from [VasttraPi](https://github.com/platisd/vasttraPi) to communicate with Västtrafik so to fetch the latest departures for the selected stations.

Read more about the project [here](https://platis.solutions/blog/2018/07/15/custom-actions-for-google-assistant/).

![VasttraPi and Google Home Mini](https://i.imgur.com/4Erjr1K.jpg)

## Get started
If you want a custom Google Action that talks to a sample Python server, then please follow this [Instructable](https://www.instructables.com/id/Create-Custom-Actions-for-Google-Assistant/).

To set up a REST server that retrieves departures from Västtrafik:
* Install PyTrafik
  * `git clone https://github.com/axelniklasson/PyTrafik.git`
  * `sudo pip3 install PyTrafik/`
* Create an `api-config` file in the root folder of this repository with your [Västtrafik API tokens](https://developer.vasttrafik.se/portal/#/applications)
* Edit `bus_assistant.py` by providing your business logic (e.g. stations of interest)
* Run `bus_assistant.py`
  * `python3 bus_assistant.py`

## Media
* [Demo video](https://www.youtube.com/watch?v=Qh_gcRqFTzE)
* [Article on platis.solutions](https://platis.solutions/blog/2018/07/15/custom-actions-for-google-assistant/)
* [Tutorial on Instructables](https://www.instructables.com/id/Create-Custom-Actions-for-Google-Assistant/)
