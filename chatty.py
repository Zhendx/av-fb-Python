### Librerias  de python ###
import nltk
from nltk.stem import WordNetLemmatizer
import numpy as np
import random
from keras.models import load_model
import pickle
import pymongo

class Chatty:
    def __init__(self):
        # Conexion con la base de datos
        client = pymongo.MongoClient("mongodb+srv://bot:bot@cluster0.yixc3.mongodb.net/Bot?retryWrites=true&w=majority")
        db = client.Bot
        # Docs generados a partir del entrenamiento del chat Bot
        self.col = db["intents"]
        self.words = pickle.load(open('words.pkl','rb'))
        self.classes = pickle.load(open('classes.pkl','rb'))
        self.model = load_model('chatbot_model.h5')
        self.lemmatizer = WordNetLemmatizer()

    def clean_up_sentence(self, sentence):
        sentence_words = nltk.word_tokenize(sentence)
        sentence_words = [self.lemmatizer.lemmatize(word.lower()) for word in sentence_words]
        return sentence_words

    def bow(self, sentence, show_details=True):        
        sentence_words = self.clean_up_sentence(sentence)
        # bolsa de palabras - matriz de N palabras, matriz de vocabulario
        bag = [0]*len(self.words)
        for s in sentence_words:
            for i,w in enumerate(self.words):
                if w == s:
                    # Asigna 1 si la palabra actual está en la posición del vocabulario
                    bag[i] = 1
                    if show_details:
                        print ("found in bag: %s" % w)
        return(np.array(bag))

    def predict_class(self, sentence):
        # Filtra las predicciones
        p = self.bow(sentence, show_details=False)
        res = self.model.predict(np.array([p]))[0]
        ERROR_THRESHOLD = 0.25
        results = [[i,r] for i,r in enumerate(res) if r>ERROR_THRESHOLD]
        # Ordena la probabilidad
        results.sort(key=lambda x: x[1], reverse=True)
        return_list = []
        for r in results:
            return_list.append({"intent": self.classes[r[0]], "probability": str(r[1])})
        return return_list

    def getResponse(self, ints):
        tag = ints[0]['intent']
        for i in self.col.find():
            if(i['tag']== tag):
                result = random.choice(i['responses'])
                break
            else:
                result = "Disculpa, no he entendido tu mensaje, ¿podrías ser más específico?"
        return result

    def getResponseIntent(self, ints):
        tag = ints[0]['intent']
        for i in self.col.find():
            if(i['tag']== tag):
                result = tag
                break
            else:
                result = "Null"
        return result

    def chatbot_response(self, msg):
        ints = self.predict_class(msg)
        res = self.getResponse(ints)
        return res

    def chatbot_intent(self, msg):
        ints = self.predict_class(msg)
        res = self.getResponseIntent(ints)
        return res

    
