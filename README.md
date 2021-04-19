# Installing anvi'o and anvi'server

The instructions below are to setup **both anvi'o and anvi'server codebase on the same computer**. This is necessary since anvi'server uses anvi'o modules to display things.

**Taking care of anvi'o**. To have anvi'o running on your system, please follow the instructions on [this installation tutorial](https://merenlab.org/2016/06/26/installation-v2/#5-follow-the-active-development-youre-a-wizard-arry). These instructions will enable you to setup anvi'o in a conda environment that has all the necessary dependencies and tracks the active development branch of anvi'o.

**Adding anvi'server on top**. In addition to that, you will first clone the anvi'server codebase. If you followed the anvi'o installation instructions word-by-word, your anvi'o codebase is under `~/github/anvio` directory, and your conda environment for the active anvi'o branch is called `anvi-dev`. If you have different paths or names for your anvi'o, please replace them in the commands below. Finally, please make sure you run these commands while the conda environment for anvi'o is activated:
 
``` bash
# make sure anvio-dev is activated and you are in the right
# conda environment:
conda activate anvio-dev

# go to the directory where the source code for anvi'o lives:
cd ~/github

# clone the anvi'server active codebase
git clone https://github.com/merenlab/anviserver

# install pip dependencies for anvi'server
pip install -r anviserver/requirements.txt

# and finally install nginx, which will be used to serve anvi'server:
conda install -y nginx
```

Copy-pasta the following lines into your terminal window to update the conda activation file for anvi'o to include point the right `PYTHONPATH` for anvi'server (the contents of this file is run every time the conda environment `anvi-dev` is initiated, with this update, it will also take care of anvi'server buisness):

``` bash
cat <<EOF >${CONDA_PREFIX}/etc/conda/activate.d/anvio.sh

# including additional steps to setup anvi'server properly. the following
# lines ensure (1) Python knows where to find anvi'server libraries and
# (2) anvi'server code is also updated from GitHub every time the anvi'o
# environment is activated:
export PYTHONPATH=\$PYTHONPATH:~/github/anviserver/
echo -e "\033[1;31mUpdating from anvi'server GitHub \033[0;31m(press CTRL+C to cancel)\033[0m ..."
cd ~/github/anviserver && git pull && cd -
EOF
```

It is a good idea to take a look at the final form of this file now to make sure everything looks alright:

```
${CONDA_PREFIX}/etc/conda/activate.d/anvio.sh
```

# Initial settings for anvi'server

Create a copy of the settings and secrets files from their templates:

```
cd ~/github/anviserver
cp anviserver/settings-TEMPLATE.py anviserver/settings.py
cp anviserver/secrets-TEMPLATE.py anviserver/secrets.py
```

Since both `anviserver/settings.py` and `anviserver/secrets.py` are mentioned in the `.gitignore` file, you will not commit your changes to these files mistakenly.

Edit `anviserver/settings.py`:

* Change`DEBUG=True` to `DEBUG=False` (if necessary)
* In SMTP settings section, change `EMAIL_HOST` and `EMAIL_HOST_USER`. You may need to change other values if you want to use any other SMTP host than Gmail. Makes sure the password is stored in `anviserver/secrets.py`.
* Find `# Sentry settings` section and remove it if you do not want to use error tracking and reporting service [Sentry](https://sentry.io/). If you want to keep it you need to open new account and get an API key, later we will put in `anviserver/secrets.py`.

# Setting up Django

Here you will setup Django.

First, delete the following symlink:

```
rm main/static/interactive
```

Then setup the Django database and static files:

```
cd ~/github/anviserver
python manage.py migrate
python manage.py collectstatic
```

Create an admin account:

```
python manage.py createsuperuser
```

# Running Gunicorn

Create a copy of the gunicorn config file from its template, and take a look at the contents:

```
cp gunicorn.conf-TEMPLATE.py gunicorn.conf.py
```

and if/when you are satisfied with what it shows, run it:

```
gunicorn -c gunicorn.conf.py anviserver.wsgi:application --daemon
```

# Run Nginx

Create a copy of the Nginx config file from its template, and take a look at the contents:

```
cp nginx-TEMPLATE.conf nginx.conf
```


Edit `nginx.conf` to,

* Update your domain name, obviously :)
* If you want to disable HTTPS, remove the first `server { ... }` block, and then in second `server { ... }` block change the port number `443` to `80`, then remove the lines that start with `ssl_certificate`, `ssl_certificate`.
* If you want to *keep* HTTPS (as you should ;)), the paths mentioned in lines that start with `ssl_certificate` and `ssl_certificate_key` must resolve to the locations of your SSL certificate.
* Find `location /static` and `location /static/interactive` directives and make sure they are pointing to correct directories on your disk under anvi'server and anvi'o locations.

Finally, replace the system default config file for ngix with the file you just edited (the location of this file will differ from system to system):

```
sudo cp nginx.conf /etc/nginx/sites-enabled/default
```

And start/restart ngix:

```
sudo service nginx restart
```

*Please note that the previous steps to update the config file for ngix and restart the server is tested for Ubuntu systems and require superuser permissions. We would be very happy to update them if you have a better way to do this.*


An important note, if there is a firewall on your system blocking port numbers `80` and/or `443`, you may need to update your rules first. This is how you could do it on an Ubuntu system:

```
sudo ufw allow 80
sudo ufw allow 443
```

At this point, you should be able to visit your anvi'server via your browser, and see it running, and it should be ready to accept new users, user groups, and project files.

# Restarting or updating server

To reflect changes in the anvi'o or anvi'server codebase, you may need to update and/or restart the server. To do this, go inside `anvio` and `anviserver` directories and run `git pull` so you have the latest from the upstream repositories.

Then run `python reset_cache.py`, which is a script that finds every HTML file and appends `?hash=<file hash>` to every static resource (js, css etc.). This will force browsers to not rely on their cache for a given anvi'server project, but request new information.

Finally, restart the gunicorn

```
killall gunicorn && gunicorn -c gunicorn.conf.py anviserver.wsgi:application --daemon
```

# License

This project is licensed under the terms of the [GNU Affero General Public License v3](https://www.gnu.org/licenses/agpl-3.0.en.html).
