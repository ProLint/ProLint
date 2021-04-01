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
The installation process above has been test on MacOS and confirmed to work. Linux should work too. I assume WSL 2 would also work, although I have not tested it yet. <br>

If you are using Windows OS directly (e.g., through the command prompt, or powershell, or anaconda prompt for windows), then you may get errors because of the different line-ending termination. To fix this, you need to tell git to keep line endings as they are. You can do that globally or on a per-repo basis. The instructions below are for configuring git globally, but if you want to do it for the repo specifically please <a href="https://docs.github.com/en/github/getting-started-with-github/configuring-git-to-handle-line-endings" target="_blank"> read here<a/> for instructions.
  
```sh
# Windows users
git config --global core.autocrlf input
docker-compose up --build
```

## What you need to know
The following are a list of things I think are important to know:
- The docker build will show useful information about your session, and you can use terminals to access the docker images. 
- Celery output is saved on the `logs/celery.log` file, so keep an eye on that when you submit jobs. 
- Submissions are saved in the media/user-data/prolint folder. They are not deleted automatically yet, so please keep an eye on that. 
- The functions to download and delete submissions are kept, but their usefulness is limited since now you have the data locally. 

## Development
All you need to contribute to the development of ProLint is open the ProLint directory with a code editor such as <a href="https://code.visualstudio.com/" target="_blank">VS Code<a/>. Your saves will automatically trigger docker to autoload the build and update the website. 
These updates are, however, not transmitted when you make changes to the `calcul` app which is used by Celery. Celery auto-reload on file save is on the to-do list, however.<br>

  
## Bug report
Please feel free to open an issue or contact us if you encounter any problem or bug while working with ProLint. 
