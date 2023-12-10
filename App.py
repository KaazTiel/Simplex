from flask import Flask, render_template, render_template_string, request
import os
import numpy as np
import warnings

warnings.filterwarnings("ignore", category=RuntimeWarning)

syst = ''
# selecionar a partir de quantas casas decimais o valor será arredondado
aux_round = 10 

if os.name == 'nt':
    syst = 'cls'
else:
    syst ='clear'


# DECLARAR
variaveis = []
restricoes = []
funcao_objetivo = {"tipo":None, "coef": []}

#----Variaveis
def add_variavel(descricao:str):
    global variaveis
    
    # ADICIONA NA LISTA DE VARIAVEIS
    variaveis.append(descricao)

    # ADICIONA UMA COLUNA DE ZEROS NA LISTA DE RESTRIÇÕES
    for linha in restricoes:
        linha["coef"].append(0)

def remover_variavel(var_index:int):
    global variaveis
    global restricoes
    global funcao_objetivo

    indice = var_index - 1

    if indice > len(variaveis):
        print('ERRO: indice nao existe')
        return
    # REMOVE DA LISTA DE VARIAVEIS
    variaveis.pop(indice)
    
    # REMOVE COEFICIENTES ASSOCIADOS NAS RESTRIÇÕES
    for linha in restricoes:
        linha["coef"].pop(indice)
    
    # REMOVE COEFICIENTE ASSOCIADO NA FUNÇÃO OBJETIVO
    funcao_objetivo['coef'].pop(indice)

def gerar_varFP() -> list:
    global variaveis
    global restricoes

    indice = len(variaveis) + 1
    lista_varFP = []

    for i in range(len(variaveis)):
        var = 'X_'+str(i+1)
        lista_varFP.append(var)

    for i in range(len(restricoes)):
        var = 'X_'+str(indice)
        indice+= 1
        lista_varFP.append(var)

    return lista_varFP

#----Restrições
def listar_coeficientes() -> list: # tambem funciona para FO
    global variaveis
    lista_coeficientes = []
    for i in range(len(variaveis)):
        try:
            coef = float(input(f'Coeficiente de X_{i + 1}: '))
        except:
            print('ERRO: valor nao numerico inserido >>> CANCELANDO...')
            return None
        lista_coeficientes.append(coef)

    return lista_coeficientes   
    


def definir_tipo() -> str:
    while(True):
        print('--SELECAO--')
        print('1. >')
        print('2. <')
        print('3. =')

        try:
            op = int(input('ESCOLHA: '))
        except:
            print('ERRO: valor não numérico inserio >>> TENTE NOVAMENTE...')
            continue

        if op == 1:
            return '>'
        elif op == 2:
            return '<'
        elif op == 3:
            return '='
        else:
            print('ERRO: Selecione um tipo válido')
            continue


def definir_Tindependente() -> float:
    try:
        termo_independente = float(input('Termo independente do segundo membro: '))
    except:
        print('ERRO: valor nao numerico inserido >>> CANCELANDO...')
        return None
    return termo_independente


def add_restricao(coeficientes:list, tipo:str, termo_independente:float):
    global variaveis
    global restricoes
    if len(coeficientes) != len(variaveis):
        print('ERRO: quantidade de coeficientes incompatível com número de variáveis')
        return
    restricoes.append({"tipo": tipo,
                       "coef":coeficientes,
                       "T_indep": termo_independente})
    

def remover_restricao(rest_index:int):
    indice = rest_index - 1
    if indice > len(restricoes):
        print('ERRO: indice nao existe')
        return
    restricoes.pop(indice)


def gerar_coeficientesFP(varFP:list) -> list:
    global restricoes
    global funcao_objetivo

    lista_coefsFP = []
    for linha in restricoes:
        lista_coefsFP.append(list(linha["coef"]))

    q_maior = 0
    precisa_artificial = []
    
    for aux, linha in enumerate(restricoes):
        for i in range(len(restricoes)):
            if i == aux:
                if linha["tipo"] == '<':
                    lista_coefsFP[i].append(1)
                elif linha["tipo"] == ">":
                    lista_coefsFP[i].append(-1)
                    q_maior +=1
                    precisa_artificial.append(aux)
                elif linha["tipo"] == '=':
                    if funcao_objetivo['tipo'] == 'Max':
                        lista_coefsFP[i].append(1)
                    elif funcao_objetivo['tipo'] == 'Min':
                        lista_coefsFP[i].append(-1)
                        q_maior +=1
                        precisa_artificial.append(aux)
                
            else:
                lista_coefsFP[i].append(0)
    
    for i in range(q_maior):
        id_rest = precisa_artificial[i]
        varArt_name = 'X_a'+str(i + 1)
        varFP.append(varArt_name)
        for aux, linha in enumerate(restricoes):
            if aux == id_rest:
                lista_coefsFP[aux].append(1)
            else:
                lista_coefsFP[aux].append(0)

    return lista_coefsFP

def gerar_equacoesFP(varFP:list, coefsFP:list) -> list:
    global variaveis
    global restricoes
    
    lista_esquacoes = []

    for i in range(len(restricoes)):
        linha = {"tipo": '=',
                "coef":coefsFP[i],
                "T_indep": restricoes[i]["T_indep"]}
        lista_esquacoes.append(linha)

    return lista_esquacoes
    

#----Função Objetivo

def definir_tipo() -> str:
    while(True):
        print('--SELECAO--')
        print('1. Max')
        print('2. Min')

        try:
            op = int(input('ESCOLHA: '))
        except:
            print('ERRO: valor não numérico inserio >>> TENTE NOVAMENTE...')
            continue

        if op == 1:
            return 'Max'
        elif op == 2:
            return 'Min'
        else:
            print('ERRO: Selecione um tipo válido')
            continue

def definir_fo(tipo:str, coeficientes:list):
    global variaveis
    global funcao_objetivo

    if len(coeficientes) != len(variaveis):
        print('ERRO: quantidade de coeficientes incompatível com número de variáveis')
        return

    funcao_objetivo["tipo"] = tipo
    funcao_objetivo["coef"] = coeficientes

def gerar_M() -> int:
    global restricoes
    global funcao_objetivo
    maior = None
    
    for linha in restricoes:
        for num in linha["coef"]:
            if maior == None:
                maior = num
            elif abs(num) > abs(maior):
                maior = num
        if abs(linha["T_indep"]) > abs(maior):
            maior = linha["T_indep"]
    for num in funcao_objetivo["coef"]:
        if abs(num) > abs(maior):
            maior = num
    
    bigM = abs(maior)*1000
    return bigM

def gerar_foFP(varFP:list) -> dict:
    global variaveis
    global restricoes
    global funcao_objetivo

    tamanho_var = len(variaveis)
    tamanho_rest = len(restricoes)
    dict_foFP = {"tipo":'Min', "coef": []}
    id_artificial = tamanho_var + tamanho_rest
    bigM = None
    
    aux_tipo = 1
    if funcao_objetivo["tipo"] == 'Max':
        aux_tipo = -1

    for i in range(tamanho_var):
        coeficiente = funcao_objetivo["coef"][i]
        dict_foFP["coef"].append((aux_tipo)*coeficiente)
    for i in range(tamanho_rest):
        dict_foFP["coef"].append(0)

    if len(varFP) > (tamanho_var + tamanho_rest):
        bigM = gerar_M()
        for i in range(id_artificial, len(varFP)):
            dict_foFP["coef"].append(bigM)

    return dict_foFP


# IMPRESSÃO

def imprimir_variaveis():
    global variaveis
    print('Variaveis de Decisao:')
    for indice, descricao in enumerate(variaveis):
        print(f"X_{indice + 1} -> {descricao}")
    print()

def imprimir_restricoes():
    global variaveis
    global restricoes

    print('Restricoes:')
    for rest_index, linha in enumerate(restricoes):
        print(f'R_{rest_index + 1} -> ', end="")
        for var_index, coeficiente in enumerate(linha["coef"]):
            print(f'({coeficiente})*X_{var_index + 1}', end="")
            if var_index < len(linha["coef"]) - 1:
                print(' + ', end="")
            else:
                print(" ", end="")
        print(linha["tipo"], end=" ")
        print(linha["T_indep"])
    print()

def imprimir_Fobjetivo():
    global variaveis
    global funcao_objetivo

    print('Funcao Objetivo:')
    print(funcao_objetivo["tipo"], end=" ")
    for var_index, coeficiente in enumerate(funcao_objetivo["coef"]):
        print(f'({coeficiente})*X_{var_index + 1}', end="")
        if var_index < len(funcao_objetivo["coef"]) - 1:
            print(' + ', end="")
        else:
            print()

    print()

def imprimir_sistema():

    imprimir_variaveis()
    imprimir_restricoes()
    imprimir_Fobjetivo()


# SIMPLEX
def gerar_Tableau() -> dict:
    lista_var = gerar_varFP()
    coefs = gerar_coeficientesFP(lista_var)
    lista_rest = gerar_equacoesFP(lista_var, coefs)
    fo = gerar_foFP(lista_var)

    dict_Tableau = {"var":lista_var,
                    "rest":lista_rest,
                    "fo":fo}
    return dict_Tableau

def buscar_coluna(varFP:list, restFP:list, foFP:dict, id_var:int) -> dict:
    dict_coluna = {"var": varFP[id_var],
                   "rest": None,
                   "fo": foFP["coef"][id_var]}
    lista_coef = []
    for linha in restFP:
        coef = linha["coef"][id_var]
        lista_coef.append(coef)
    dict_coluna['rest'] = lista_coef
    
    return dict_coluna

def eh_base(coluna:dict) -> bool:
    rest = list(coluna["rest"])
    fo = coluna["fo"]
    if rest.count(0) == len(rest) - 1 and rest.count(1) == 1 and fo == 0:
        return True
    else:
        return False

def artificiais_pBase(varFP:list, restFP:list, foFP:dict):
    global variaveis
    global restricoes
    tam_var = len(variaveis)
    tam_rest = len(restricoes)
    tam_varFP = len(varFP)
    q_notArtficial = tam_var + tam_rest
    q_Artificial = tam_varFP - q_notArtficial

    if q_Artificial == 0:
        return
    
    id_linhaList = []
    for i in range(q_Artificial):
        id_var = q_notArtficial + i
        col = buscar_coluna(varFP, restFP, foFP, id_var)
        for id_linha, coef in enumerate(col["rest"]):
            if coef == 1:
                id_linhaList.append(id_linha)
    aux_coef_FO = list(foFP["coef"])
    for i, id in enumerate(id_linhaList):
        id_var = q_notArtficial + i
        aux_multiplic = foFP["coef"][id_var] 
        aux_coef_FO = [a - (aux_multiplic)*b for a, b in zip(aux_coef_FO, restFP[id]["coef"])]
    foFP["coef"] = aux_coef_FO

# ->  x restrições = x variáveis na base
def listar_var_RB (varFP:list, restFP:list, foFP:dict) -> tuple:
    lista_R = []
    lista_B = []
    quant_var = len(varFP)

    for i in range(quant_var):
        col = buscar_coluna(varFP, restFP, foFP, i)
        if(eh_base(col)):
            lista_B.append(col["var"])
        else:
            lista_R.append(col["var"])

    return lista_R, lista_B

def listar_matrizes (varFP:list, restFP:list, foFP:dict) -> tuple:
    lista_varR, lista_varB = listar_var_RB(varFP, restFP, foFP)
    tam_varFP = len(varFP)
    tam_restFP = len(restFP)
    R = []
    B = []
    b = []
    cr = []
    cb = []

    for linha in restFP:
        b.append(linha["T_indep"])
        R.append([])
        B.append([])

    for variavel in varFP:
        id = varFP.index(variavel)

        if variavel in lista_varR:
            for i in range(tam_restFP):
                R[i].append(restFP[i]["coef"][id])
            cr.append(foFP["coef"][id])

        elif variavel in lista_varB:
            for i in range(tam_restFP):
                B[i].append(restFP[i]["coef"][id])
            cb.append(foFP["coef"][id])
    
    return R, B, b, cr, cb

def swap_varRB(varR_id:int, varB_id:int, lista_R:list, lista_B:list):
    aux = lista_R[varR_id]
    lista_R[varR_id] = lista_B[varB_id]
    lista_B[varB_id] = aux

def swap_coefRB(varR_id:int, varB_id:int, R:np.ndarray, B:np.ndarray):
    temporaria = np.copy(R[:, varR_id])
    R[:, varR_id] = B[:, varB_id]
    B[:, varB_id] = temporaria

def swap_foRB(varR_id:int, varB_id:int, R:np.ndarray, B:np.ndarray):
    temporaria = np.copy(R[varR_id])
    R[varR_id] = B[varB_id]
    B[varB_id] = temporaria

def gerar_matrizes(varFP:list, restFP:list, foFP:dict) -> tuple:    
    global variaveis
    global restricoes
    # tam_var = len(variaveis)
    # tam_rest = len(restricoes)
    # tam_varFP = len(varFP)

    lista_R, lista_B, lista_b, lista_cr, lista_cb = listar_matrizes(varFP, restFP, foFP)

    matR = np.array(lista_R)
    matB = np.array(lista_B)
    matb = np.array(lista_b).reshape(-1, 1)
    matcr = np.array(lista_cr)
    matcb = np.array(lista_cb)

    return matR, matB, matb, matcr, matcb

def eh_otima(cr:np.ndarray) -> bool:
    return np.all(cr > 0)

def buscar_idPivo(cr:np.ndarray):
    return np.argmin(cr)

def buscar_idForaB(R:np.ndarray, b:np.ndarray, id_pivo:int):
    coluna_pivo = R[:, id_pivo].reshape(-1, 1) 
    # print('b') [0.5] [10 ] -> 20
    # print(b)   [ 3 ] [12 ] -> 4
    # print('coluna_pivo')
    # print(coluna_pivo)

    divisao = b / coluna_pivo
    # print('divisao')
    # print(divisao)
    id_positivos = np.where(divisao > 0)[0]
    val_positivos = divisao[id_positivos]
    # if id_pivo == 2:
    #     print('val_positivos')
    #     print(val_positivos)

    if len(val_positivos.tolist()) == 0:
        return None

    id_menorVal = id_positivos[np.argmin(val_positivos)]
    
    return id_menorVal

def sort_B (var_B:list, B:np.ndarray) -> tuple:
    quant_varB = len(var_B)
    identidade = np.eye(quant_varB)

    list_sortB = [None for _ in range(quant_varB)]

    for i in range(quant_varB):
        for j in range(quant_varB):
            if np.array_equal(B[:, i], identidade[:, j]):
                list_sortB[j] = var_B[i]
                break
    return list_sortB

def listar_varInicial(varFP:list) -> list:
    global variaveis
    tam_varInicial = len(variaveis)
    lista_varInicial = []

    for i in range(tam_varInicial):
        lista_varInicial.append( varFP[i] )

    return lista_varInicial

def listar_varArtificial(varFP:list) -> list:
    global variaveis
    global restricoes

    q_var = len(varFP)
    q_notArt = len(variaveis) + len(restricoes)

    lista_Artificias = []

    for id in range(q_notArt, q_var):
        lista_Artificias.append( varFP[id] )

    return lista_Artificias

def eh_inviavel(varB:list, varFP:list) -> bool:
    artificiais = listar_varArtificial(varFP)

    for var in artificiais:
        if var in varB:
            return True
    return False

def eh_multiSol(cr:np.ndarray) -> bool:
    return np.any(cr == 0)

def val_varInicial(var_inicial:list, var_B:list, mat_b:np.ndarray) -> list:
    # retorna uma lista de tuplas (nome da variável inicial, valor associado)
    # caso a variável pertença a base, a função busca um valor associado em b
    # caso contrário, a função determina que o valor associado é igual a ZERO

    lista_valVar = []
    for var in var_inicial:
        if var in var_B:
            id = var_B.index(var)
            val_b = mat_b[id]
            # print(var, id, int(val_b))
            lista_valVar.append((var, round(val_b.item(), aux_round)))
        else:
            lista_valVar.append((var, 0))
    # print(lista_valVar)   
    return lista_valVar

def gerar_fo_noArt(foFP:dict) -> dict:
    global funcao_objetivo

    fo_noArt = {"tipo":"Min", "coef": []}

    for id in range(len(foFP["coef"])):
        if id in range(len(funcao_objetivo["coef"])):
            if funcao_objetivo["tipo"] == "Max":
                fo_noArt["coef"].append((-1)*funcao_objetivo["coef"][id])
            elif funcao_objetivo["tipo"] == "Min":
                fo_noArt["coef"].append(funcao_objetivo["coef"][id])
        else:
            fo_noArt["coef"].append(0)

    return fo_noArt

def simplex_revisado (varFP:list, restFP:list, foFP:dict) -> str: 
    global variaveis
    global funcao_objetivo

    fo_noArt = gerar_fo_noArt(foFP)

    matR, matB, b, cr, cb = gerar_matrizes(varFP, restFP, foFP)
    _, _, _, cr_noArt, cb_noArt = gerar_matrizes(varFP, restFP, fo_noArt)

    var_R, var_B = listar_var_RB(varFP, restFP, foFP)
    quant_varB = len(var_B)
    identidade = np.eye(quant_varB)
    # matriz_zeros = np.zeros(quant_varB)
    F_obj = 0
    lista_reconf = []

    var_iniciais = listar_varInicial(varFP)
    lista_solOtima = []

    var_B = sort_B(var_B, matB)
    # print('matB')
    # print(matB)
    # input()
    # print(var_B)
    matB = identidade.copy() # verificar depois
    
    reconfR = matR.copy()
    reconfB = matB.copy()
    reconfb = b.copy()
    reconfcr = cr.copy()
    reconfcb = cb.copy()
    reconfcr_noArt = cr_noArt.copy()
    reconfcb_noArt = cb_noArt.copy()

    guardar_cr = []

    frase = ''

    while not(eh_otima(reconfcr)):
        # print('reconfcr')
        # print(var_B)
        # print(reconfR)
        # print(reconfb)
        # print(reconfcr)
        if eh_multiSol(reconfcr):
            lista_solOtima.append(val_varInicial(var_iniciais, var_B, reconfb))
            id_zeros = np.where(reconfcr == 0)

            for id in id_zeros:
                id_pivo = id.item()
                id_forab = buscar_idForaB(reconfR, reconfb, id_pivo)
                tempR = matR.copy()
                tempB = matB.copy()
                tempb = b.copy()
                tempcr = cr.copy()
                tempcb = cb.copy()
                tempcr_noArt = cr_noArt.copy()
                tempcb_noArt = cb_noArt.copy()
                temp_varR = var_R.copy()
                temp_varB = var_B.copy()

                for i in range(len(lista_reconf)):
                    tmp_id_pivo = lista_reconf[i][0]
                    tmp_id_forab = lista_reconf[i][1]
                    swap_coefRB(tmp_id_pivo, tmp_id_forab, tempR, tempB)
                    swap_foRB(tmp_id_pivo, tmp_id_forab, tempcr, tempcb)
                    swap_foRB(tmp_id_pivo, tmp_id_forab, tempcr_noArt, tempcb_noArt)

                swap_varRB(id_pivo, id_forab, temp_varR, temp_varB)
                swap_coefRB(id_pivo, id_forab, tempR, tempB)
                swap_foRB(id_pivo, id_forab, tempcr, tempcb)
                swap_foRB(tmp_id_pivo, tmp_id_forab, tempcr_noArt, tempcb_noArt)

                inversa_tempB = np.linalg.inv(tempB)
                tempb = np.dot(inversa_tempB, tempb)

                lista_solOtima.append(val_varInicial(var_iniciais, temp_varB, tempb))
            
            break
            
        reconfR = matR.copy()
        reconfB = matB.copy()
        reconfb = b.copy()
        reconfcr = cr.copy()
        reconfcb = cb.copy()
        reconfcr_noArt = cr_noArt.copy()
        reconfcb_noArt = cb_noArt.copy()

        for i in range(len(lista_reconf)):
            id_pivo = lista_reconf[i][0]
            id_forab = lista_reconf[i][1]
            swap_coefRB(id_pivo, id_forab, reconfR, reconfB)
            swap_foRB(id_pivo, id_forab, reconfcr, reconfcb)
            swap_foRB(id_pivo, id_forab, reconfcr_noArt, reconfcb_noArt)

        # print(reconfB)
        inversa_B = np.linalg.inv(reconfB)

        # FO
        # parcial_fo1 = np.dot(reconfcb_noArt, inversa_B)
        # F_obj = np.dot(parcial_fo1, reconfb)
        # input()
        

        # CR
        parcial_cr1 = np.dot(reconfcb, inversa_B)
        parcial_cr2 = np.dot(parcial_cr1, reconfR)
        reconfcr = reconfcr - parcial_cr2

        # *b
        reconfb = np.dot(inversa_B, reconfb)

        # *R
        reconfR = np.dot(inversa_B, reconfR)
        
        if eh_multiSol(reconfcr):
            continue
        
        if eh_otima(reconfcr):
            break

        # print(reconfcr)
        id_pivo = buscar_idPivo(reconfcr)
        # print('id_pivo:', id_pivo)
        id_forab = buscar_idForaB(reconfR, reconfb, id_pivo)
        # print('id_forab:', id_forab)



        # TRATAMENTO PPL ILIMITADO
        if id_forab == None:
            print('> PPL Ilimitado:')
            print('Nenhuma variável sai da base')
            frase += 'PPL Ilimitado: '
            frase +='Nenhuma variável sai da base.'
            return frase

        lista_reconf.append((id_pivo, id_forab))
        # ---------------- ----------------
        guardar_cr.append(reconfcr.copy())
        # ---------------- ----------------
        swap_varRB(id_pivo, id_forab, var_R, var_B)

    # TRATAMENTO PPL INVIÁVEL
    if eh_inviavel(var_B, varFP):
        print('> PPL Inviável:')
        print('Variável artificial permaneceu na base')
        frase += 'PPL Inviável: '
        frase +='Variável artificial permaneceu na base.'
        return frase
    
    
    # print('reconfcr')
    # print(var_B)
    # print(reconfR)
    # print(reconfb)
    # print(reconfcr)
    # print(lista_reconf)
    reconfR = matR.copy()
    reconfB = matB.copy()
    reconfb = b.copy()
    reconfcr = cr.copy()
    reconfcb = cb.copy()
    reconfcr_noArt = cr_noArt.copy()
    reconfcb_noArt = cb_noArt.copy()

    for i in range(len(lista_reconf)):
        id_pivo = lista_reconf[i][0]
        id_forab = lista_reconf[i][1]
        swap_coefRB(id_pivo, id_forab, reconfR, reconfB)
        swap_foRB(id_pivo, id_forab, reconfcr, reconfcb)
        swap_foRB(id_pivo, id_forab, reconfcr_noArt, reconfcb_noArt)

    inversa_B = np.linalg.inv(reconfB)
    parcial_fo1 = np.dot(reconfcb_noArt, inversa_B)
    F_obj = np.dot(parcial_fo1, reconfb)

    # CR
    parcial_cr1 = np.dot(reconfcb, inversa_B)
    parcial_cr2 = np.dot(parcial_cr1, reconfR)
    reconfcr = reconfcr - parcial_cr2

    # *b
    reconfb = np.dot(inversa_B, reconfb)

    
    # TRATAMENTO PPL MULTIPLAS SOLUÇÕES
    if eh_multiSol(reconfcr):
        q_solOtima = len(lista_solOtima)
        print('> PPL com Multiplas Soluções:')
        print(f'Com fins de obter a solucao {funcao_objetivo["tipo"]}, onde FO= {abs(F_obj.item())}, podemos optar por')
        frase += 'PPL com Multiplas Soluções: '
        frase += 'Com fins de obter a solucao '+funcao_objetivo["tipo"]+', onde FO= '+str(abs(F_obj.item()))+', podemos optar por '
        for i in range(q_solOtima):
            frase += '{'
            for id, var in enumerate(var_iniciais):
                print(f'{var} = {lista_solOtima[i][id][1]}')
                frase += var +'= '+ str(lista_solOtima[i][id][1])
                if id < len(var_iniciais) - 2:
                    frase += ', '
                elif id == len(var_iniciais) - 2:
                    frase += ' e '
            frase += '}'
            if i != q_solOtima - 1:
                print('ou')
                frase += ' ou '
        return frase
    
    # TRATAMENTO PPL SOLUÇÃO ÚNICA
    else:
        print(var_iniciais)
        print('> PPL com Solução Única:')
        print(f'Com fins de obter a solucao {funcao_objetivo["tipo"]}, onde FO= {abs(F_obj.item())}, devemos optar por')
        frase += 'PPL com Solução Única: '
        frase += 'Com fins de obter a solucao '+funcao_objetivo["tipo"]+', onde FO= '+str(abs(F_obj.item()))+' devemos optar por {'
        solucao = val_varInicial(var_iniciais, var_B, reconfb)
        for id, var in enumerate(var_iniciais):
            print(f'{var} = {solucao[id][1]}')
            frase += var +'='+ str(solucao[id][1])
            if id < len(var_iniciais) - 2:
                frase += ', '
            elif id == len(var_iniciais) - 2:
                frase += ' e '
        frase += '}'
        return frase
    

# MAIN
def main():

    while(True):
        print('----MENU----')
        print('1. Visualizar Sistema')
        print('2. Inserir Variável')
        print('3. Inserir Restricao')
        print('4. Definir Funcao Objetivo')
        print('5.')
        print('\n0. SAIR')

        try:
            op = int(input('> Selecione a operacao: '))
        except:
            print('ERRO: Digite um valor numérico')
            continue

        if(op == 0):
            print('ENCERRANDO...')
            break
        elif(op ==1):
            pass
        elif(op ==2):
            pass
        elif(op ==3):
            pass
        elif(op ==4):
            pass
        elif(op ==5):
            pass


app = Flask(__name__)

# request.form.get('meuInput1')

@app.route('/', methods=['GET', 'POST'])
def index():
    global variaveis, restricoes, funcao_objetivo
    # frase = request.form.get('frase-rodape')
    # print('frase:')
    # print(frase)
    # if frase == None:
    #     frase = ''

    if request.method == 'POST':
        # frase = ''
        variaveis = []
        restricoes = []
        funcao_objetivo = {"tipo":None, "coef": []}

        q_var = request.form.get('colunas')
        q_var = int(q_var) # colunas
        q_rest = request.form.get('linhas')
        q_rest = int(q_rest) # linhas

        print('Q_VAR:', q_var)
        print('Q_REST:', q_rest)
        
        # ADD VARIAVEIS
        for i in range(q_var):
            nome = 'X_'+str(i+1)
            add_variavel(nome)

        # ADD RESTRIÇÕES
        for i in range(q_rest):
            linha = []
            for j in range(q_var):
                nome = 'valor_'+str(i)+'_'+str(j)
                valor = request.form.get(nome)
                valor = float(valor)
                linha.append(valor)
            tipo = request.form.get('tipo_'+str(i))
            # print(tipo)
            t_indep = request.form.get('valor_'+str(i)+'_'+str(q_var))
            t_indep = float(t_indep)
            add_restricao(linha, tipo, t_indep)

        # ADD FUNÇÃO OBJETIVO
        linha_fo = []
        for i in range(q_var):
            valor = request.form.get('valor_'+str(q_rest)+'_'+str(i))
            valor = float(valor)
            linha_fo.append(valor)
        tipo_fo = request.form.get('tipo_fo')
        definir_fo(tipo_fo, linha_fo)


        imprimir_sistema()

        # FORMA PADRÃO + ARTIFICIAIS
        varFP = gerar_varFP()
        coefFP = gerar_coeficientesFP(varFP)
        eqFP = gerar_equacoesFP(varFP, coefFP)
        foFP = gerar_foFP(varFP)

        # ENVIAR AS ARTIFICIAIS PRA BASE
        artificiais_pBase(varFP, eqFP, foFP)

        # CALCULAR SIMPLEX
        try:
            frase = simplex_revisado(varFP, eqFP, foFP)
        except Exception as erro:
            frase = 'ERRO: '+ str(erro)
        # print('FRASE:')
        # print(frase)

        print('frase_rodape:', frase)
        # print(render_template_string('{{ frase_rodape }}', frase_rodape = frase))
        return render_template_string('{{ frase_rodape }}', frase_rodape = frase)
        

    # print('frase_rodape:', frase)
    return render_template('index.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
