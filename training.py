import cv2
import os
import numpy as np


def treinarLBPH():
    lbph = cv2.face.LBPHFaceRecognizer_create()

    def getImagemComId():
        caminhos = [os.path.join('fotos', f) for f in os.listdir('fotos')]
        faces = []
        ids = []

        for caminhoImagem in caminhos:
            imagemFace = cv2.cvtColor(cv2.imread(caminhoImagem), cv2.COLOR_BGR2GRAY)
            id = int(os.path.split(caminhoImagem)[-1].split('.')[1])
            ids.append(id)
            faces.append(imagemFace)
        return np.array(ids), faces

    ids, faces = getImagemComId()

    print('Treinando...')

    lbph.train(faces, ids)
    lbph.write('classificadorLBPH.yml')

    print('Treinamento concluido!')