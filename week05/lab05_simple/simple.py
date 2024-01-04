'''comp1531 lab05 simple.py by Celine Lin'''
from flask import Flask, request
from json import dumps
from error import InputError

app = Flask(__name__)
names = []
@app.route("/name/add", methods=['POST'])
def add(): 
    '''append name to the 'names' list'''
    data = request.get_json()
    name = data['name']
    names.append(name)
    return dumps({})
    
@app.route("/names", methods=['GET'])
def print_names():
    '''return the list "name"'''
    return dumps({'names': names})

@app.route("/name/remove", methods=['DELETE'])
def remove():
    '''find the name and remove the name from the list'''
    data = request.get_json()
    delete_name = data['name']
    try:
        names.remove(delete_name)
        return dumps({})
    except ValueError:
        raise InputError("The name does not exist!")


if __name__ == '__main__':
    app.run(port=0, debug=True)
