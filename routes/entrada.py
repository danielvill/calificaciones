from flask import Blueprint, render_template, request, flash, session, redirect, url_for
from controllers.database import Conexion as dbase
from modules.entrada import Entrada
from pymongo import MongoClient
db = dbase()
entrada = Blueprint('entrada', __name__)
