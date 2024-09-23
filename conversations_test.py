import datetime




class Conversation:
    def __init__(self):
        self.file_name = self.generate_filename()
        


    def generate_filename(self, prefix="file", extension="json"):
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        return  f"{prefix}_{timestamp}.{extension}"




