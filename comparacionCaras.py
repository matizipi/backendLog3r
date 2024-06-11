import math
from repository.configRepository import get_config_repository
from repository.usersRepository import get_user_repository
from repository.imagenesRepository import get_image_embeddings

THRESHOLD = get_config_repository('certeza')[0]['valor']

def compararEmbeddingConDB(embedding_input):
    if len(embedding_input) < 1:
        return -1

    user = -1
    cursor = get_image_embeddings()
    max_imagen_similitude = -1
    max_similitude = 0
    for imagen in cursor:

        embeddings_db = imagen['embedding']
        # check if empty
        if len(embeddings_db) == len(embedding_input):

            aux = calculateCosineSimilarity(embedding_input, embeddings_db)
            if (aux > max_similitude and aux > THRESHOLD):
                max_imagen_similitude = imagen
                max_similitude = aux

    cursor.close()
    if(max_imagen_similitude != -1):
        user = get_user_repository(max_imagen_similitude['userId'],with_horarios=True,with_lugares=True)
    return user


def calculateCosineSimilarity(embeddings1,embeddings2):
    dotProduct = 0.0
    norm1 = 0.0
    norm2 = 0.0

    for i in range((len(embeddings1))): 
        
        dotProduct += embeddings1[i] * embeddings2[i]
        norm1 += embeddings1[i] * embeddings1[i]
        norm2 += embeddings2[i] * embeddings2[i]
        
    cosine_similarity = dotProduct / (math.sqrt(norm1) * math.sqrt(norm2))
    return float(cosine_similarity)


def getTHRESHOLD():
    return THRESHOLD

def setTHRESHOLD(nuevo_umbral):
    global THRESHOLD
    THRESHOLD = nuevo_umbral
