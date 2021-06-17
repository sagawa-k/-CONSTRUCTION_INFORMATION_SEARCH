import os
import eel
from selenium.webdriver import Chrome, ChromeOptions
import time
import pandas as pd
import datetime
from selenium.webdriver.chrome.webdriver import WebDriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.select import Select

EXP_CSV_PATH="./{datetime}.csv"

class Driver:
    ### Chromeを起動する関数
    def set_driver(self, headless_flg):
        # Chromeドライバーの読み込み
        options = ChromeOptions()

        # ヘッドレスモード（画面非表示モード）をの設定　
        if headless_flg == True:
            options.add_argument('--headless')

        # 起動オプションの設定
        options.add_argument(
            '--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.116 Safari/537.36')
        # options.add_argument('log-level=3')
        options.add_argument('--ignore-certificate-errors')
        options.add_argument('--ignore-ssl-errors')
        options.add_argument('--incognito')          # シークレットモードの設定を付　与

        # ChromeのWebDriverオブジェクトを作成する。
        return Chrome(ChromeDriverManager().install(), options=options)

class FindElems:
    def find_table_phone_number(self, th_elms, td_elms, phone_number_list):
        for th_elm,td_elm in zip(th_elms,td_elms):
            if th_elm.text == "電話番号":
                phone_number_list.append(td_elm.find_elements_by_tag_name("td")[0].text)


    def find_table_target_word(self, driver, th_elms, tr_elms, number_list, phone_number_list,
        address_list, name_list, parson_list, page_text, onclick_script_list):
        # ヘッダ行を削除
        del tr_elms[0]
        td_list = []
        # tableのthからtargetの文字列を探し一致する行のtdを返す    
        for tr_elm in tr_elms:
            for th_elm,td_elm in zip(th_elms, tr_elm.find_elements_by_tag_name("td")):
                if th_elm.text == "No.":
                    number_list.append(td_elm.text)
                elif th_elm.text == "商号又は名称":
                    name_list.append(td_elm.text)
                    td_list.append(td_elm)
                elif th_elm.text == "代表者名":
                    parson_list.append(td_elm.text)
                elif th_elm.text == "所在地":
                    address_list.append(td_elm.text)

        for td in td_list:
            onclick_script_list.append(td.find_element_by_tag_name("a").get_attribute("onclick"))

        for index, onclick_script in enumerate(onclick_script_list):
            driver.execute_script(onclick_script)
            time.sleep(1)
            table_list = driver.find_elements_by_css_selector("#input > div:nth-child(1) > table")
            self.find_table_phone_number(table_list[0].find_elements_by_tag_name("th"), table_list[0].find_elements_by_tag_name("tr"), phone_number_list)
            next_page_link  = driver.find_element_by_css_selector("#container_cont > div:nth-child(7) > p > a").get_attribute("href")
            driver.execute_script(next_page_link)
            eel.view_log_js(f"{index}件目成功")
            time.sleep(3)

        eel.view_log_js(f"{page_text}成功")    

def construction_search():
    eel.view_log_js("建設業者検索を開始")
    # driverを起動
    set_up__driver = Driver()
    driver = set_up__driver.set_driver(False)

    # 検索URL作成
    url = "https://etsuran.mlit.go.jp/TAKKEN/kensetuKensaku.do?outPutKbn=1"
    # Webサイトを開く
    driver.get(url)
    time.sleep(3)

    #csv書き出し用のリスト生成
    number_list = []
    address_list = []
    name_list = []
    phone_number_list = []
    parson_list = []
    onclick_script_list = []

    try:
        findElems = FindElems()
        # 都道府県を選択
        dropdown = driver.find_element_by_id("kenCode")
        select = Select(dropdown)
        select.select_by_index(31)

        # 検索結果表示件数を選択
        result_number = driver.find_element_by_css_selector("#dispCount")
        select_result_number = Select(result_number)
        select_result_number.select_by_index(4)

        # 検索ボタンを選択
        img_button = driver.find_element_by_css_selector("#input > div:nth-child(6) > div:nth-child(5) > img")
        img_button.click()

        # ページ一覧ドロップダウンを取得
        all_result_page_list = Select(driver.find_element_by_id("pageListNo1")).options
        # テキスト配列を作成
        page_text_list = []
        for all_result_page in all_result_page_list:
            page_text_list.append(all_result_page.text)

        for page_text in page_text_list:
            # 検索結果ページ一覧を取得
            select_result_page_list = Select(driver.find_element_by_id("pageListNo1"))
            select_result_page_list.select_by_visible_text(page_text)
            time.sleep(2)
            table_list = driver.find_elements_by_css_selector("#container_cont > table")
            for table in table_list:
                findElems.find_table_target_word(driver, table.find_elements_by_tag_name("th"), table.find_elements_by_tag_name("tr"),
                number_list, phone_number_list, address_list, name_list, parson_list, page_text, onclick_script_list)

    except Exception as e:
        print(e)
        driver.close()

    # csv出力
    now = datetime.datetime.now().strftime('%Y-%m-%d-%H-%M-%S')
    df = pd.DataFrame({"No.":number_list, "社名":name_list, "電話番号":phone_number_list,  "代表者名":parson_list, "所在地":address_list})
    df.to_csv(EXP_CSV_PATH.format(datetime=
                                now), index = False, encoding="utf-8-sig")
    eel.view_log_js("******************************")
    eel.view_log_js("書き出しが完了しました。")
    print("******************************")
    print("書き出しが完了しました。")

def building_search():
    eel.view_log_js("宅地建物取引業者検索を開始")
    # driverを起動
    set_up__driver = Driver()
    driver = set_up__driver.set_driver(False)

    # 検索URL作成
    url = "https://etsuran.mlit.go.jp/TAKKEN/takkenKensaku.do?outPutKbn=1"
    # Webサイトを開く
    driver.get(url)
    time.sleep(3)

    