# ProLint
This is the source-code for the ProLint Webserver. 

## Installation

#### Install Docker
You need to have <a href="https://docs.docker.com/get-docker/" target="_blank">Docker<a/> installed first, in order to install ProLint. 
  
#### Install ProLint
To install ProLint locally, all you have to do is download/clone the repository: 
```sh
git clone https://github.com/ProLint/ProLint.git
```
and then execute: 

```sh
cd ProLint
docker-compose up
```

The main and only installation command is `docker-compose up`. It will create a Docker build that contains all of the software packages, python libraries and environment configuration required by ProLint to work. 

You may get warning and notifications about missing files, but they are harmless. 

When installation finishes, open a browser and navigate to: 127.0.0.1:8000 

#### Tested
The installation process above has been test on MacOS and confirmed to work. Linux should work too. <br>
~~The thickness & curvature application is currently not working because of some permission issue with the main program g_surf, which we'll fix very soon.~~ FIXED NOW!<br>
For Windows there is a bug with the termination of line-endings on the entrypoint.sh script which will be fixed soon too. 

## What you need to know
The docker build will show useful information about your session. 
Celery output is saved on the `logs/celery.log` file, so keep an eye on that when you submit jobs. 

## Development
All you need to contribute to the development of ProLint is open the ProLint directory with a code editor such as <a href="https://code.visualstudio.com/" target="_blank">VS Code<a/>. Your saves will automatically trigger docker to autoload the build and update the website. 
These updates are, however, not transmitted when you make changes to the `calcul` app which is used by Celery. Celery auto-reload on file save is on the to-do list, however.
  
## Bug report
Please feel free to open an issue or contact us if you encounter any problem or bug while working with ProLint. 
