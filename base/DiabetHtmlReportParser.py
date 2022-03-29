import json
import os
from urllib import request, error


def add_header_district_to_table(district):
    return "  <tr id=\"district\"><td>{0}</td></tr>\n  <tr>\n".format(district["name"].strip())


class DiabetHtmlReportParser:
    def __init__(self, data_suffix=''):
        self.headers_benefit_federal = ["Название", "Адрес", "Федеральная льгота"]

        self.headers_benefit_regional = ["Название", "Адрес", "Региональная льгота"]

        self.headers_diff = ["Название", "Адрес", "Что изменилось"]

        self.base_url = "https://eservice.gu.spb.ru/portalFront/proxy/async?filter={}&operation=getMedicament"

        self.timeout = 30

        self.count_tries = 10

        self.nothing_found = "Ничего не найдено"

        self.json_data_dir = "../json_data"

        self.data_suffix = data_suffix

        self.district_substring = " район"

    def add_district_to_table(self, district, benefit_federal):
        if self.district_substring in district["name"]:
            district_table = "  <tr id=\"district\"><td>{0}</td></tr>\n  <tr>\n".format(district["name"].strip())
        else:
            district_table = "  <tr id=\"district\"><td>{0} {1}</td></tr>\n  <tr>\n".format(district["name"].strip(),
                                                                                            self.district_substring)
        for pharmacy in district["apothecaries"]:
            district_table += self.add_pharmacy_to_table(pharmacy, benefit_federal)
        return district_table

    def add_new_district_to_table(self, district, benefit_federal):
        district_table = add_header_district_to_table(district)
        for pharmacy in district["apothecaries"]:
            district_table += self.add_new_pharmacy_to_table(pharmacy, benefit_federal)
        return district_table

    def add_pharmacy_to_table(self, pharmacy, benefit_federal):
        district_table = "  <tr>\n"
        if benefit_federal:
            for pharmacy_column in [pharmacy["name"], self.clear_address(pharmacy["address"]),
                                    pharmacy["ost2"]]:
                district_table += "    <td>{0}</td>\n".format(pharmacy_column.strip())
        else:
            for pharmacy_column in [pharmacy["name"], self.clear_address(pharmacy["address"]),
                                    pharmacy["ost2"]]:
                district_table += "    <td>{0}</td>\n".format(pharmacy_column.strip())
        district_table += "  </tr>\n"
        return district_table

    def add_new_pharmacy_to_table(self, new_pharmacy, benefit_federal):
        ost1_new = float(new_pharmacy["ost1"].replace(",", "."))
        ost2_new = float(new_pharmacy["ost2"].replace(",", "."))

        district_table = "  <tr>\n"
        for pharmacy_column in [new_pharmacy["name"], self.clear_address(new_pharmacy["address"])]:
            district_table += "    <td>{0}</td>\n".format(pharmacy_column.strip())

        district_table += "    <td>"
        if ost1_new != 0 and benefit_federal:
            district_table += "Федеральная льгота: {0} ({1}) ".format(ost1_new, new_pharmacy["date"])

        if ost2_new != 0 and not benefit_federal:
            district_table += "Региональная льгота: {0} ({1})".format(ost2_new, new_pharmacy["date"])

        district_table += "</td>\n  </tr>\n"

        return district_table

    def add_diff_pharmacy_to_table(self, old_pharmacy, new_pharmacy, benefit_federal):
        ost1_new = float(new_pharmacy["ost1"].replace(",", "."))
        ost2_new = float(new_pharmacy["ost2"].replace(",", "."))
        ost1_old = float(old_pharmacy["ost1"].replace(",", "."))
        ost2_old = float(old_pharmacy["ost2"].replace(",", "."))

        district_table = ""
        if (ost1_old == 0 or ost2_old == 0) and (ost1_new != ost1_old or ost2_new != ost2_old):
            district_table += "  <tr>\n"
            for pharmacy_column in [new_pharmacy["name"], self.clear_address(new_pharmacy["address"])]:
                district_table += "    <td>{0}</td>\n".format(pharmacy_column.strip())

            district_table += "    <td>"
            if ost1_new != ost1_old and benefit_federal:
                district_table += "Федеральная льгота: не было {0} -> {1} ({2}) ".format(old_pharmacy["date"],
                                                                                         ost1_new, new_pharmacy["date"])

            if ost2_new != ost2_old and not benefit_federal:
                district_table += "Региональная льгота: не было {0} -> {1} ({2})".format(old_pharmacy["date"],
                                                                                         ost2_new, new_pharmacy["date"])

            district_table += "</td>\n  </tr>\n"

        return district_table

    def get_table_for_one_position(self, name, districts_filter, benefit_federal):
        url = self.base_url.format(request.quote(name)).strip()
        if benefit_federal:
            url += "&ost1=true"
        else:
            url += "&ost2=true"

        try:
            if not os.path.isdir(self.json_data_dir):
                os.makedirs(self.json_data_dir)
        except OSError as os_error:
            print(os_error)
            return

        res_table = ""
        data_diff = ""
        for count_tries in range(1, self.count_tries):
            try:
                contents = request.urlopen(url, timeout=self.timeout).read()
                json_res = json.loads(contents.decode("utf-8"))

                if json_res["status"] == "FAILED":
                    res_table += "<h1>{0}</h1>\n<h2>{1}</h2>".format(name, self.nothing_found)
                else:
                    result = json_res["model"]["result"][0]

                    if self.data_suffix:
                        data_file_name = os.path.join(self.json_data_dir, f"json_data_{name}_{self.data_suffix}.json")
                    else:
                        data_file_name = os.path.join(self.json_data_dir, f"json_data_{name}.json")

                    try:
                        with open(data_file_name) as json_file:
                            previous_result = json.load(json_file)
                    except FileNotFoundError:
                        previous_result = {}

                    with open(data_file_name, 'w') as outfile:
                        json.dump(result, outfile, indent=4)

                    table_result = ""
                    table_diff = ""
                    for district in result["districts"]:
                        if self.check_district_name(district["name"], districts_filter):
                            table_result += self.add_district_to_table(district, benefit_federal)

                            checking_district = self.find_district_in_result(district["id"], previous_result)
                            if checking_district is None:
                                table_diff += self.add_new_district_to_table(district, benefit_federal)
                            else:
                                table_diff_pharmacy = ""
                                for pharmacy in district["apothecaries"]:
                                    checking_pharmacy = self.find_pharmacy_in_district(pharmacy["name"],
                                                                                       checking_district)
                                    if checking_pharmacy is None:
                                        table_diff_pharmacy += self.add_new_pharmacy_to_table(pharmacy, benefit_federal)
                                    else:
                                        table_diff_pharmacy += self.add_diff_pharmacy_to_table(checking_pharmacy, pharmacy, benefit_federal)

                                if table_diff_pharmacy:
                                    table_diff += add_header_district_to_table(district)
                                    table_diff += table_diff_pharmacy

                    if table_result:
                        if benefit_federal:
                            res_table += self.print_table_headers(result["name"], self.headers_benefit_federal) + table_result + "</table>"
                        else:
                            res_table += self.print_table_headers(result["name"],
                                                                  self.headers_benefit_regional) + table_result + "</table>"
                    if table_diff:
                        data_diff += self.print_table_headers(result["name"],
                                                              self.headers_diff) + table_diff + "</table>"
                break
            except error.HTTPError as e:
                print(f"error = {e.__dict__}, url = {url}")
            except error.URLError as e:
                print(f"error = {e.__dict__}, url = {url}")
            except TimeoutError as e:
                print(f"error = {e.__dict__}, url = {url}")

        return res_table, data_diff

    def get_tables_from_html_positions(self, positions, districts, benefit_federal):
        table = ""
        new_table = ""
        for position in positions:
            table_res, diff_table_res = self.get_table_for_one_position(position, districts, benefit_federal)
            if table_res:
                table += table_res
            if diff_table_res:
                new_table += diff_table_res
        return table, new_table

    @staticmethod
    def find_pharmacy_in_district(checking_name, district_for_check):
        for pharmacy in district_for_check["apothecaries"]:
            if pharmacy["name"] == checking_name:
                return pharmacy
        return None

    @staticmethod
    def print_table_headers(h1_name, headers):
        html_headers = "<h1>{0}</h1><table>\n  <tr>\n".format(h1_name)
        for column in headers:
            html_headers += "    <th>{0}</th>\n".format(column.strip())
        html_headers += "  </tr>\n"
        return html_headers

    @staticmethod
    def check_district_name(district_name, filter_data):
        clean_name = district_name.lower().replace(" район", "")
        for filter_district in filter_data:
            filter_name = filter_district.lower().replace(" район", "")
            if filter_name == clean_name:
                return True
        return False

    @staticmethod
    def clear_address(address):
        return address.split('*')[0].replace(", ,", ", ").replace("  ", " ")

    @staticmethod
    def find_district_in_result(district_id, result_for_check):
        if "districts" not in result_for_check:
            return None

        for district in result_for_check["districts"]:
            if district["id"] == district_id:
                return district
        return None
