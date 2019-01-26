import requests
from aws import get_item


# personal details / default choices pulled from dynamodb user item
personal_access_token = get_item['ynab_access_token']
card_name = get_item['default_card']
budget = get_item['default_budget']

# base api url
base_url = 'https://api.youneedabudget.com/v1/'

# Budgets url
budget_list_url = f'{base_url}/budgets'

headers = {
    'accept': 'application/json',
    'Authorization': f'Bearer {personal_access_token}',
    'Content-Type': 'application/json',
}


# returns list of all budgets in YNAB account
def get_budgets():
    request_budget_list = requests.get(budget_list_url, headers=headers)
    budgets = request_budget_list.json()['data']['budgets']
    return budgets


# Returns budget id of a specific budget passed in as budget_name
def specific_budget_id(budget_name):
    for item in get_budgets():
        for value in item.values():
            if budget_name == value:
                budget_id = item['id']

                return budget_id


# class for getting necessary information from specific budgets
class BudgetInfo:

    def __init__(self, card, budget):
        self.card = card
        self.budget = budget

    def budget_categories(self):
        budget_url = f'{budget_list_url}/{specific_budget_id(self.budget)}'
        broad_budget_categories = requests.get(f'{budget_url}/categories',
                                               headers=headers)
        budget_categories = broad_budget_categories.json()['data']['category_groups']
        return budget_categories

    def account_list(self):
        budget_accounts_list = requests.get(f'{budget_list_url}/{specific_budget_id(self.budget)}',
                                            headers=headers)
        account_list = budget_accounts_list.json()['data']['budget']['accounts']
        return account_list

    def account_id(self):
        for item in BudgetInfo.account_list(self):
            if item['name'] == self.card:
                account_id = item['id']
                return account_id


main_budget = BudgetInfo(card_name, budget)


# returns the id of a passed in category
def get_category_id(category):
    for item in main_budget.budget_categories():
        for specific_category in item['categories']:
            if specific_category['name'] == category:
                return specific_category['id']

