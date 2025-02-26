import file_processor

if __name__ == "__main__":
    folder_to_watch = r'\\allen-files\edi\ASC\BRAWHI-ORDER-STATUS'
    file_processor.process_existing_files(folder_to_watch)