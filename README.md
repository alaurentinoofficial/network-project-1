# HTTP Server

Basic HTTP server to delivery HTML and a file explorer

<br>

### Run

* It's necessary have Python 3 - [Download Here](https://www.python.org/downloads/)

```sh
python3 main.py
```


<br>


### File explorer

If in a folder there is a index.html, this file is redereded by default, otherwise show the file in the `static` folder like the image below:

![files](/assets/files.png)


<br>

### Large files

Other thing super important it is to be capble to download large files using thread and sending the chucks little by little to do not overflow the server memory.

![download](/assets/download.png)

<br>

### See content using browser media

Other valueble aspect it is interpret files properly in the browser using the variateted content types, as plain text or binary, like HTML, json, pdf, mp3, wav, mp4 and other.

<p align="center">
  <img width="460" height="250" src="/assets/html.png">
  <br>
  <em>html</em>
</p>

<p align="center">
  <img width="460" height="250" src="/assets/mp3.png">
</p>

<p align="center">
  <img width="460" height="300" src="/assets/pdf.png">
</p>