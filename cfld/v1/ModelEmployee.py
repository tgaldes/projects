from House import House

class ModelEmployee:
    def __init__(self, houses):
        #self.apiToken = apiToken
        self.houses = []
        for house in houses:
            self.houses.append(House(house))

    def send_intro_emails(self, min_duplicate_days,
                          house_filter=[],
                          house_filter_is_include=True,
                          school_filter=[],
                          school_filter_is_include=True,
                          code_filter=[],
                          code_filter_is_include=True):
        pass
    def make_phone_calls(self, min_duplicate_days,
                          house_filter=[],
                          house_filter_is_include=True,
                          school_filter=[],
                          school_filter_is_include=True,
                          code_filter=[],
                          code_filter_is_include=True):
        pass
    def send_snail_mail(self, min_duplicate_days,
                          house_filter=[],
                          house_filter_is_include=True,
                          school_filter=[],
                          school_filter_is_include=True,
                          code_filter=[],
                          code_filter_is_include=True):
        for house in self.houses:
            print(house.write_letter())





if __name__=='__main__':
    emp = ModelEmployee(['Theta Xi', 'SAE'])
    emp.send_snail_mail(365)


