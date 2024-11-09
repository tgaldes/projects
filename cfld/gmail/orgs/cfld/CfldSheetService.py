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
        info = self.service.spreadsheets().values().get(spreadsheetId=self.spreadsheet_id, range='llm_context!A4:G200').execute().get('values', [])
        # info is a list of lists. each inner list has a single string element
        # combine them all into a single string then return
        d = {}
        for i, key in enumerate(info[0]):
            d[key] = ''
            for j in info[1:]:
                if len(j) <= i:
                    continue
                d[key] += j[i] + '\n\n'
            #d[key] = '\n\n'.join([j[i] for j in info[1:]])
        return d

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

    def check_reload(self):
        try:
            reload = int(self.service.spreadsheets().values().get(spreadsheetId=self.spreadsheet_id, range='reload!A2:A2').execute().get('values', [])[0][0])
            if reload == 1:
                # reset reload flag on the sheet
                self.service.spreadsheets().values().update(spreadsheetId=self.spreadsheet_id, range='reload!A2:A2', body={'values': [[0]]}, valueInputOption='RAW').execute()
                return True
            else:
                return False
        except:
            return False
