import requests
from urllib.request import urlopen
from bs4 import BeautifulSoup
import re
import pandas as pd


all_vacancies = []
vacancy = input("Enter desired vacancy: ")
if len(vacancy.split(" ")) > 1:
    vacancy = "+".join(vacancy.split(" "))

html = f"https://hh.ru/search/vacancy?text={vacancy}"

class hh(): #Класс
    def __init__(self):
        self.count = 0
        self.currency_n = None

    def getting_vacancies(self, html_file):
        all_vacations = []
        for tag in html_file.find_all("div", {"class" : "bloko-gap"}):
            for a in tag.find_all("div", {"data-qa" : re.compile("vacancy-serp__vacancy")}):
                vacancy = {}
                try:
                    vacancy["salary_min"] = hh.calculate_min_salary(a.select("[data-qa~=vacancy-serp__vacancy-compensation]")[0].text)
                except (AttributeError, IndexError) as error:
                    vacancy["salary_min"] = "-"
                try:
                    vacancy["salary_max"] = hh.calculate_max_salary(a.select("[data-qa~=vacancy-serp__vacancy-compensation]")[0].text)
                except (AttributeError, IndexError) as error:
                    vacancy["salary_max"] = "-"
                try:
                    vacancy["currency_n"] = hh.extract_cur(a.select("[data-qa~=vacancy-serp__vacancy-compensation]")[0].text)
                except (AttributeError, IndexError) as error:
                    vacancy["currency_n"] = "-"
                try:
                    vacancy["currency"] = a.select("[data-qa~=vacancy-serp__vacancy-compensation]")[0].text
                except (AttributeError, IndexError) as error:
                    vacancy["currency"] = "-"
                try:
                    vacancy["position"] = a.select("[data-qa~=vacancy-serp__vacancy-title]")[0].text
                except (AttributeError, IndexError) as error:
                    vacancy["position"] = "-"
                try:
                    vacancy["respons"] = a.select("[data-qa~=vacancy-serp__vacancy_snippet_responsibility]")[0].text
                except (AttributeError, IndexError) as error:
                    vacancy["respons"] = "-"
                try:
                    vacancy["city"] = a.select("[data-qa~=vacancy-serp__vacancy-address]")[0].text
                except (AttributeError, IndexError) as error:
                    vacancy["city"] = "-"
                try:
                    vacancy["Link to the vacancy"] = a.select("[data-qa~=vacancy-serp__vacancy-title]")[0].get('href')
                except (AttributeError, IndexError) as error:
                    vacancy["Link to the vacancy"] = "-"

                all_vacations.append(vacancy)

        return all_vacations

    def extract_cur(self, salary):
        salary = salary.replace("\u202f", '')
        split_salary = salary.split()
        return split_salary[len(split_salary)-1]

    def find_appropr_cur(self, list):
        cur_dict = {}
        for cur in list:
            cur_dict[cur] = extraction_currency(cur)
        return cur_dict

    def gather_cur(self, all_vacancies):
        currencies = []

        for el in all_vacancies:
            for item in el:
                currencies.append(item["currency_n"])
        currencies = set(currencies)
        currencies = list(currencies)
        currencies = [el for el in currencies if el != "-"]
        return currencies

    def calculate_min_salary(self, salary):
        salary = salary.replace("\u202f", '')
        split_salary = salary.split()
        numbers = []
        # self.currency_n =

        if any(map(lambda each: each in ["–", "-"], split_salary)) == True:
            for el in split_salary:
                if el.isdigit():
                    numbers.append(el)
            return (min(numbers))
        elif "от" in split_salary:
            for el in split_salary:
                if el.isdigit():
                    numbers.append(el)
            return (min(numbers))
        else:
            return "-"

    def calculate_max_salary(self, salary):
        salary = salary.replace("\u202f", '')
        split_salary = salary.split()
        numbers = []

        if any(map(lambda each: each in ["–", "-"], split_salary)) == True:
            for el in split_salary:
                if el.isdigit():
                    numbers.append(el)
            return (max(numbers))
        elif "до" in split_salary:
            for el in split_salary:
                if el.isdigit():
                    numbers.append(el)
            return (max(numbers))
        else:
            return "-"

def multiply(all_vacancies): #Функция для перемножения двух столбцов
    all_vacancies["salary_min_rub"] = all_vacancies["salary_min"]
    all_vacancies["salary_max_rub"] = all_vacancies["salary_max"]
    all_vacancies.loc[all_vacancies["currency_n"] != "-", "calculated_cur"] = "Rub"
    Number_min = all_vacancies.loc[((~all_vacancies["Number"].isna()) & (all_vacancies["salary_min"] != "-")), "Number"].str.replace(',', '.').astype("float")
    Number_max = all_vacancies.loc[((~all_vacancies["Number"].isna()) & (all_vacancies["salary_max"] != "-")), "Number"].str.replace(',','.').astype("float")
    salary_min_upd = all_vacancies.loc[((~all_vacancies["Number"].isna()) & (all_vacancies["salary_min"] != "-")), "salary_min"].str.replace(',', '.').astype("float")
    salary_max_upd = all_vacancies.loc[((~all_vacancies["Number"].isna()) & (all_vacancies["salary_max"] != "-")), "salary_max"].str.replace(',', '.').astype("float")
    all_vacancies.loc[((~all_vacancies["Number"].isna()) & (all_vacancies["salary_min"] != "-")), "salary_min_rub"] = salary_min_upd * Number_min
    all_vacancies.loc[((~all_vacancies["Number"].isna()) & (all_vacancies["salary_min"] != "-")), "salary_max_rub"] = salary_max_upd * Number_max
    return all_vacancies

def gather_vacancies(html): #Функция для сбора вакансий по опредленному названию
    i = 0
    while True:
        try:
            html_file = BeautifulSoup(urlopen(html), "lxml")
            all_vacancies.append(hh.getting_vacancies(html_file))
            i = i + 1
            print(f"Completed {i} link: {html}")
            html_ref = html_file.select("[data-qa~=pager-next]")[0].get("href")
            html = "https://hh.ru" + html_ref
            # if i == 3:
            #     return all_vacancies
        except IndexError as error:
            return all_vacancies
    return all_vacancies

def extraction_currency(cur): #Выгрузка курсов валют на основании тех валют, что указаны в вакансиях
    url = "https://www.google.com/search?q="
    if cur.lower() not in ["rub", "rub.", "руб", "руб."]:
        url = url + cur + " rub"
        headers = {'User-Agent' : "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.82 Safari/537.36"}
        full_page = requests.get(url, headers = headers, verify=False)
        soup = BeautifulSoup(full_page.content, 'html.parser')
        convert = soup.findAll("span", {"class": "DFlfde SwHCTb", "data-precision" : re.compile("\d")})
        # return convert[0].text
        return(convert[0].text)

def to_data_frame(all_vac): #Функция для уменьшения размерности списка и превращения его в dataframe
    return pd.DataFrame([item for sublist in all_vac for item in sublist])

def merge_cur(all_vac, cur): #Объединение с таблицей валют
    cur = pd.DataFrame.from_dict(cur, orient='index', columns=['Number'])
    all_vac = all_vac.merge(cur, how="left", left_on="currency_n", right_index=True)
    return all_vac

def remove_all_useless_inf(all): #удаление ненужных знаков тире
    try:
        return all[(all["position"] != "-")]
    except KeyError as error:
        pass

hh = hh()
all_vacancies = gather_vacancies(html)

list_currencies = hh.gather_cur(all_vacancies)
all_vacancies = to_data_frame(all_vacancies)
if len(list_currencies) != 0:
    cur_dict = hh.find_appropr_cur(list_currencies)
    all_vacancies = merge_cur(all_vacancies, cur_dict)
all_vacancies = remove_all_useless_inf(all_vacancies)
all_vacancies = multiply(all_vacancies)

try:
    all_vacancies.to_excel("test.xlsx")
except AttributeError:
    print("No found")