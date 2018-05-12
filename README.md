<p align="center">
  <img src="./static/assets/logos/logo.png" width='500'>
</p>

#

A web application that integrates movie, music album, book info queries and comments.
Users are able to search for movie, music and book info from databases supported by APIs.
Useful information is provided within different types of queries, including movie tickets and times, album track previews, best-seller books and previews, sale information, etc.
Signed-in users can give ratings and comments, and add them to their wish-lists.

## Running

### 

- [Demo](http://34.198.185.145)

### Prerequisites

- [Python 3.6](https://www.python.org/)

- [Django 1.11](https://www.djangoproject.com/download/)

- [Virtualenv](https://virtualenv.pypa.io/en/stable/) (optional)

### Install Vitualenv

To install globally with _pip_ (if you have pip 1.3 or greater installed globally)

```bash
$ [sudo] pip install virtualenv
```

Set up an environment for Django

```bash
$ virtualenv djangoenv
```

To activate script

```bash
$ source bin/activate
```

To undo the change to your path (and prompt)

```bash
$ (djangoenv) deactivate
```

On Windows, the equivalent `activate` script is in the `Scripts` folder

```bash
> \djangoenv\Scripts\activate
```

Then, you can install any python package for the app in `djangoenv`, and make it independent from your system environment.

### Libraries

- [tmdbsimple](https://github.com/celiao/tmdbsimple)
- [spotipy](https://github.com/plamere/spotipy)
- [requests](http://docs.python-requests.org/en/master/)

### APIs

- [freegeoip](https://ipstack.com/)
- [Gracenote](http://developer.tmsapi.com/page)
- [Google Books APIs](https://developers.google.com/books/)
- [NYT APIs](https://developer.nytimes.com/)

### Front-end

- [Materialize](http://materializecss.com/)

### Deployment

- [AWS](https://aws.amazon.com/)
- [Apache](https://httpd.apache.org/)


## Authors

- **Zhilin Huang**