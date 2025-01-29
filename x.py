from flask import Flask, render_template,flash, request, redirect, url_for, send_file
import os
import time
from functools import reduce
# from werkzeug.utils import secure_filename
import secrets
secret_key = secrets.token_hex(16)

print(secret_key)
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = '/uploads'
app.config['SECRET_KEY'] = secret_key

class HuffmanCoding:
    def __init__(self, path, file, export_file=None):
        self.export_file = export_file
        self.path = path + file
        self.dictionary = None
        self.text = None
        self.current_directory = path
        self.file_name = file[len(file) - file[::-1].index('/'):len(file) - file[::-1].index('.') - 1]
        if self.export_file is None:
            self.export_file = '/encoded/' + \
                            self.file_name + \
                            '_comp.bin'

    def set_dictionary(self):
        self.dictionary = self.frequency_alphabet_init()

    def set_text(self):
        self.text = self.path_to_string()

    def path_to_string(self):
        with open(self.path, "r") as file:
            return reduce(lambda x, y: x + y, file.readlines())

    def frequency_alphabet(self):
        self.set_text()
        print('INI TEXT ',self.text)
        list_alphabet = dict()
        for letter in self.text:
            if letter in list_alphabet.keys():
                list_alphabet[letter] += 1
            else:
                list_alphabet[letter] = 1
        list_alphabet = list(zip(list_alphabet.keys(), list_alphabet.values()))
        print('INI LIST ALPHABET ',list_alphabet)
        return list_alphabet

    def sorted_alphabet(self, list_alphabet=None):
        if list_alphabet is None:
            list_alphabet = self.frequency_alphabet()
        list_frequency_values = sorted(list(set([value[1] for value in list_alphabet])), reverse=True)

        list_alphabet_temp_ascii = []
        list_alphabet_temp_other = []
        list_alphabet_final = []

        for value_frequency in list_frequency_values:
            list_alphabet_temp_ascii = sorted(
                [element[0] for element in list_alphabet if element[1] == value_frequency and type(element[0]) == str],
                key=ord, reverse=True)
            list_alphabet_temp_other = [element[0] for element in list_alphabet if
                                        element[1] == value_frequency and not type(element[0]) == str]
            list_alphabet_temp_ascii = [(element, value_frequency) for element in list_alphabet_temp_ascii]
            list_alphabet_temp_other = [(element, value_frequency) for element in list_alphabet_temp_other]
            list_alphabet_final += list_alphabet_temp_ascii
            list_alphabet_final += list_alphabet_temp_other

        return list_alphabet_final

    def binary_list(self):
        alphabet = self.sorted_alphabet()
        while len(alphabet) > 2:
            # take the two smaller ones (divide the alphabet in half)
            first_part, second_part = alphabet[:-2], alphabet[-2:]
            # create new node
            if len(alphabet) == 2:
                new_node = (second_part, 0)
            else:
                new_node = (second_part, second_part[0][1] + second_part[1][1])
            # add it to the alphabet
            first_part.append(new_node)
            # sort the alphabet
            alphabet = self.sorted_alphabet(first_part)

        # return the dag
        return alphabet

    def binary_alphabet(self, binary_list=None, binary_dict=None, binary_code=''):
        if binary_list is None:
            binary_list = self.binary_list()
        if binary_dict is None:
            binary_dict = dict()

        for element in binary_list:
            binary_code_init = binary_code
            # if it's str
            if not type(element) == int:
                # if it's not a leaf
                if type(element[1]) == int:
                    binary_value_to_add = str(binary_list.index(element))
                    binary_value_to_add = '1' if binary_value_to_add == '0' else '0'
                else:
                    binary_value_to_add = ''
                # if it's a leaf
                if type(element[0]) == str:
                    # add value to the dict
                    binary_dict[element[0]] = (binary_code_init + binary_value_to_add)  # [::-1]
                # if it's not a leaf
                else:
                    self.binary_alphabet(element, binary_dict, binary_code_init + binary_value_to_add)

        return binary_dict

    def encode_file_bin(self, destination=None):
        if destination is None:
            destination = self.current_directory + self.export_file

        binary_alphabet = self.binary_alphabet()
        binary_text = ''

        for letter in self.text:
            binary_text += binary_alphabet[letter]
        length_binary_text = len(binary_text)

        file = open(destination, "wb")

        index_begin = 0
        while index_begin + 9 <= length_binary_text:
            octet = binary_text[index_begin:index_begin + 8]
            index_begin += 8
            file.write(int(octet, 2).to_bytes(len(octet) // 8, byteorder='big'))
        octet = binary_text[index_begin:] + '0' * (8 - len(binary_text[index_begin:]))
        file.write(int(octet, 2).to_bytes(-(-len(octet) // 8), byteorder='big'))

        file.close()

    def export_binary_alphabet(self):
        dict_values = self.binary_alphabet()
        dict_to_list = list(zip(dict_values.keys(), dict_values.values()))
        destination = self.current_directory + '/encoded/' + self.file_name + '_bin.txt'

        file = open(destination, "w")

        # special characters are replaced
        for couple_dict in dict_to_list:
            if couple_dict[0] == '\n':
                c = '[enter]'
            elif couple_dict[0] == '\t':
                c = '[tab]'
            elif couple_dict[0] == ' ':
                c = '[space]'
            else :
                c = couple_dict[0]

            file.write(c + '\t' + couple_dict[1] + '\n')

        file.close()
        return self.export_file

    def export_freq_alphabet(self):
        list_values = self.sorted_alphabet()[::-1]
        destination = self.current_directory + '/encoded/' + self.file_name + '_freq.txt'

        file = open(destination, "w")

        file.write(str(len(list_values)) + '\n')
        for character, value in list_values:
            if character == '\n':
                character = '[enter]'
            elif character == '\t':
                character = '[tab]'
            elif character == ' ':
                character = '[space]'

            file.write(character + '\t' + str(value) + '\n')

        file.close()

    def import_binary_alphabet(self, file_path):
        dictionary = {}
        with open(file_path, "r") as file:
            for line in file:
                key, value = line.strip().split('\t')
                print('INI KEY ',key,value)
                if key == '[enter]':
                    key = '\n'
                elif key == '[tab]':
                    key = '\t'
                elif key == '[space]':
                    key = ' '
                dictionary[key] = value
        print('INI DICT ',dictionary)
        return dictionary

    def decode(self, encoded_file=None, destination=None):  
        if destination is None:
            destination = os.path.dirname(os.path.abspath(__file__)).replace('\\', '/') + '/encoded/decode.txt'

        if encoded_file is None:
            encoded_file = os.path.dirname(os.path.abspath(__file__)).replace('\\', '/') + self.export_file

        with open(encoded_file, "rb") as file:
            encoded_bytes = file.read()

        encoded_text = ''.join(['{:08b}'.format(byte) for byte in encoded_bytes])
        encoded_text, last_octet = encoded_text[:-32], encoded_text[-32:]

        process_filename = lambda x: x.replace("_comp_comp", "").replace(".", "_")

        with open(destination, "w") as file:
            dictionary = self.import_binary_alphabet(self.current_directory +process_filename(self.export_file)+'.txt')
            dictionary = dict(zip(dictionary.values(), dictionary.keys()))

            print(dictionary)
            octet_found = False
            while not octet_found:
                value = last_octet
                while value:
                    if value in dictionary:
                        octet_found = True
                        break
                    value = value[1:]
                if not last_octet or octet_found:
                    break
                last_octet = last_octet[:-1]
            encoded_text += last_octet
            print('TOLD')
            print('INII DICT 2 2 ',dictionary)
            print('INII ENCODED ',encoded_text)

            encoded_text = encoded_text[:-4]
            while encoded_text:
                for key in dictionary:
                    if encoded_text.startswith(key):
                        print('write',dictionary[key],key)
                        file.write(dictionary[key])
                        encoded_text = encoded_text[len(key):]
                        break
                else:
                    print("Finally finished!")
                    break
                # print(encoded_text)
            print('INI MASOKZ')

@app.route('/')
def index():
    encoded_file = None
    decoded_file = None
    if 'encoded_file' in request.args:
        encoded_file = request.args['encoded_file']
    if 'decoded_file' in request.args:
        decoded_file = request.args['decoded_file']

    return render_template('index.html',encoded_file=encoded_file,decoded_file=decoded_file)

@app.route('/encode', methods=['POST'])
def encode():
    if 'file' not in request.files:
        return 'No file part'
    file = request.files['file']
    # Pastikan file yang diterima tidak kosong
    if file.filename == '':
        return 'No selected file'

    # Disimpan dalam direktori tempat file diunggah
    file.save(os.path.join('uploads/', file.filename))

    path = os.path.dirname(os.path.abspath(__file__)).replace('\\', '/')

    encoding = HuffmanCoding(path,'/uploads/'+file.filename)
    encoding.encode_file_bin()
    namefile = encoding.export_binary_alphabet()
    encoding.export_freq_alphabet()
    encoding.binary_alphabet()
    return redirect(url_for('index',encoded_file=namefile))


@app.route('/decode', methods=['POST'])
def decode():
    if 'file' not in request.files:
        return 'No file part'
    file = request.files['file']
    if file.filename == '':
        return 'No selected file'

    file.save(os.path.join('uploads/', file.filename))

    path = os.path.dirname(os.path.abspath(__file__)).replace('\\', '/')

    encoding = HuffmanCoding(path,'/encoded/'+file.filename)
    encoding.decode(encoded_file=path + '/encoded/'+file.filename)

    return redirect(url_for('index',decoded_file='decode.txt'))

@app.route('/download/<folder>/<filename>')
def download_file(folder,filename):
    return send_file(folder+'/'+filename, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)
