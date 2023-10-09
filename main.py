import os
import requests
import config
import mimetypes
import time
import json
import time


def send_file(endpoint_to_send:str, token:str, folder_id:str, file_path:str) -> dict:
    #prepara o arquivo para o envio.
    file_name = os.path.basename(file_path)

    mimetype, _ = mimetypes.guess_type(file_path)
    if mimetype is None:
        mimetype = 'application/octet-stream'

    with open(file_path, 'rb') as file:
        file_to_send = ('files', (file_name, file, mimetype))

        #faz o envio para o Alan.
        payload = {'folder_id': folder_id}
        headers = {'Authorization': 'Bearer ' + token}

        response = requests.request("POST", endpoint_to_send, headers=headers, data=payload, files=[file_to_send])
    return response

def search_file(endpoint_to_search:str, token:str, file_id:str) -> dict:
    url = endpoint_to_search + file_id
    headers = {'Authorization': 'Bearer ' + token}
    response = requests.request("GET", url, headers=headers, data={})
    return response

def search_folder(endpoint_to_search:str, token:str, folder_id:str) -> dict:
    url = endpoint_to_search + folder_id
    headers = {'Authorization': 'Bearer ' + token}
    response = requests.request("GET", url, headers=headers, data={})
    return response


if __name__ == "__main__":
    #recebe e valida o ambiente que deve ser usado.
    environment = input("Informe o ambiente que deve ser usado (local, qa, prod): ")
    while environment not in ["local", "qa", "prod"]:
        environment = input("Informe um ambiente válido (local, qa, prod): ")

    if environment == "local":
        endpoint_to_send_file = config.SEND_FILE_LOCAL
        endpoint_to_search_file = config.SEARCH_FILE_LOCAL
        endpoint_to_search_folder = config.SEARCH_FOLDER_LOCAL

    elif environment == "qa":
        endpoint_to_send_file = config.SEND_FILE_QA
        endpoint_to_search_file = config.SEARCH_FILE_QA
        endpoint_to_search_folder = config.SEARCH_FOLDER_QA

    else:
        endpoint_to_send_file = config.SEND_FILE_PROD
        endpoint_to_search_file = config.SEARCH_FILE_PROD
        endpoint_to_search_folder = config.SEARCH_FOLDER_PROD

    #recebe e valida o token e folder_id que deve ser usado.
    token = input("Informe o token que deve ser usado: ")
    folder_id = input("Informe o folder_id que deve ser usado: ")
    response = search_folder(endpoint_to_search=endpoint_to_search_folder, token=token, folder_id=folder_id)
    while response.status_code != 200:
        print("ERRO: token ou folder_id inválidos, insira novamente")
        token = input("Informe o token que deve ser usado: ")
        folder_id = input("Informe o folder_id que deve ser usado: ")
        token_response = search_folder(endpoint=endpoint_to_search_folder, token=token, folder_id=folder_id)

    #recebe e valida o diretório onde estão os arquivos que serão enviados.
    dir = input("Informe o diretório dos arquivos que devem ser enviados: ")
    while not os.path.exists(dir):
        dir = input("O diretório informado não foi encontrado, informe outro diretório: ")

    file_list = os.listdir(dir)
    for file in file_list:
        try:
            #verifica se o formato é aceito pelo Alan.
            if file.split('.')[-1] not in config.FILES_ACCEPTED:
                continue

            #envia o arquivo para o Alan.
            print(f"Enviando arquivo: {file}")
            send_response = send_file(endpoint_to_send=endpoint_to_send_file, token=token, folder_id=folder_id, file_path=dir + "/" + file)
            send_response_data = json.loads(send_response.text)

            #verifica se o envio foi concluído com sucesso.
            if send_response.status_code != 201:
                print(f"Falha ao enviar o arquivo: {file}")
                with open("log_errors.txt", "a") as log:
                    message = f"{file}: Falha durante o envio."
                    log.write(message + "\n")
                print("=" * 100)
                continue

            #aguarda o processamento do arquivo atual para dar início ao envio do próximo arquivo.
            print(f"Aguardando processamento do arquivo: {file}")
            search_response = search_file(endpoint_to_search=endpoint_to_search_file, token=token, file_id=send_response_data['message'][0]['file_id'])
            search_response_data = json.loads(search_response.text)

            start_time = time.time()
            while True:
                print(f"{int(search_response_data['read_percentage'])}% -> {file}")

                #verifica se o processamento está demorando mais de 30 minutos.
                if time.time() - start_time > 30 * 60:
                    print("O processamento durou mais de 30 minutos. Iniciando envio do próximo arquivo.")
                    with open("log_errors.txt", "a") as log:
                        message = f"{file}: O processamento durou mais de 30 minutos."
                        log.write(message + "\n")
                    print("=" * 100)
                    break

                if search_response_data['reading_status'] == "DN":
                    print(f"Processamento do arquivo concluído: {file}")
                    print("=" * 100)
                    break

                if search_response_data['reading_status'] == "ER":
                    print(f"Falha ao processar o arquivo: {file}")
                    with open("log_errors.txt", "a") as log:
                        message = f"{file}: Falha durante o processamento."
                        log.write(message + "\n")
                    print("=" * 100)
                    break

                time.sleep(5)
                search_response = search_file(endpoint_to_search=endpoint_to_search_file, token=token, file_id=send_response_data['message'][0]['file_id'])
                search_response_data = json.loads(search_response.text)

        except Exception as e:
            print(f"Um erro interno ocorreu, retomando o envio em 5 minutos.")
            with open("log_errors.txt", "a") as log:
                message = f"{file}: Falha interna: {e}"
                log.write(message + "\n")
            print("=" * 100)
            time.sleep(300)