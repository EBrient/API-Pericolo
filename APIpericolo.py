#!/usr/bin/env python
# -*- coding:utf-8 -*-

from flask import Flask, request, flash, redirect, url_for, render_template
from flask import send_file
from werkzeug import secure_filename
import os
from Pericolo.libs.image_warper import ImageWarper
import shutil
from skimage import io


app = Flask(__name__)
app.secret_key = '0000'

DOSSIER = './images/'
DOSSIER_TEMP = './images/temp/'
DOSSIER_WWARPED = './images/well_warped/'
DOSSIER_UNWARPED = './images/unwarped/'
DOSSIER_WARPED = './images/warped'

def extension_ok(nomfic):
    """ Renvoie True si le fichier possède une extension d'image valide. """
    return '.' in nomfic and nomfic.rsplit('.', 1)[1] in ('png', 'jpg', 'jpeg', 'gif', 'bmp')

@app.route('/', methods=['GET', 'POST'])
def upload():
    images = [img for img in os.listdir(DOSSIER_TEMP) if extension_ok(img)] # la liste des images dans le dossier
    already_in = []
    bad_ext = []
    if request.method == 'POST':
        f = request.files.getlist('fic[]')
        if f: # on vérifie qu'un fichier a bien été envoyé
            for file in f:
                nom = secure_filename(file.filename)
                if extension_ok(file.filename): # on vérifie que son extension est valide
                    if nom not in os.listdir(DOSSIER_UNWARPED) and nom not in os.listdir(DOSSIER_WARPED):
                        file.save(DOSSIER_TEMP + nom)
                    else:
                        already_in.append(nom)
                else:
                    bad_ext.append(nom)
            for noms in bad_ext:
                flash(u'Le fichier {} est à un format non compatible'.format(noms), 'error')
            for noms in already_in:
                flash(u'Le fichier {} a déjà été warpé, vous pouvez le retrouver dans le dossier '.format(noms)
                      + str(DOSSIER), 'error')
            return redirect('/')
        else:
            flash(u'Vous avez oublié le fichier !', 'error')
    return render_template('Accueil.html', images=images)

@app.route('/view/<nom>')
def upped(nom):
    nom = secure_filename(nom)
    if os.path.isfile(DOSSIER_WARPED + nom): # si le fichier existe
        return send_file(DOSSIER_WARPED + nom, as_attachment=True) # on l'envoie
    if os.path.isfile(DOSSIER_UNWARPED + nom): # si le fichier existe
        return send_file(DOSSIER_UNWARPED + nom, as_attachment=True) # on l'envoie
    else:
        flash(u'Fichier {nom} inexistant.'.format(nom=nom), 'error')
        return redirect(url_for('upload')) # sinon on redirige vers la liste des images, avec un message d'erreur

@app.route('/script/')
def warping():
    list = os.listdir(DOSSIER_TEMP)
    unwarped = []
    well_warped = []
    for img in list:
        iw = ImageWarper(DOSSIER_TEMP + img)
        auto_warped_img = iw.warp()  # Automated warping
        save_name = DOSSIER_WARPED + img
        result_log = iw.logs  # Get the validation steps as a dictionnary
        if auto_warped_img is None:
            shutil.move(DOSSIER_TEMP + img, DOSSIER_UNWARPED + img)
            unwarped.append(img)
        else:
            well_warped.append(img)
            io.imsave(save_name, auto_warped_img)
            shutil.move(DOSSIER_TEMP + img, DOSSIER_WWARPED + img)
    return render_template('results.html', unwarped=unwarped, well_warped=well_warped)

if __name__ == '__main__':
    app.run(debug=True)


## A faire : 1) Vérifier qu'on rajoute pas une photo déjà testé 2) afficher les photos warped and unwarped