from services.gmail.SheetService import SheetService

class CfldSheetService(SheetService):
    def __init__(self, email, sheet_name, spreadsheet_id, secret_path, token_dir):
        super(CfldSheetService, self).__init__(email, sheet_name, spreadsheet_id, secret_path, token_dir)

    def get_lookup_info_data(self):
        try:
            return self.lookup_info_data
        except:
            self.lookup_info_data = self.service.spreadsheets().values().get(spreadsheetId=self.spreadsheet_id, range='lookup_info!A1:C100').execute().get('values', [])
        return self.lookup_info_data

    def get_llm_info(self):
        try:
            return self.llm_context_data
        except:
            self.llm_context_data = self.service.spreadsheets().values().get(spreadsheetId=self.spreadsheet_id, range='llm_context!A1:C100').execute().get('values', [])
        return self.llm_context_data

    def get_availability(self):
        try:
            return self.availability
        except:
            self.availability = self.service.spreadsheets().values().get(spreadsheetId=self.spreadsheet_id, range='availability!A1:E100').execute().get('values', [])
        return self.availability

    def get_availability_blurbs(self):
        try:
            return self.availability_blurbs
        except:
            self.availability_blurbs = self.service.spreadsheets().values().get(spreadsheetId=self.spreadsheet_id, range='availability!I1:N3').execute().get('values', [])
        return self.availability_blurbs
