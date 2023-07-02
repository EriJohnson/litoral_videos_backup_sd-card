import os
import shutil
import datetime
import msvcrt
import psutil
import locale
from tqdm import tqdm

locale.setlocale(locale.LC_TIME, 'pt_BR.UTF-8')

def copy_files(source, destination):
    total_files = len(source)
    total_size = sum(os.path.getsize(file) for file in source)
    print(f"Total files: {total_files}")
    print(f"Total size: {total_size} bytes")
    print("Copying files:")
    with tqdm(total=total_size, unit='B', unit_scale=True, ncols=80) as progress_bar:
        for file in source:
            shutil.copy(file, destination)
            progress_bar.update(os.path.getsize(file))
    print("Copying files: Done")
    print("")

def rename_files(folder_path):
    files = os.listdir(folder_path)
    for file in files:
        if file.endswith(".LRV"):
            new_name = os.path.splitext(file)[0] + ".MP4"
            os.rename(os.path.join(folder_path, file), os.path.join(folder_path, new_name))

def create_folder_structure(date, guide_name, tour_name, base_path):
    year_folder = os.path.join(base_path, date.strftime("%Y"))
    month_number = date.strftime('%m')
    month_name = date.strftime('%B').upper()
    folder_name = f"{date.day} DE {month_name} {date.year} - {tour_name.upper()} - {guide_name.upper()}"
    folder_path = os.path.join(year_folder, f"{month_number}. {month_name}", folder_name)
    os.makedirs(folder_path, exist_ok=True)
    footage_path = os.path.join(folder_path, "Footage")
    proxy_path = os.path.join(folder_path, "Proxy Media")
    os.makedirs(footage_path, exist_ok=True)
    os.makedirs(proxy_path, exist_ok=True)
    return folder_path, footage_path, proxy_path

def write_message_file(date, tour_name, folder_path):
    formatted_date = date.strftime("%d de %B de %Y")
    message = f"*Litoral Vídeos* 📹🏖☀😎\n\nOlá!\n\nSegue, o link do YouTube com a filmagem do seu passeio de *{tour_name}* do dia {formatted_date}:\n\n[LINK DO VÍDEO]\n\nAqui também vai um link com as imagens aéreas do Ceará que separamos para vocês:\n\nhttps://youtu.be/4C7cDVfsGf4\n\nObrigado pela sua visita e aproveite a filmagem!\n\nQualquer dúvida estamos à disposição"
    file_path = os.path.join(folder_path, "message.txt")
    with open(file_path, "w", encoding='utf-8') as file:
        file.write(message)

def format_participants_text(pasted_text):
    participants = []
    lines = pasted_text.split("[")

    for line in lines:
        if line.strip():
            name_start = line.find(":", line.find(":") + 1) + 2
            name_end = line.rfind("[")
            name = line[name_start:name_end].strip().title()
            participants.append(name)
    return participants

def write_participants_file(participants, folder_path):
    file_path = os.path.join(folder_path, "participants.txt")
    with open(file_path, "w") as file:
        for participant in participants:
            file.write(participant + "\n")

def get_sd_card_path():
    drives = psutil.disk_partitions(all=True)
    for drive in drives:
        if drive.fstype == 'exfat' or drive.fstype == 'fat32' or drive.fstype == 'FAT':
            return drive.mountpoint
    raise ValueError("Nenhum cartão SD detectado")

def get_user_input():
    print("De que dia é a filmagem?")
    print("")

    print("1) Hoje")
    print("2) Ontem")
    print("3) Especificar data (Formato: DD/MM/AAAA)")
    print("")

    option = int(input("Opção: "))
    if option == 1:
        date = datetime.date.today()
    elif option == 2:
        date = datetime.date.today() - datetime.timedelta(days=1)
    elif option == 3:
        print("")
        date_str = input("Digite a data (DD/MM/AAAA): ")
        date = datetime.datetime.strptime(date_str, "%d/%m/%Y").date()
    else:
        raise ValueError("Opção inválida")
    os.system("cls")

    guide_name = input("Nome do guia? ")
    os.system("cls")

    print("Qual passeio?")
    print("")

    print("1) Morro Branco")
    print("2) Lagoinha")
    print("3) Canoa Quebrada")
    print("4) Outro")
    print("")

    tour_option = int(input("Opção: "))
    if tour_option == 1:
        tour_name = "Morro Branco"
    elif tour_option == 2:
        tour_name = "Lagoinha"
    elif tour_option == 3:
        tour_name = "Canoa Quebrada"
    elif tour_option == 4:
        tour_name = input("Digite o nome do passeio: ")
    else:
        raise ValueError("Opção inválida")
    os.system("cls")

    participants_text = input("Cole o texto com os participantes: ")
    participants = format_participants_text(participants_text)
    

    return date, guide_name, tour_name, participants

def wait_for_keypress():
    print("\nProcesso finalizado com sucesso. Aperte qualquer tecla para encerrar...")
    msvcrt.getch()

try:
    # Get SD card path
    sd_card_path = get_sd_card_path()
    print(f"Cartão SD detectado em: {sd_card_path}")
    print("")

    # Get user input
    date, guide_name, tour_name, participants = get_user_input()

    # Copy files from SD card
    files_to_copy = [file for file in os.listdir(sd_card_path) if os.path.isfile(os.path.join(sd_card_path, file))]
    destination_folder = f"bkp - {datetime.datetime.now().strftime('%Y%m%d%H%M%S')}"
    destination_path = os.path.join(os.getcwd(), destination_folder)
    os.makedirs(destination_path, exist_ok=True)
    print("Iniciando backup do cartão:")
    print("")

    copy_files([os.path.join(sd_card_path, file) for file in files_to_copy], destination_path)

    # Create folder structure
    base_path = r"D:\ARQUIVO"
    folder_path, footage_path, proxy_path = create_folder_structure(date, guide_name, tour_name, base_path)

    # Copy files
    print("Iniciando cópia dos arquivos bruto:")
    print("")

    copy_files([os.path.join(destination_path, file) for file in files_to_copy if file.endswith(".MP4")], footage_path)

    print("Iniciando cópia dos arquivos proxy:")
    print("")
    copy_files([os.path.join(destination_path, file) for file in files_to_copy if file.endswith(".LRV")], proxy_path)

    # Rename files in Proxy Media folder
    rename_files(proxy_path)

    # Write message file
    write_message_file(date, tour_name, folder_path)

    # Write participants file
    write_participants_file(participants, folder_path)

    # Wait for keypress to exit
    wait_for_keypress()

    os.startfile(folder_path)

except ValueError as e:
    print(f"Erro: {str(e)}")
except Exception as e:
    print(f"Ocorreu um erro durante a execução do script: {str(e)}")
    wait_for_keypress()
