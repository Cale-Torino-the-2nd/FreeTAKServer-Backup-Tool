import os
from distutils.errors import DistutilsFileError
from shutil import copyfile, rmtree
from distutils.dir_util import copy_tree
import zipfile
import importlib

VERSION = "0.1"


def backup_fts():
    try:
        import FreeTAKServer.controllers.configuration.MainConfig as Mainconfig
    except ImportError:
        print("Cannot import FTS, it must not be installed on this machine. cannot continue")
        exit(0)
    tmp_dir = "/tmp/fts-backup"
    if os.path.exists(tmp_dir):
        rmtree(tmp_dir)
    os.makedirs(tmp_dir)
    try:
        # MainConfig.py
        try:
            copyfile(f"{Mainconfig.MainConfig.MainPath}/controllers/configuration/MainConfig.py", f"{tmp_dir}/MainConfig.py")
        except FileNotFoundError:
            print("Cannot find MainConfig.py")
        # FTSDataBase.db
        try:
            copyfile(Mainconfig.MainConfig.DBFilePath, f"{tmp_dir}/FTSDataBase.db")
        except FileNotFoundError as e:
            print("Cannot find the FTSDataBase")
        # ExCheck
        copy_tree(Mainconfig.MainConfig.ExCheckMainPath, f"{tmp_dir}/ExCheck")
        # FreeTAKServerDataPackageFolder
        copy_tree(Mainconfig.MainConfig.DataPackageFilePath, f"{tmp_dir}/FreeTAKServerDataPackageFolder")
        # certs
        copy_tree(Mainconfig.MainConfig.certsPath, f"{tmp_dir}/certs")
    except PermissionError as e:
        print("You are not root, this tool needs to be running as root.")
        exit(1)

    with zipfile.ZipFile("./fts-backup.zip", 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(tmp_dir):
            for file in files:
                zipf.write(os.path.join(root, file), os.path.join(root[4:], file))
    rmtree(tmp_dir)


def restore_fts(backup_zip: str = "./fts-backup.zip"):
    try:
        import FreeTAKServer.controllers.configuration.MainConfig as Mainconfig
    except ImportError:
        print("Cannot import FTS, it must not be installed on this machine. cannot continue")
        exit(0)
    with zipfile.ZipFile(backup_zip, 'r') as zip_ref:
        zip_ref.extractall("./")
        backup_dir = "./fts-backup"
    try:
        # MainConfig.py
        copyfile(f"{backup_dir}/MainConfig.py", f"{Mainconfig.MainConfig.MainPath}/controllers/configuration/MainConfig.py")
        # FTSDataBase.db
        copyfile(f"{backup_dir}/FTSDataBase.db", Mainconfig.MainConfig.DBFilePath)
        # ExCheck
        copy_tree(f"{backup_dir}/ExCheck", Mainconfig.MainConfig.ExCheckMainPath)
        # FreeTAKServerDataPackageFolder
        try:
            copy_tree(f"{backup_dir}/FreeTAKServerDataPackageFolder", Mainconfig.MainConfig.DataPackageFilePath)
        except DistutilsFileError:
            # This happens because the directory is empty when backing up so isn't present
            pass
        # certs
        copy_tree(f"{backup_dir}/certs", Mainconfig.MainConfig.certsPath)
    except PermissionError as e:
        print("You are not root, this tool needs to be running as root.")
        exit(1)
    rmtree(backup_dir)


def backup_fts_ui():
    tmp_dir = "/tmp/fts-ui-backup"
    if os.path.exists(tmp_dir):
        rmtree(tmp_dir)
    os.makedirs(tmp_dir)
    try:
        ui_config = importlib.import_module("FreeTAKServer-UI.config")
        test = ui_config.Config()
        copyfile(f"{test.basedir}/config.py", f"{tmp_dir}/config.py")

        with zipfile.ZipFile("./fts-ui-backup.zip", 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, dirs, files in os.walk(tmp_dir):
                for file in files:
                    zipf.write(os.path.join(root, file), os.path.join(root[4:], file))
    except PermissionError as e:
        print("You are not root, this tool needs to be running as root.")
        exit(1)
    rmtree(tmp_dir)


def restore_fts_ui(backup_zip: str = "./fts-ui-backup.zip"):
    with zipfile.ZipFile(backup_zip, 'r') as zip_ref:
        zip_ref.extractall("./")
    backup_dir = "./fts-ui-backup"
    ui_config = importlib.import_module("FreeTAKServer-UI.config")
    ui_config_class = ui_config.Config()
    try:
        copyfile(f"{backup_dir}/config.py", f"{ui_config_class.basedir}/config.py")
    except PermissionError as e:
        print("You are not root, this tool needs to be running as root.")
        exit(1)
    rmtree(backup_dir)


if __name__ == '__main__':
    print("""
    -------------------------
    FreeTAKServer Backup Tool
    -------------------------
    
    """)
    backup_or_restore = input("Backup or Restore? b/r  ")
    if backup_or_restore.lower() == "b":
        backup_fts_answer = input("Would you like to backup your FTS instance? Y/n ")
        if backup_fts_answer.lower() != "n":
            backup_fts()
            print("-------------------------")
            print("  FTS Backup Complete")
            print("-------------------------")

        backup_fts_ui_answer = input("Would you like to backup your FTS UI? Y/n ")
        if backup_fts_ui_answer.lower() != "n":
            backup_fts_ui()
            print("-------------------------")
            print("   UI Backup Complete")
            print("-------------------------")

    elif backup_or_restore.lower() == "r":

        restore_fts_answer = input("Would you like to restore your FTS instance? Y/n ")
        if restore_fts_answer.lower() != "n":
            restore_fts()
            print("-------------------------")
            print("     FTS Restored")
            print("-------------------------")

        restore_fts_ui_answer = input("Would you like to restore your FTS UI? Y/n ")
        if restore_fts_ui_answer.lower() != "n":
            restore_fts_ui()
            print("-------------------------")
            print("      UI Restored")
            print("-------------------------")
