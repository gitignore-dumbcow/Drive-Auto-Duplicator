import os
import datetime
from google.oauth2 import service_account
from googleapiclient.discovery import build

# Path to your service account credentials
CREDENTIALS_FILE = 'drive-auto-file-duplicator-d2c32ec0ecce.json'  # Update this path
TEMPLATE_FOLDER_ID = '1WPoPRM4D0SCS6CgSP7xz4pgwkpH9dwnH'  # Template folder ID
TARGET_FOLDER_ID = '1-8qb3oRJwkvx4qvFONP6j3yDXUZAREmw'  # Target folder ID

def authenticate_drive():
    creds = service_account.Credentials.from_service_account_file(
        CREDENTIALS_FILE,
        scopes=["https://www.googleapis.com/auth/drive"]
    )
    return build('drive', 'v3', credentials=creds)

def create_folder(service, name, parent_id):
    file_metadata = {
        'name': name,
        'mimeType': 'application/vnd.google-apps.folder',
        'parents': [parent_id]
    }
    folder = service.files().create(body=file_metadata, fields='id').execute()
    print(f"Created folder '{name}' with ID: {folder.get('id')}")
    return folder.get('id')

def copy_file(service, file_id, new_folder_id):
    # Copy the file to the new folder
    copied_file = {'parents': [new_folder_id]}
    return service.files().copy(fileId=file_id, body=copied_file).execute()

def duplicate_files(service, template_folder_id, new_folder_id):
    results = service.files().list(
        q=f"'{template_folder_id}' in parents and mimeType != 'application/vnd.google-apps.folder'",
        fields="files(id, name)"
    ).execute()
    items = results.get('files', [])

    if not items:
        print('No files found.')
    else:
        for item in items:
            # Preserve the original file name in the new copy
            copied_file = {'name': item['name'], 'parents': [new_folder_id]}
            service.files().copy(fileId=item['id'], body=copied_file).execute()
            print(f"Copied file '{item['name']}' to new folder.")


def main():
    service = authenticate_drive()

    # Create a new folder named as the current date
    import datetime

    date_folder_name = (datetime.datetime.now() + datetime.timedelta(days=7)).strftime("%d/%m")

    new_folder_id = create_folder(service, date_folder_name, TARGET_FOLDER_ID)

    # Create subfolders
    create_folder(service, 'Media', new_folder_id)
    create_folder(service, 'Document', new_folder_id)

    # Duplicate files from the template folder into the new folder
    duplicate_files(service, TEMPLATE_FOLDER_ID, new_folder_id)

if __name__ == '__main__':
    main()
