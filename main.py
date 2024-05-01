import re


class GLC:
    def __init__(self):
        self.variaveis = {}
        self.inicial = ''
        self.terminais = {}
        self.producoes = []


# Função que verifica se a gramatica forneceida é valida


# função que ler o arquivo que contem a gramatica
def read_glc_from_file(path: str):
    try:
        with open(path, "r", encoding="utf-8") as arquivo:
            gramatica = arquivo.read()
    except OSError:
        print("Houve um error inesperao ao ler o arquivo por favor tente novamente!")
        return False

    try:
        # separa a string do arquivo em um array onde cada elemento representa uma linha
        gramatica = gramatica.split("\n")

        # como no formato do arquivo possui uma linha em branco separando o conjunto das produções:
        # aqui se separa os conjuntos de variavies terminais e simbolo inicial das produções:
        mid = False
        conjuntos = []
        producoes = []
        for line in gramatica:
            if line == '' and mid:
                print("arquivo em formato inesperado!")
                return False
            if line == '':
                mid = True
                continue
            if not mid:
                conjuntos.append(line)
                continue
            if mid:
                producoes.append(line)
                continue

        gramatica = GLC()
        # Organiza cada string em dicionarios que representam cada conjunto:
        for line in conjuntos:
            chave = line.split(":")
            valores = chave[1].split(",")
            if re.match("variaveis", chave[0]):
                gramatica.variaveis = {chave[0]: valores}
            elif re.match("terminais", chave[0]):
                gramatica.terminais = {chave[0]: valores}
            elif re.match("inicial", chave[0]):
                gramatica.inicial = {chave[0]: valores}
            else:
                print("arquivo com formato inesperado!")
                return False
        # Organiza todas as produções da gramatia em um array
        gramatica.producoes = producoes[1:]

        # verifica o formato da gramatica
        if not verifica_gramatica(gramatica):
            print("Os dados no arquivo não representam uma gramatica livre de contexto valida!")
            return False
        return gramatica
    except Exception:
        print("Erro inesperado no formato do arquivo!")
        return False


def verifica_gramatica(gramatica: GLC):
    # caso o inicial não esteja no conjunto de variaveis:
    if gramatica.inicial['inicial'][0] not in gramatica.variaveis['variaveis']:
        return False
    # verficicando as produções
    for producao in gramatica.producoes:
        p = producao.split(":")
        if len(p) > 2:  # formato inesperado
            return False
        # caso possua mais de uma variavel do lado esquerdo da produção
        # Ou caso esse simbolo não esteja indicado no conjunto de variaveis
        if len(p[0]) > 1 or p[0] not in gramatica.variaveis['variaveis']:
            return False
        # verificando se o simbolo é uma variavel valida um não terminal valido
        # Ou o 'epsilon'
        p = str(p[1]).split()  # retirando o espaço em branco que tem na espcificação para verificar
        # verifiando se as substituições estão no formato esperado
        for i in range(0, len(p)):
            if re.match('epsilon', p[i]):
                continue
            for simbolo in p[i]:
                if simbolo not in gramatica.variaveis['variaveis'] and simbolo not in gramatica.terminais['terminais']:
                    return False

    return True


def fast_mode(garamticaglc: GLC):
    # criando a cadeia inicial
    cadeia_atual = garamticaglc.inicial['inicial'][0]
    productions = [garamticaglc.inicial['inicial'][0]]
    # chama um metodo que gera codecs recursivamente:
    generete_recursivo(cadeia_atual, garamticaglc, productions, '')


def generete_recursivo(cadeia: str, gramatica: GLC, productions: list, deriv: str):
    # encontrando o index do elemento que sera substituido
    index = find_the_most_left_no_terminal(cadeia, gramatica.variaveis)

    # Criando uma lista com todas as produções possiveis da variavel atual
    list_of_producions = []
    for producao in gramatica.producoes:
        if re.match(producao[0], cadeia[index]):
            list_of_producions.append(producao.split(":")[1].strip())

    # organizando as produções de forma que ele substitua epsilon sempre que possivel
    # e que caso haja uma produção sem variaveis ( ou seja uma produção so com  finais) ela tenha prioridade
    if 'epsilon' in list_of_producions:
        list_of_producions.remove('epsilon')
        # organizando as produções de forma que aquelas so com não terminais tenham prioridade
        # para evitar loops infinitos
        for producao in list_of_producions:
            b = False
            for variavel in gramatica.variaveis['variaveis']:
                if variavel in producao:
                    b = True
            if not b:
                aux = producao
                list_of_producions.remove(producao)
                list_of_producions.insert(0, aux)
        list_of_producions.insert(0, 'epsilon')
    else:
        for producao in list_of_producions:
            b = False
            for variavel in gramatica.variaveis['variaveis']:
                if variavel in producao:
                    b = True
            if not b:
                aux = producao
                list_of_producions.remove(producao)
                list_of_producions.insert(0, aux)

    # fazendo substituições recursivas até ter uma cadeia valida
    if index != -1:
        for element in list_of_producions:
            # guardando as produções escolhidas para mostrar as derivações
            # substituindo o não terminal mais a esquerda pela produção
            cadeia_nova = replace_once(cadeia, cadeia[index], element)
            productions.append(cadeia_nova)

            if not cadeia_nova == '':
                cadeia_final = generete_recursivo(cadeia_nova, gramatica, productions, deriv)
                # verificando casos de parada
                if cadeia_final is None:
                    productions.pop()
                    continue
                if cadeia_final == 0:
                    productions.pop()
                    return 0
            # caso onde ele subistitui s por epsilon de primeira
            else:
                cadeia_final = ''

            p = ''
            for i in range(0, len(productions)):
                p += f" {productions[i]}"
                if i < len(productions) -1 :
                    p += " ->"

            print(f'{cadeia_final} -- Derivações: {p}')
            productions.pop()
            # Mostrando as derivaçõe feitas e a cadeia final


            # perguntando se o ususario quer continuar:
            try:
                choice = int(input("Digite [1] para continuar e [0] para parar: "))
            except ValueError:
                print("Valor invalido!")
                return 0
            while choice != 1 and choice != 0:
                choice = int(input("Numero invalido digite novamente: "))
            if choice == 0:
                return 0

    # retornando cadeia sem variaveis:
    else:
        return cadeia



def detail_mode(gramatia: GLC):
    cadeia_atual = str(gramatia.inicial['inicial'][0])
    most_left_no_terminal_index = find_the_most_left_no_terminal(cadeia_atual, gramatia.variaveis)
    s = f'{cadeia_atual} ->'
    while most_left_no_terminal_index != -1:
        count = 1
        print("Digite o Numero da produção que você deseja usar: ")
        productions = []
        for line in gramatia.producoes:
            if re.match(line[0], cadeia_atual[most_left_no_terminal_index]):
                productions.append(line)
                print(f'[{count}] {line}  ', end=' ')
                count += 1
        print()
        try:
            number_of_production = int(input("Number: "))
        except ValueError:
            print("Valor invalido!")
            continue
        cadeia_atual = replace_once(cadeia_atual, cadeia_atual[most_left_no_terminal_index],
                                    str(productions[number_of_production - 1]).split(":")[1].strip())

        s += f' {cadeia_atual}'
        print("\n ----------------------------------")
        print(s)
        most_left_no_terminal_index = find_the_most_left_no_terminal(cadeia_atual, gramatia.variaveis)
        s += '->'

    print("------------------------------------")
    return True


def find_the_most_left_no_terminal(cadeia: str, variables: dict):
    for element in cadeia:
        if element in variables['variaveis']:
            return cadeia.index(element)
    # quando ela não possuir mais não terminais
    return -1


def replace_once(s, old_char, new_char):
    index = s.find(old_char)
    if index != -1:
        if re.match("epsilon", new_char):
            return s[:index] + '' + s[index + 1:]
        return s[:index] + new_char + s[index + 1:]
    return s


# funcionamento do programa e interação com o usuario
in_execution = True
while in_execution:
    path_to_glc = str(input("Digite o caminho para a gramatica (digite exit para encerrar): "))
    # caso o usuario digite para sair.
    if re.match("exit", path_to_glc):
        in_execution = False
        continue
    gramatica_glc = read_glc_from_file(path_to_glc)
    if not gramatica_glc:  # caso o caminho seja invalido
        continue

    print("Escolha o Modo de funcionamento: ")
    try:
        modo_de_funcionamento = int(input("[1] Modo rapido\n[2] Modo detalhado\n-: "))
    except ValueError:
        print("Valor invalido!")
        continue
    while modo_de_funcionamento < 1 or modo_de_funcionamento > 2:
        modo_de_funcionamento = int(input("Por favor digite um valor valido: "))
    if modo_de_funcionamento == 1:
        fast_mode(gramatica_glc)
    else:
        detail_mode(gramatica_glc)
