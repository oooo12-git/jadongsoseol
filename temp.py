from sheet.modify_sheet import GoogleSheet

sheet = GoogleSheet('motivation')

budget_tokens = sheet.get_last_data('budget_tokens')

print(type(budget_tokens))