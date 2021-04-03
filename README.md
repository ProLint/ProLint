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

## Installation from source
You can also install ProLint directly from source. You can use the provided `environment.yml` file to create the conda environmet. You'll also need to have gromacs installed and sourced for g_surf to work. 
Once installed, remember that you have to run `redis-server`, then in the prolint directory you have to run the `celery` worker and then you also have to run the actual server `python manage.py runserver`. 


## Important things to know
The following are a list of things I think are important to know:
- The docker build will show useful information about your session, and you can use terminals to access the docker images. 
- Celery output is saved on the `logs/celery.log` file, so keep an eye on that when you submit jobs. 
- Submissions are saved in the media/user-data/prolint folder. They are not deleted automatically yet, so please keep an eye on that. 
- The functions to download and delete submissions are kept, but their usefulness is limited since now you have the data locally. The reason why these buttons are kept is clear from the development roadmap provided below. 

## Roadmap 
ProLint is the result of a lot of work and it already provides many features. It is also in very active development and the following is a rough roadmap of what is planned to come to ProLint: 

- A cleaner installation without the notifications and warning messages given by Docker currently. 
- Full support for atomistic simulations. Currently, atomistic data are supported as a beta-feature and we want to fix bugs and add stability to fully handle data at this resolution. 
- Martini 3 should be supported already, but we still need to test it. 
- Allow the user to specify residues manually in the submission form. 
- Provide additional metric support and add the ability for the user to select the preferred ones. 
- Provide support for systems containing multiple different proteins. Currently, support for these systems is partial. 
- Support user-requested features. 

### Support for deployment on local networks. 
This can already be done, but the current config is not secure. We want to allow people to deploy ProLint on a local network where multiple users/members of research groups can use it. For this reason, ProLint already has a working setup with support for secure user accounts and individual pages to track all the submitted jobs and ability to make them available to other members of the local network. This allows members of a group, for example, to share data with others, prepare for group meetings, use the data during presentations (e.g. during zoom calls), and in general, collaborate. This functionality **already exists and has been implemented** in ProLint but currently it has been disabled!

## Development
All you need to contribute to the development of ProLint is open the ProLint directory with a code editor such as <a href="https://code.visualstudio.com/" target="_blank">VS Code<a/>. Your saves will automatically trigger docker to autoload the build and update the website. 
These updates are, however, not transmitted when you make changes to the `calcul` app which is used by Celery. Celery auto-reload on file save is on the to-do list, however.<br>

  
## Bug report
Please feel free to open an issue or contact us if you encounter any problem or bug while working with ProLint. 
