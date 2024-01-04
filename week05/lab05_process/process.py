from unpickle import most_common
import pickle
import json

def process():
    file = open("shapecolour.p", 'rb')
    shapecolour = pickle.load(file)
    output = {
        "mostCommon" : most_common(),
        "rawData" : shapecolour
        }
     
    with open('processed.json', 'w') as FILE:
        json.dump(output, FILE)
 
process()
