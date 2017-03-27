from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import User
from django.conf import settings
from main.models import UserProfile, Project

from anvio.utils import get_names_order_from_newick_tree

import sqlite3
import datetime
import shutil
import os

class Command(BaseCommand):
    help = 'Import UserDB, usage: importuserdb <userdbpath> <userfilespath>'

    def add_arguments(self, parser):
        parser.add_argument('userdb_path', nargs='+', type=str)
        parser.add_argument('userfiles_path', nargs='+', type=str)

    def handle(self, *args, **options):
        conn = sqlite3.connect(options['userdb_path'][0])

        """
        CREATE TABLE users (
        0    login TEXT PRIMARY KEY, 
        1    firstname TEXT, 
        2    lastname TEXT, 
        3    email TEXT, 
        4    password TEXT,
        5    path TEXT,
        6    token TEXT, 
        7    accepted INTEGER,
        8    project TEXT,
        9    affiliation TEXT,
        10   ip TEXT,
        11   clearance TEXT,
        12   date TEXT,
        13   visit TEXT)
        """

        print("Migrating users table...")
        user_paths = {}

        for row in conn.execute('SELECT * FROM users;'):
            username = row[0]
            password = "crypt$$" + row[4]
            email = row[3]
            is_active = True
            is_superuser = True if row[11] == 'admin' else False

            user_paths[row[5]] = username
            date_joined = datetime.datetime.strptime(row[12] + " UTC", "%Y-%m-%d")

            newuser = User(username=username, password=password, email=email, is_active=is_active, is_superuser=is_superuser, is_staff=is_superuser, date_joined=date_joined)
            newuser.save()

            fullname = "%s %s" % (row[1], row[2])
            institution = row[9]

            if len(fullname) < 2:
                fullname = None

            newuser_profile = UserProfile(user=newuser, fullname=fullname, orcid=None, institution=institution)
            newuser_profile.save()

        print(" - Successful.")
        print("Moving project files... ")

        for path in user_paths:
            username = user_paths[path]

            # old user project dir
            src = os.path.join(options['userfiles_path'][0], path)

            #new user project dir
            dst = os.path.join(settings.USER_DATA_DIR, username)

            try:
                shutil.copytree(src, dst)
            except FileNotFoundError:
                # if user path does not exists create empty dir for user
                os.makedirs(dst)
        print(" - Successful")
        print("Migratins project table... ")
        
        """
        CREATE TABLE projects (
        0    name TEXT PRIMARY KEY, 
        1    path TEXT, 
        2    user TEXT, 
        3    description TEXT)
        """
        for row in conn.execute('SELECT * FROM projects;'):
            name = row[0]
            path = row[1]
            username = row[2]
            description = row[3]

            if not description or not len(description) > 0:
                description = ""

            newproject = Project(name=name, user=User.objects.get(username=username), secret=path)
            newproject.save()

            project_path = newproject.get_path()

            if not os.path.exists(newproject.get_profile_path()):
                newproject.create_profile_db(description)
            else:
                try:
                    if description and len(description) > 0:
                        newproject.set_description(description)

                    if os.path.exists(os.path.join(project_path, 'treeFile')):
                        newproject.num_leaves = len(get_names_order_from_newick_tree(os.path.join(project_path, 'treeFile')))

                    if os.path.exists(os.path.join(project_path, 'dataFile')):
                        newproject.num_layers = len(open(os.path.join(project_path, 'dataFile')).readline().rstrip().split('\t')) - 1
                except: 
                    print("there is something wrong with this project: " + project_path)

                newproject.save()
        print(" - Successful")






