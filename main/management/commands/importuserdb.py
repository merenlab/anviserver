from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import User
from django.utils.text import slugify
from django.conf import settings
from main.models import UserProfile, Project

from anvio.utils import get_names_order_from_newick_tree
from anvio import dbops

from datetime import datetime
from datetime import timezone

import sqlite3
import shutil
import os

def sanitize_username(username):
    if '@' in username:
        username = username.split('@')[0]

    username = slugify(username).replace('-', '_')

    return username


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
            username = sanitize_username(row[0])
            password = "crypt$$" + row[4]
            email = row[3]
            is_active = True
            is_superuser = True if row[11] == 'admin' else False

            user_paths[row[5]] = username
            date_joined = datetime.strptime(row[12], "%Y-%m-%d").replace(tzinfo=timezone.utc)

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
            username = sanitize_username(row[2])
            description = row[3]

            #rename project files
            fileTypes_old = ['treeFile', 'dataFile', 'fastaFile', 'samplesOrderFile', 'samplesInformationFile']
            fileTypes_new = ['tree.txt', 'data.txt', 'fasta.fa', 'samples-order.txt', 'samples-info.txt']

            for i in range(5):
                try:
                    os.rename(os.path.join(settings.USER_DATA_DIR, username, path, fileTypes_old[i]), os.path.join(settings.USER_DATA_DIR, username, path, fileTypes_new[i]))
                except:
                    pass

            try:
                if not description or not len(description) > 0:
                    description = ""

                project = Project(name=name, user=User.objects.get(username=username), secret=path)

                samples_info = project.get_file_path('samples-order.txt', default=None)
                samples_order = project.get_file_path('samples-info.txt', default=None)
                
                if (samples_info or samples_order) and not project.get_file_path('samples.db', default=None):
                    s = dbops.SamplesInformationDatabase(project.get_file_path('samples.db', dont_check_exists=True), quiet=True)
                    s.create(samples_order, samples_info)

                interactive = project.get_interactive()

                # try to get number of leaves
                try:
                    leaves = get_names_order_from_newick_tree(project.get_file_path('tree.txt', default=None))
                    project.num_leaves = len(leaves) if leaves != [''] else 0
                except:
                    project.num_leaves = 0

                # try to get number of layers
                try:
                    project.num_layers = len(interactive.views['single'][0]) - 1 # <- -1 because first column is contigs
                except:
                    project.num_layers = 0

                # store description
                dbops.update_description_in_db(project.get_file_path('profile.db', default=None), description or '')

                project.synchronize_num_states()
                project.synchronize_num_collections()

                project.save()
            except Exception as e:
                print(username + " " + name + " " + path + " failed to create project, here is the exception " + str(e))
                shutil.rmtree(os.path.join(settings.USER_DATA_DIR, username, path))
        
        print(" - Successful")






