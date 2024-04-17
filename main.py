import re


class GLC:
    def __init__(self):
        self.variaveis = {}
        self.inicial = ''
        self.terminais = {}
        self.producoes = []


def read_glc_from_file(path: str):
    with open(path, "r", encoding="utf-8") as arquivo:
        gramatica = arquivo.read()

    gramatica = gramatica.split("\n")

    mid = False
    conjuntos = []
    producoes = []
    for line in gramatica:
        if line == '':
            mid = True
            continue
        if not mid:
            conjuntos.append(line)
        if mid:
            producoes.append(line)
    gramatica_glc = GLC()
    for line in conjuntos:
        chave = line.split(":")
        valores = chave[1].split(",")
        if re.match("variaveis", chave[0]):
            gramatica_glc.variaveis = {chave[0]: valores}
        elif re.match("terminais", chave[0]):
            gramatica_glc.terminais = {chave[0]: valores}
        elif re.match("inicial", chave[0]):
            gramatica_glc.inicial = {chave[0]: valores}
    gramatica_glc.producoes = producoes[1:]
    return gramatica_glc


glc = read_glc_from_file("gramatica_generica.txt")
print(glc.variaveis)
print(glc.inicial)
print(glc.terminais)
print(glc.producoes)

for producao in glc.producoes:
    if "A" in producao[0]:
        print(producao)
