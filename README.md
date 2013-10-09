## Substream

Subsonic playlist HTTP proxy streamer in Python.

### Requires

* [py-sonic](https://pypi.python.org/pypi/py-sonic)

### Usage

1. Install py-sonic (pip, easy\_install, etc..)
2. Create and edit config 
`
cp config.ex config
`
3. Run
`
python stream.py
`
4. Visit http://localhost:8080 in a browser

### Request Path Reference

#### /
200 - text/plain: Table of playlist Name and ID's

#### /pl/{playlist-id}
200 - audio/mpeg: Stream playlist-id  
400 - bad request missing playlist-id  
404 - playlist-id not found on server  

