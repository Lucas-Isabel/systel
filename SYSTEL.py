import os
import time
import os.path
import psycopg2
import datetime
import shutil


def caracter_remove(txt):
    texto = txt.replace("\n", "").replace("    ", "").replace(", ", ",").replace(" (", "(")
    return texto


def tare_analyze(arq):
    tara_txt = open(arq, 'r')
    dict_tara = {}
    for line in tara_txt:
        cod = line[0:4]
        valor =  line[18:22]
        try:
            valor = float(valor)/1000
            dict_tara[cod] = valor
            #print(cod, valor)
        except:
            msg_erro = "Erro ao importar informações de: " + arq
            print(msg_erro)
    return dict_tara
        

def conserva_analyze(arq):
    conserva_txt = open(arq, 'r')
    dict_conserva = {}
    for line in conserva_txt:
        #dict_conserva[line[0:4]] = (line[4:194].replace('\n', '')).replace("    ", "")
        dict_conserva[line[0:4]] =  caracter_remove(line[104:194]) if line[0:4] != '0003' else caracter_remove(line[4:40])

    conserva_txt.close()
    return dict_conserva

def fraciona_analyze(arq):
    fraciona_txt = open(arq, 'r')
    dict_fraciona = {}
    for line in fraciona_txt:
        #dict_fraciona[line[0:4]] = (line[104:217].replace('\n', '')).replace("    ", "")
        dict_fraciona[line[0:4]] = caracter_remove(line[104:])
    fraciona_txt.close()
    return dict_fraciona

def alergia_analyze(arq):
    camp_txt = open(arq, 'r')
    dict_aler = {}
    for line in camp_txt:
        #dict_aler[line[0:4]] = caracter_remove(line[104:272].replace('\n', '')).replace("    ", "")
        dict_aler[line[0:4]] = caracter_remove(line[104:])
    camp_txt.close()
    return dict_aler

def forn_analyze(arq):
    forn_txt = open(arq, 'r')
    dict_fornecedor = {}
    for line in forn_txt:

        dict_fornecedor[line[0:4]] = caracter_remove(line[104:217])
    forn_txt.close()
    return dict_fornecedor


def info_analyze(arq):
    info_txt = open(arq, 'r')
    dict_info = {}
    for line in info_txt:

        dict_info[line[0:6]] = caracter_remove(line[106:])
    info_txt.close()
    return dict_info

def conectar_banco(ip):
    try:
        if ip == 'localhost':
            conn = psycopg2.connect(
                dbname="cuora",
                user="postgres",
                password="postgres",
                host="localhost",
                port="5432"
            )
            return conn
        else:
            conn = psycopg2.connect(
            dbname="cuora",
            user="user",
            password="1234",
            host=ip,
            port="5432"    
            )
            return conn    
    except psycopg2.Error as e:
        print("Erro ao conectar ao banco de dados:", e)
        return None

def infoSystel_writer(arq, d_info, d_forn, d_aler, d_fra, d_con, d_tara,ip):
    item = open(arq, 'r')

    if True:
        passw = '1234'
        user = 'user'
        if ip == 'localhost':
            passw = 'postgres'
            user = 'postgres'
        
        if True:
            #db_acess = f'pq://{user}:{passw}@{ip}:5432/cuora'
            db = conectar_banco(ip)
            for line in item:
                lote = line[90:102]
                cod_plu = line[3:9]
                cod_info = line[68:74]
                cod_aler = line[126:130]
                cod_forn = line[86:90]
                cod_frac = line[122:126]
                cod_cons = line[134:138]
                cod_tara = line[118:122]
                venda = line[2:3]

                    

                espaco =  (' '*1)
                if cod_tara != '0000' and venda != '1':
                    tara = d_tara[cod_tara] if cod_tara in d_tara else " "
                else: tara = " "
                
                info = d_info[cod_info]  if cod_info in d_info else " "
                aler = d_aler[cod_aler] if cod_aler in d_aler else " "
                forn = d_forn[cod_forn] if cod_forn in d_forn else " "
                cons = d_con[cod_cons] if cod_cons in d_con else " "
                frac = d_fra[cod_frac] if cod_frac in d_fra else " "

                if len(forn) < 158 and forn != " ":
                    forn = forn + ' '*(158- len(forn))

                
                forn_frac = forn + ' ' + frac

                lote = int(lote)

                if not(tara ==  " "):
                    enviar_inf(d_tara[cod_tara], cod_plu, db, 'tare')
                    #print('enviado: ', d_tara[cod_tara], ' para ', cod_plu, 'no campo tare')
                if lote > 0:
                    enviar_inf(str(lote), cod_plu, db, 'lot')
                if not(info ==  " "):
                    enviar_inf(d_info[cod_info], cod_plu, db, 'extra_field1')
                if not(aler ==  " "):
                    enviar_inf(d_aler[cod_aler], cod_plu, db, 'extra_field2')
                if not(cons ==  " "):
                    enviar_inf(d_con[cod_cons], cod_plu, db, 'preservation_info')
                if not(forn ==  " " and frac ==  " "):
                    enviar_inf(forn_frac, cod_plu, db, 'ingredients')

            db.close()
            #print(ip)
        

    #print('hm')
    item.close()


def itens_analize(arq):
    arquivoItensMgv = open(arq, 'r')
    arquivoMGV7 = open('../itens.TXT', 'w')
    for l in arquivoItensMgv:
        if len(l) < 60:
            textoModificado = l.replace("\n", " ")

        else: 
            textoModificado = l

        arquivoMGV7.write(textoModificado)

    arquivoItensMgv.close()
    arquivoMGV7.close()


#DB

def enviar_inf(t, p, db, campo):
    #if p == "005003": print('Aqui: ', t)
    plu = p
    tara = t
    cur = db.cursor()
    try:
        cur.execute("UPDATE product SET {} = %s WHERE product_id = %s".format(campo), (tara, plu))
        db.commit()
    except psycopg2.Error as e:
        print(e)


def file_ports_ex():
    try:
        teste = open('porta.txt', 'r')
        teste.close()
        return open('porta.txt', 'r')
    except:
        try:
            teste2 = open('porta.txt', 'r')
            teste2.close()
            return open('porta.txt', 'r')
        except:
            teste3 = open('porta.txt', 'w')
            teste3.close()
            return open('porta.txt', 'r')





def setorWrite():
    arquivo = 'setor.txt'
    dict_setor = {}
    setor_array = []
    if not (os.path.isfile(arquivo)):
        with open(arquivo, 'w') as setor_file:
            for i in range(1, 13):
                setor = str(i)
                if len(setor) < 2: setor = '0' + setor
                setor_array.append(setor)
                nome = ""
                match setor:
                    case '01':
                        nome = "GERAL"
                        dict_setor[setor] = nome
                        linha = f'{setor}{nome}\n'
                        setor_file.write(linha)
                    case '02':
                        nome = "HORTIFRUTI"
                        dict_setor[setor] = nome
                        linha = f'{setor}{nome}\n'
                        setor_file.write(linha)
                    case '03':
                        nome = "PADARIA"
                        dict_setor[setor] = nome
                        linha = f'{setor}{nome}\n'
                        setor_file.write(linha)
                    case '04':
                        nome = "AÇOGUE"
                        dict_setor[setor] = nome
                        linha = f'{setor}{nome}\n'
                        setor_file.write(linha)
                    case '05':
                        nome = "FRIOS"
                        dict_setor[setor] = nome
                        linha = f'{setor}{nome}\n'
                        setor_file.write(linha)
                    case '06':
                        nome = "PREPARAÇÃO"
                        dict_setor[setor] = nome
                        linha = f'{setor}{nome}\n'
                        setor_file.write(linha)
                    case '07':
                        nome = "NOBRE"
                        dict_setor[setor] = nome
                        linha = f'{setor}{nome}\n'
                        setor_file.write(linha)
                    case '08':
                        nome = "HORTIFRUTI"
                        dict_setor[setor] = nome
                        linha = f'{setor}{nome}\n'
                        setor_file.write(linha)
                    case '09':
                        nome = "GERAL 09"
                        dict_setor[setor] = nome
                        linha = f'{setor}{nome}\n'
                        setor_file.write(linha)
                    case '10':
                        nome = "GERAL 10"
                        dict_setor[setor] = nome
                        linha = f'{setor}{nome}\n'
                        setor_file.write(linha)
                    case '11':
                        nome = "GERAL 11"
                        dict_setor[setor] = nome
                        linha = f'{setor}{nome}\n'
                        setor_file.write(linha)
                    case '12':
                        nome = "GERAL 12"
                        dict_setor[setor] = nome
                        linha = f'{setor}{nome}\n'
                        setor_file.write(linha)
                        
    else:
        with open(arquivo, 'r') as setor_file:
            for line in setor_file:
                try:
                    setor = line[0:2]
                    setor_array.append(setor)
                    nome = line[2:].replace('\n', '')
                    dict_setor[setor] = nome
                except: pass

    dict_plu = {}
    array_setor = []
    print(setor_array)
    folder = 'setores'
    if not os.path.exists(folder):
        os.makedirs(folder)

    systel = open('itensSystel.TXT', 'r')
    for line in systel:
        setor_plu = line[0:2]
        if not setor_plu in array_setor:
            array_setor.append(setor_plu)
        if setor_plu in dict_plu:
            dict_plu[setor_plu].append(line)
        else: dict_plu[setor_plu] = [line]
    for s in array_setor:
        if s in setor_array:
            name_file = f'{folder}/{dict_setor[s]}.txt'
            arquivo_nomeado = open(name_file, 'w')
            for item in dict_plu[s]:
                arquivo_nomeado.write(item)
            arquivo_nomeado.close()
        else:
            name_file = f'{folder}/GERAL {s}.txt'
            arquivo_nomeado = open(name_file, 'w')
            for item in dict_plu[s]:
                arquivo_nomeado.write(item)
            arquivo_nomeado.close()
    systel.close()

    nutri = 'nutriSystel.txt'
    nutri_setor = f'{folder}/nutriSystel.txt'

    shutil.copyfile(nutri, nutri_setor)         





def comunicabal():
    array = []
    porta = file_ports_ex()
    for line in porta:
        ip = str(line)
        ip = ip.replace('\n', '')
        if ip != '' and ip != '-1':
            array.append(ip)
    porta.close()
    return array
                
                



def main():
    start()
    data_criacao = ""
    data_atualizacao = ""

    data_criacao_portas = ""
    data_atualizacao_portas = ""
    while(True):
        
        arquivo = '../itensmgv.txt' if not (os.path.isfile('../itensmgv.bak')) else '../itensmgv.bak'
        arquivo_portas = 'porta.txt'

        if(os.path.isfile(arquivo)):
            time.sleep(1)
            data_atualizacao_timestamp = os.path.getmtime(arquivo)
            data_atualizacao = str(datetime.datetime.fromtimestamp(data_atualizacao_timestamp))
            #print(data_atualizacao)

            if(os.path.isfile(arquivo_portas)):
                time.sleep(1)
                data_atualizacao_timestamp = os.path.getmtime(arquivo_portas)
                data_atualizacao = str(datetime.datetime.fromtimestamp(data_atualizacao_timestamp))
            
            if data_criacao != data_atualizacao or data_criacao_portas != data_atualizacao_portas:
                data_criacao = data_atualizacao
                data_criacao_portas = data_atualizacao_portas

                if(os.path.isfile('../tara.bak')):
                    dict_tara = tare_analyze('../tara.bak')
                elif(os.path.isfile('../tara.txt')):
                    dict_tara = tare_analyze('../tara.txt')
                else: dict_tara = {}

                
                if(os.path.isfile('../conserva.bak')):
                    dict_conserva = conserva_analyze('../conserva.bak')
                
                elif(os.path.isfile('../conserva.txt')):
                    dict_conserva = conserva_analyze('../conserva.txt')
                else: dict_conserva = ''

                if(os.path.isfile('../fraciona.bak')):
                    dict_fraciona = fraciona_analyze('../fraciona.bak')
                elif(os.path.isfile('../fraciona.txt')):
                    dict_fraciona = fraciona_analyze('../fraciona.txt')
                else: dict_fraciona = ''

                if(os.path.isfile('../campext1.bak')):
                    dict_aler = alergia_analyze('../campext1.bak')
                elif(os.path.isfile('../campext1.txt')):
                    dict_aler = alergia_analyze('../campext1.txt')
                else: dict_aler = ''

                if(os.path.isfile('../txforn.bak')):
                    dict_forn =  forn_analyze('../txforn.bak')
                elif(os.path.isfile('../txforn.txt')):
                    dict_forn =  forn_analyze('../txforn.txt')
                else:
                    dict_forn = '' 
                
                if(os.path.isfile('../txinfo.bak')):
                    info = info_analyze('../txinfo.bak')
                elif(os.path.isfile('../txinfo.txt')):
                    info = info_analyze('../txinfo.txt')
                else:
                    info = ""
                    pass

                if(os.path.isfile('../infnutri.txt')):
                    arquivoInfonutri = '../infnutri.txt'
                elif(os.path.isfile('../infnutri.bak')):
                    arquivoInfonutri = '../infnutri.bak'
                else:
                    arquivoInfonutri = open('../infnutri.bak', 'w')
                    arquivoInfonutri.close()
                    arquivoInfonutri = '../infnutri.bak'
                
                arquivoInfonutri = open(arquivoInfonutri)
                
                itens_analize(arquivo)


                arquivoMGV7 = open('../itens.TXT', 'r')

                nutri = open('nutriSystel.TXT', 'w')
                codPlu_array = []
                codNutri_array = []
                codNutriMGVARRAY = []
                receita_array = []
                setor_array = []
                arquivoSystel = open('itensSystel.TXT', 'w')
                for linha in arquivoMGV7:
                
                    

                    codPlu = linha[3:9]
                    
                    codPlu_array.append(codPlu)
                    codNutriMGV = linha[79:84]
                    codReceita = linha[68:74]
                    receita_array.append(codReceita)

                    codNutriMGVARRAY.append(int(codNutriMGV))
                    textoModificado = linha[0:43] + (' ')*25 + linha[68:150] +  "000000|01|                                                                      0000000000000000000000000||0||0000000000000000000000"

                    arquivoSystel.write(textoModificado+"\n")

                arquivoSystel.close()



                
                array_cod_nutri = []


                


                for linha in arquivoInfonutri:
                    codNutri = int(linha[1:7])

                    boo = linha[7:110] != '000000000000000000000000000000000000000000|000000000000000000000000000000000000000000000000000000000000'
                    #print(boo)
                    if len(linha) < 50:
                        #print(linha[7:11])
                        linha = linha[0:49].replace('\n', '') 
                        linha = linha + '|' + ('0'*3)
                        porcao = linha[7:11] if int(linha[7:11]) > 0 else '0100'
                        #print(porcao, int(linha[7:11]))
                        linha = linha + porcao
                        linha = linha + '0' + linha[12:26] 
                        linha = linha + '0'*6 + linha[26:50].replace('\n','') 
                        linha = linha + '0'*9 + '\n'
                    else:
                        linha = linha.replace('|', '0000|')
                    if int(linha[61:63]) > 28:
                        #print(linha[61:63])
                        linha = linha[:61] + '16' + linha[63:]
                    if codNutri in codNutriMGVARRAY and not(codNutri in array_cod_nutri) and boo:
                        array_cod_nutri.append(codNutri)
                        #if codNutri == 5:
                            ##print("teste")
                        #print(codNutri, codNutriMGVARRAY)
                        nutri.write(linha)
                        codNutri_array.append(codNutri)
                    #print("1")
                arquivoMGV7.close()
                arquivoInfonutri.close()
                nutri.close()
                arquivoSystel.close()

                setorWrite()


                arr_ip = comunicabal()
                if not 'localhost' in arr_ip:
                    arr_ip.append('localhost')
                if len(arr_ip) > 0:
                    txt = ''
                    for ip in arr_ip:
                        #ip_db = ip.replace('\n', '')
                        #infoSystel_writer('itensSystel.TXT', info, dict_forn, dict_aler, dict_fraciona, dict_conserva, ip_db)
                        try:
                            ip_db = ip.replace('\n', '')
                            infoSystel_writer('itensSystel.TXT', info, dict_forn, dict_aler, dict_fraciona, dict_conserva, dict_tara ,ip_db)
                        except Exception as err:
                            with open('log-erro-conexao.txt', 'a') as log:
                                log.write(f'#{datetime.datetime.now()} - erro ao importar para: {ip} erro : {err}\n')
                        else:
                            txt += f'{ip} '
                            time.sleep(5)
                        finally:
                            pass
                    with open('log.txt', 'a') as log:
                        log.write(f'#{datetime.datetime.now()} - importou corretamente: {txt}\n')
                    
                #print(len(codPlu_array))
                #print(len(codNutri_array))
                #os.remove("../arqsok.bak")
                
                

                time.sleep(25)
                        
            else:
                pass
            time.sleep(20)


def start():
    print("""
░██████╗██╗░░░██╗░██████╗████████╗███████╗██╗░░░░░
██╔════╝╚██╗░██╔╝██╔════╝╚══██╔══╝██╔════╝██║░░░░░
╚█████╗░░╚████╔╝░╚█████╗░░░░██║░░░█████╗░░██║░░░░░
░╚═══██╗░░╚██╔╝░░░╚═══██╗░░░██║░░░██╔══╝░░██║░░░░░
██████╔╝░░░██║░░░██████╔╝░░░██║░░░███████╗███████╗
╚═════╝░░░░╚═╝░░░╚═════╝░░░░╚═╝░░░╚══════╝╚══════╝
██╗███╗░░░███╗██████╗░░█████╗░██████╗░████████╗░█████╗░██████╗░░█████╗░██████╗░
██║████╗░████║██╔══██╗██╔══██╗██╔══██╗╚══██╔══╝██╔══██╗██╔══██╗██╔══██╗██╔══██╗
██║██╔████╔██║██████╔╝██║░░██║██████╔╝░░░██║░░░███████║██║░░██║██║░░██║██████╔╝
██║██║╚██╔╝██║██╔═══╝░██║░░██║██╔══██╗░░░██║░░░██╔══██║██║░░██║██║░░██║██╔══██╗
██║██║░╚═╝░██║██║░░░░░╚█████╔╝██║░░██║░░░██║░░░██║░░██║██████╔╝╚█████╔╝██║░░██║
╚═╝╚═╝░░░░░╚═╝╚═╝░░░░░░╚════╝░╚═╝░░╚═╝░░░╚═╝░░░╚═╝░░╚═╝╚═════╝░░╚════╝░╚═╝░░╚═╝"""
    )

    print("""

          

🅱 y Lucas Isabel - [https://github.com/Lucasbyte]
              """)

if __name__ == "__main__":
    main()