from webdriver_auto_update.webdriver_auto_update import WebdriverAutoUpdate
from selenium import webdriver
import time
from bs4 import BeautifulSoup
import pandas as pd
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver import Chrome
from selenium.webdriver.chrome.service import Service
import threading

try:
    driver_directory = "D:/dataanalyst/webscraping/aws_project/drivers"
    driver_manager = WebdriverAutoUpdate(driver_directory)
    driver_manager.main()
except:
    print("Terjadi kesalahan saat mengatur driver!")
    

print("Pilihan:")
print("1. Scrape Shopee Toko By Continue")
print("2. Scrape Shopee Toko By MultiDriver")
print("3. Scrape Shopee (Barang) ")

try:
    scrape_choice = input("Masukkan pilihan (1/2/3): ")
except:
    print("Pilihan yang Anda masukkan tidak valid. Silakan masukkan 1, 2, atau 3.")


if scrape_choice == "1":
        num_toko = int(input("Jumlah toko yang akan di scrape: "))
        
        toko_data = []
        servis = Service('chromedriver.exe')
        driver = None  # Inisialisasi driver

        for toko_index in range(num_toko):
            cari_toko = input(f"Cari toko {toko_index + 1}: ")
            total_pages_barang = int(input(f"Jumlah halaman yang ingin anda scrape untuk toko {toko_index + 1}: "))
            file_name = input(f"Simpan file dengan nama untuk toko {toko_index + 1}: ") + ".csv"
            clean_data_choice = input("Apakah data mau di cleaning? 1.Ya/2.Tidak (pilih 1 atau 2)  ")

            driver = webdriver.Chrome(service=servis)

            login_url = "https://shopee.co.id/buyer/login?next=https%3A%2F%2Fshopee.co.id%2F"
            driver.get(login_url)
            
            time.sleep(3)

            wait = WebDriverWait(driver, 5)
            username_value = "mrkonten123@gmail.com"
            password_value = "Belibeli1"

            username = wait.until(EC.presence_of_element_located((By.NAME, 'loginKey')))
            password = wait.until(EC.presence_of_element_located((By.NAME, 'password')))

            username.send_keys(username_value)
            password.send_keys(password_value)

            login_button = wait.until(EC.element_to_be_clickable((By.CLASS_NAME, '_7w24N1')))
            login_button.click()

            time.sleep(7)

            for page in range(1, total_pages_barang + 1):
                toko_base_url = "https://shopee.co.id/{}?page={}&sortBy=pop".format(cari_toko, page)

                driver.get(toko_base_url)

                time.sleep(6)

                WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.CSS_SELECTOR, "#main")))
                time.sleep(2)

                last_height = driver.execute_script("return document.body.scrollHeight")
                for j in range(7):
                    driver.execute_script("window.scrollBy(0, 700)")
                    time.sleep(2)
                    new_height = driver.execute_script("return document.body.scrollHeight")

                soup = BeautifulSoup(driver.page_source, "html.parser")

                for item2 in soup.findAll('div', class_='UgJq78'):
                    try:
                        namatoko = item2.find('h1', class_='section-seller-overview-horizontal__portrait-name').text
                    except Exception as e:
                        namatoko = "N/A"

                for item in soup.findAll('div', class_='col-xs-2 shop-collection-view__item'):
                    try:
                        namaproduk = item.find('div', class_='odGYKR').text
                        harga = item.find('span', class_='sx+hTv').text
                        terjual = item.find('div', class_='CVzuKa').text
                    except Exception as e:
                        namaproduk = "N/A"
                        harga = "N/A"
                        terjual = "N/A"
                    toko_data.append([namatoko, namaproduk, harga, terjual])

            time.sleep(5)

        driver.quit()

        toko_df = pd.DataFrame(toko_data, columns=["Nama Toko", "Nama Produk", "Harga", "Terjual"])
        toko_df.index = range(1, len(toko_df) + 1)

        toko_df.to_csv(file_name, index=False)

        print(toko_df)
        print(f"Data telah tersimpan di file {file_name}.")

        if clean_data_choice == "1":
            try:
                toko_df['Terjual'] = toko_df['Terjual'].str.replace('Terjual', '', case=False)
                toko_df['Terjual'] = toko_df['Terjual'].str.replace(',', '')
                toko_df['Terjual'] = toko_df['Terjual'].str.replace('RB', '000').str.replace('rb', '000')

                toko_df['Harga'] = toko_df['Harga'].str.replace('Rp', '').str.replace('.', '').str.replace(',', '').astype(int)

                cleaned_file_name = file_name.replace('.csv', '_clean.csv')
                toko_df.to_csv(cleaned_file_name, index=False)
                print(toko_df)
                print(f"Data toko {cari_toko} yang telah dibersihkan tersimpan di {cleaned_file_name}")
            except Exception as e:
                print(f"Terjadi kesalahan saat membersihkan data toko {cari_toko}: {str(e)}")


elif scrape_choice == "2":
    def scrape_toko(toko_data):
        cari_toko, total_pages, file_name, clean_data_choice = toko_data
        
        toko_data = []

        options = webdriver.ChromeOptions()
        driver = webdriver.Chrome(options=options)
        driver.set_window_size(1080, 1080)

        login_url = "https://shopee.co.id/buyer/login?next=https%3A%2F%2Fshopee.co.id%2F"
        driver.get(login_url)

        time.sleep(3)
        
        wait = WebDriverWait(driver, 5)
        username_value = "mrkonten123@gmail.com"
        password_value = "Belibeli1"

        username = wait.until(EC.presence_of_element_located((By.NAME, 'loginKey')))
        password = wait.until(EC.presence_of_element_located((By.NAME, 'password')))

        username.send_keys(username_value)
        password.send_keys(password_value)

        login_button = wait.until(EC.element_to_be_clickable((By.CLASS_NAME, '_7w24N1')))
        login_button.click()

        time.sleep(10)

        for page in range(1, total_pages + 1):
            toko_base_url = "https://shopee.co.id/{}?page={}&sortBy=pop".format(cari_toko, page)
            driver.get(toko_base_url)
            time.sleep(10)

            WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.CSS_SELECTOR, "#main")))
            time.sleep(2)

            last_height = driver.execute_script("return document.body.scrollHeight")
            for j in range(7):
                driver.execute_script("window.scrollBy(0, 700)")
                time.sleep(2)
                new_height = driver.execute_script("return document.body.scrollHeight")

                if new_height == last_height:
                    break
                last_height = new_height

            soup = BeautifulSoup(driver.page_source, "html.parser")

            for item2 in soup.findAll('div', class_='UgJq78'):
                try:
                    namatoko = item2.find('h1', class_='section-seller-overview-horizontal__portrait-name').text
                except Exception as e:
                    namatoko = "N/A"

                for item in soup.findAll('div', class_='col-xs-2 shop-collection-view__item'):
                    try:
                        namaproduk = item.find('div', class_='odGYKR').text
                        harga = item.find('span', class_='sx+hTv').text
                        terjual = item.find('div', class_='CVzuKa').text
                    except Exception as e:
                        namaproduk = "N/A"
                        harga = "N/A"
                        terjual = "N/A"
                    toko_data.append([namatoko, namaproduk, harga, terjual])

                time.sleep(5)

        driver.quit()

        toko_df = pd.DataFrame(toko_data, columns=["Nama Toko", "Nama Produk", "Harga", "Terjual"])
        toko_df.index = range(1, len(toko_df) + 1)

        toko_df.to_csv(file_name, index=False)

        print(f"Data toko {cari_toko} telah tersimpan di {file_name}.")

        if clean_data_choice == "1":
            try:
                toko_df['Terjual'] = toko_df['Terjual'].str.replace('Terjual', '', case=False)
                toko_df['Terjual'] = toko_df['Terjual'].str.replace(',', '')
                toko_df['Terjual'] = toko_df['Terjual'].str.replace('RB', '000').str.replace('rb', '000')

                toko_df['Harga'] = toko_df['Harga'].str.replace('Rp', '').str.replace('.', '').str.replace(',', '').astype(int)

                cleaned_file_name = file_name.replace('.csv', '_clean.csv')
                toko_df.to_csv(cleaned_file_name, index=False)
                print(toko_df)
                print(f"Data toko {cari_toko} yang telah dibersihkan tersimpan di {cleaned_file_name}")
            except Exception as e:
                print(f"Terjadi kesalahan saat membersihkan data toko {cari_toko}: {str(e)}")


    def run_scraper():
        store_data = []
        num_stores = int(input("Mau scrape berapa toko? "))

        for i in range(num_stores):
            cari_toko = input(f"Nama toko ke-{i+1}: ")
            total_pages = int(input(f"Jumlah halaman yang ingin di-scrape untuk toko {cari_toko}: "))
            file_name = input(f"Simpan file {cari_toko} dengan nama: ") + ".csv"
            clean_data_choice = input("Apakah data mau di cleaning? 1.Ya/2.Tidak (pilih 1 atau 2)  ")
            store_data.append((cari_toko, total_pages, file_name, clean_data_choice))

        threads = []
        for data in store_data:
            thread = threading.Thread(target=scrape_toko, args=(data,))
            threads.append(thread)
            thread.start()

        for thread in threads:
            thread.join() 
    
    if __name__ == '__main__':
        run_scraper()


elif scrape_choice == "3":
    cari_barang = input("Cari barang: ")
    total_pages_barang = int(input("Jumlah halaman yang ingin Anda scrape untuk barang: "))
    file_name = input("Simpan file dengan nama: ") + ".csv"
    clean_data_choice = input("Apakah data mau di cleaning? 1.Ya/2.Tidak (pilih 1 atau 2)  ")

    barang_data = []

    servis = Service('chromedriver.exe')
    driver = webdriver.Chrome(service=servis)
    login_url = "https://shopee.co.id/buyer/login?next=https%3A%2F%2Fshopee.co.id%2F"
    driver.get(login_url)
    driver.set_window_size(1080, 1080)

    wait = WebDriverWait(driver, 5)
    username_value = "mrkonten123@gmail.com"
    password_value = "Belibeli1"

    username = wait.until(EC.presence_of_element_located((By.NAME, 'loginKey')))
    password = wait.until(EC.presence_of_element_located((By.NAME, 'password')))

    username.send_keys(username_value)
    password.send_keys(password_value)

    login_button = wait.until(EC.element_to_be_clickable((By.CLASS_NAME, '_7w24N1')))
    login_button.click()

    time.sleep(7)

    for page in range(1, total_pages_barang + 1):
        barang_base_url = "https://shopee.co.id/search?keyword={}&page={}".format(cari_barang, page)

        driver.get(barang_base_url)

        time.sleep(10)

        WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.CSS_SELECTOR, "#main")))
        time.sleep(2)

        last_height = driver.execute_script("return document.body.scrollHeight")
        for j in range(8):
            driver.execute_script("window.scrollBy(0, 500)")
            time.sleep(2)
            new_height = driver.execute_script("return document.body.scrollHeight")


        soup = BeautifulSoup(driver.page_source, "html.parser")

        for item in soup.findAll('div', class_='KMyn8J'):
            try:
                namaproduk = item.find('div', class_='bM+7UW').text
                harga = item.find('span', class_='ZEgDH9').text
                lokasi = item.find('div', class_='zGGwiV').text
                terjual = item.find('div', class_='r6HknA').text
                barang_data.append([namaproduk, harga, lokasi, terjual])
            except Exception as e:
                barang_data.append(["None", "None", "None", "None"])  

    time.sleep(2)
    driver.quit()

    barang_df = pd.DataFrame(barang_data, columns=["Nama Barang", "Harga", "Lokasi", "Terjual"])
    barang_df.index = range(1, len(barang_df) + 1)

    barang_df.to_csv(file_name, index=False)

    print(barang_df)
    print(f"Data telah tersimpan di file {file_name}.")
    print("=====================================================================================")

    if clean_data_choice == "1":
        barang_df['Terjual'] = barang_df['Terjual'].str.replace('Terjual', '', case=False)
        barang_df['Terjual'] = barang_df['Terjual'].str.replace(',', '')
        barang_df['Terjual'] = barang_df['Terjual'].str.replace('RB', '000').str.replace('rb', '000')

        barang_df['Harga'] = barang_df['Harga'].str.replace('Rp', '').str.replace('.', '').str.replace(',', '').astype(int)

        cleaned_file_name = file_name.replace('.csv', '_clean.csv')
        barang_df.to_csv(cleaned_file_name, index=False)
        print(barang_df)
        print(f"Data barang {cari_barang} yang telah dibersihkan tersimpan di {cleaned_file_name}")


    driver.quit()

else:
    print("ok")

