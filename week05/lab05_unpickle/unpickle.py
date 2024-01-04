import pickle
from collections import Counter 

def most_common():
        
    file = open("shapecolour.p", 'rb')
    shapecolour = pickle.load(file)
    
    colour = [x["colour"] for x in shapecolour]
    freq_colour = Counter(colour).most_common(1)[0]
    
    shape = [x["shape"] for x in shapecolour]
    freq_shape = Counter(shape).most_common(1)[0]
    
    output = {"Colour": freq_colour[0], 
               "Shape": freq_shape[0],
              }
    print(output)
    return output
 
most_common()
