from webdriver_auto_update.webdriver_auto_update import WebdriverAutoUpdate
from selenium import webdriver
import time
from bs4 import BeautifulSoup
import pandas as pd
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver import Chrome
import threading

try:
    driver_directory = "D:/dataanalyst/webscraping/aws_project/drivers"
    driver_manager = WebdriverAutoUpdate(driver_directory)
    driver_manager.main()
except:
    print("Terjadi kesalahan saat mengatur driver!")

print("Pilihan:")
print("1. Scrape Toko By Continue")
print("2. Scrape Toko By MultiDriver")
print("3. Scrape Barang Apapun")
print("4. Scrape Link Barang di Toko (include stok)")
print("5. Scrape Link Barang Apapun (include stok)")

try:
    scrape_choice = input("Masukkan pilihan (1/2/3/4/5): ")
except:
    print("Pilihan yang Anda masukkan tidak valid. Silakan masukkan 1, 2, atau 3.")

if scrape_choice == "1":
    try:
        num_stores = int(input("Mau scrape berapa toko? "))
        store_data = []

        for i in range(num_stores):
            store_name = input(f"Nama toko ke-{i+1}: ")
            total_pages = int(input(f"Jumlah halaman yang ingin di-scrape untuk toko {store_name}: "))
            file_name = input(f"Simpan file {store_name} dengan nama: ") + ".xlsx"
            clean_data_choice = input("Apakah data mau di cleaning? 1.Ya/2.Tidak (pilih nomor 1 atau 2)  ")
            store_name = store_name.replace("-", " ")
            store_name = store_name.replace(" ", "-")
            toko_base_url = f"https://www.tokopedia.com/{store_name}/product"
        
            toko_data = []
            options = webdriver.ChromeOptions()
            # options.headless = True
            driver = Chrome(options=options)
            driver.set_window_size(1080, 1080)

            for page in range(1, total_pages+1):
                toko_page_url = f"{toko_base_url}/page/{page}"
                driver.get(toko_page_url)
                time.sleep(2)
                
                WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.CSS_SELECTOR, "#zeus-root")))
                time.sleep(2)

                last_height = driver.execute_script("return document.body.scrollHeight")
                for j in range(7):
                    driver.execute_script("window.scrollBy(0, 600)")
                    time.sleep(2)
                    new_height = driver.execute_script("return document.body.scrollHeight")

                    if new_height == last_height:
                        break
                last_height = new_height

                time.sleep(2)
                toko_soup = BeautifulSoup(driver.page_source, "html.parser")

                for item in toko_soup.findAll('div', class_='css-nqwx6t'):
                    nama_toko = item.find('h1', class_='css-1g675hl').text

                    for item in toko_soup.findAll('div', class_='css-1izdl9e'):
                        namaproduk = item.find('div', class_='prd_link-product-name').text
                        harga = item.find('div', class_='prd_link-product-price').text

                        tjl = item.findAll('span', class_='css-1sgek4h')
                        if len(tjl) > 0:
                            terjual = item.find('span', class_='css-1sgek4h').text
                        else:
                            terjual = ''

                        toko_data.append((nama_toko, namaproduk, harga, terjual))

                time.sleep(1)

            driver.quit()

            toko_df = pd.DataFrame(toko_data, columns=['Nama Toko', 'Nama Produk', 'Harga', 'Terjual'])
            toko_df.to_excel(file_name, index=False)
            print(f"Data toko {store_name} telah tersimpan di {file_name}")
        
        if clean_data_choice == "1":
            try:
                toko_df['Terjual'] = toko_df['Terjual'].apply(lambda x: str(x).replace('terjual', '').replace('+', '') if isinstance(x, str) and ('terjual' in x or '+' in x) else x)
                toko_df['Terjual'] = pd.to_numeric(toko_df['Terjual'], errors='coerce')
                toko_df['Harga'] = toko_df['Harga'].str.replace('Rp', '').str.replace('.', '').astype(int) 
                toko_df = toko_df.dropna(subset=['Terjual'])
                toko_df['Terjual'] = toko_df['Terjual'].astype(int)
                toko_df = toko_df.sort_values(by='Terjual', ascending=False)
                toko_df.index = range(1, len(toko_df) + 1)

                cleaned_file_name = file_name.replace('.xlsx', '_clean.xlsx')
                toko_df.to_excel(cleaned_file_name, index=False)
                print(f"Data toko {store_name} yang telah diclean tersimpan di {cleaned_file_name}")
            except Exception as e:
                print(f"Terjadi kesalahan saat membersihkan data: {str(e)}")

        else:
            print("Data tidak di cleaning.")

    except:
        print("Terjadi kesalahan saat scrape data toko dan produk.")


elif scrape_choice == "2":
    def scrape_store_data(store_data):
        store_name, total_pages, file_name = store_data
        store_name = store_name.replace("-", " ")
        store_name = store_name.replace(" ", "-")
        toko_base_url = f"https://www.tokopedia.com/{store_name}/product"

        toko_data = []
        options = webdriver.ChromeOptions()
        # options.headless = True
        driver = Chrome(options=options)
        driver.set_window_size(1080, 1080)

        for page in range(1, total_pages+1):
            toko_page_url = f"{toko_base_url}/page/{page}"
            driver.get(toko_page_url)
            time.sleep(2)
            WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.CSS_SELECTOR, "#zeus-root")))
            time.sleep(2)

            last_height = driver.execute_script("return document.body.scrollHeight")
            for j in range(7):
                driver.execute_script("window.scrollBy(0, 700)")
                time.sleep(2)
                new_height = driver.execute_script("return document.body.scrollHeight")

                if new_height == last_height:
                    break
                last_height = new_height

            time.sleep(2)
            toko_soup = BeautifulSoup(driver.page_source, "html.parser")

            for item in toko_soup.findAll('div', class_='css-nqwx6t'):
                nama_toko = item.find('h1', class_='css-1g675hl').text

                for item in toko_soup.findAll('div', class_='css-1izdl9e'):
                    namaproduk = item.find('div', class_='prd_link-product-name').text
                    harga = item.find('div', class_='prd_link-product-price').text

                    tjl = item.findAll('span', class_='css-1sgek4h')
                    if len(tjl) > 0:
                        terjual = item.find('span', class_='css-1sgek4h').text
                    else:
                        terjual = ''

                    toko_data.append((nama_toko, namaproduk, harga, terjual))

            time.sleep(1)

        driver.quit()

        toko_df = pd.DataFrame(toko_data, columns=['Nama Toko', 'Nama Produk', 'Harga', 'Terjual'])
        toko_df.to_excel(file_name, index=False)
        print(f"Data toko {store_name} telah tersimpan di {file_name}.")

        if clean_data_choice == "1":
            try:
                toko_df['Terjual'] = toko_df['Terjual'].apply(lambda x: str(x).replace('terjual', '').replace('+', '') if isinstance(x, str) and ('terjual' in x or '+' in x) else x)
                toko_df['Terjual'] = pd.to_numeric(toko_df['Terjual'], errors='coerce')
                toko_df['Harga'] = toko_df['Harga'].str.replace('Rp', '').str.replace('.', '').astype(int) 
                toko_df = toko_df.dropna(subset=['Terjual'])
                toko_df['Terjual'] = toko_df['Terjual'].astype(int)
                toko_df = toko_df.sort_values(by='Terjual', ascending=False)
                toko_df.index = range(1, len(toko_df) + 1)

                cleaned_file_name = file_name.replace('.xlsx', '_clean.xlsx')
                toko_df.to_excel(cleaned_file_name, index=False)
                print(f"Data toko {store_name} yang telah diclean tersimpan di {cleaned_file_name}")
            except:
                print("Terjadi kesalahan saat scrape data toko dan produk.")
        
        else:
            print("Data tidak di cleaning.")

    if __name__ == "__main__":
        try:
            num_stores = int(input("Mau scrape berapa toko? "))
            store_data = []

            for i in range(num_stores):
                store_name = input(f"Nama toko ke-{i+1}: ")
                total_pages = int(input(f"Jumlah halaman yang ingin di-scrape untuk toko {store_name}: "))
                file_name = input(f"Simpan file {store_name} dengan nama: ") + ".xlsx"
                clean_data_choice = input("Apakah data mau di cleaning? 1.Ya/2.Tidak (pilih 1 atau 2)  ")
                store_data.append((store_name, total_pages, file_name))
                
            threads = []
            for data in store_data:
                thread = threading.Thread(target=scrape_store_data, args=(data,))
                threads.append(thread)
                thread.start()

            for thread in threads:
                thread.join()
        except:
            print("Terjadi kesalahan saat scrape data toko dan produk.")

elif scrape_choice == "3":
    try:
        cari_barang = input("Masukkan nama barang: ")
        total_pages_barang = int(input("Jumlah halaman yang ingin Anda scrape untuk barang: "))
        file_name = input("Simpan dengan nama file: ") 
        clean_data_choice = input("Apakah data mau di cleaning? 1.Ya/2.Tidak (pilih nomor 1 atau 2)  ")
        file_name = f"{file_name}.xlsx"
        barang_data = []

        for page in range(1, total_pages_barang + 1):
            base_barang_url = 'https://www.tokopedia.com/search?navsource=&page={}&q={}&srp_component_id=02.01.00.00&srp_page_id=&srp_page_title=&st=product'.format(page, cari_barang)

            driver = webdriver.Chrome()
            driver.get(base_barang_url)
            driver.set_window_size(1080, 1080)
            time.sleep(2)

            WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.CSS_SELECTOR, "#zeus-root")))
            time.sleep(2)

            last_height = driver.execute_script("return document.body.scrollHeight")
            for j in range(9):
                driver.execute_script("window.scrollBy(0, 700)")
                time.sleep(2)
                new_height = driver.execute_script("return document.body.scrollHeight")

            time.sleep(2)
            soup = BeautifulSoup(driver.page_source, "html.parser")
            for item in soup.findAll('div', class_='css-1izdl9e'):
                nama_produk = item.find('div', class_='prd_link-product-name').text
                harga = item.find('div', class_='prd_link-product-price').text

                tjl = item.findAll('span', class_='css-1sgek4h')
                if len(tjl) > 0:
                    terjual = item.find('span', class_='css-1sgek4h').text
                else:
                    terjual = ''

                for item2 in item.findAll('div', class_='css-1rn0irl'):
                    lokasi = item2.findAll('span', class_='css-1kdc32b')[0].text
                    toko = item2.findAll('span', class_='css-1kdc32b')[1].text

                    barang_data.append((toko, nama_produk, harga, terjual, lokasi))

            time.sleep(1)

            driver.close()

        barang_df = pd.DataFrame(barang_data, columns=['Toko', 'Nama Barang', 'Harga', 'Terjual', 'Lokasi'])
        print(barang_df)
        time.sleep(1)

        barang_df.to_excel(file_name, index=False)
        print(f"Data telah tersimpan di file {file_name}")
    
        if clean_data_choice == "1":
            try:
                barang_df['Terjual'] = barang_df['Terjual'].apply(lambda x: str(x).replace('terjual', '').replace('+', '') if isinstance(x, str) and ('terjual' in x or '+' in x) else x)
                barang_df['Terjual'] = pd.to_numeric(barang_df['Terjual'], errors='coerce')
                barang_df['Harga'] = barang_df['Harga'].str.replace('Rp', '').str.replace('.', '').astype(int) 
                barang_df = barang_df.dropna(subset=['Terjual'])
                barang_df['Terjual'] = barang_df['Terjual'].astype(int)
                
                barang_df = barang_df.sort_values(by='Terjual', ascending=False)
                barang_df.index = range(1, len(barang_df) + 1)

                cleaned_file_name = file_name.replace('.xlsx', '_clean.xlsx')
                barang_df.to_excel(cleaned_file_name, index=False)
                print(barang_df)
                print(f"Data barang {file_name} yang telah diclean tersimpan di {cleaned_file_name}")
            except Exception as e:
                print(f"Terjadi kesalahan saat clean data toko dan produk: {str(e)}")
        
        else:
            print("Data tidak di cleaning.")

    except:
        print("Terjadi kesalahan saat scrape data barang.")

if scrape_choice == "4":
    try:
        num_stores = int(input("Mau scrape berapa toko? "))
        store_data = []

        for i in range(num_stores):
            store_name = input(f"Nama toko ke-{i+1}: ")
            total_pages = int(input(f"Jumlah halaman yang ingin di-scrape untuk toko {store_name} (Scrape Link Produk): "))
            file_name = input(f"Simpan file {store_name} dengan nama: ") + ".xlsx"
            scrape_link = int(input("Apakah link mau langsung di scraping? 1.Ya 2.Tidak "))
            store_name = store_name.replace("-", " ")
            store_name = store_name.replace(" ", "-")
            toko_base_url = f"https://www.tokopedia.com/{store_name}/product"
        
            link_data_toko = []
            options = webdriver.ChromeOptions()
            driver = Chrome(options=options)
            driver.set_window_size(1080, 1080)

            try:
                for page in range(1, total_pages+1):
                    toko_page_url = f"{toko_base_url}/page/{page}"
                    driver.get(toko_page_url)
                    time.sleep(2)

                    WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.CSS_SELECTOR, "#zeus-root")))
                    time.sleep(2)
                    last_height = driver.execute_script("return document.body.scrollHeight")
                    for j in range(7):
                        driver.execute_script("window.scrollBy(0, 600)")
                        time.sleep(2)
                        new_height = driver.execute_script("return document.body.scrollHeight")

                        if new_height == last_height:
                            break
                    last_height = new_height

                    time.sleep(2)
                    toko_soup = BeautifulSoup(driver.page_source, "html.parser")
                    for item in toko_soup.findAll('div', class_='css-1izdl9e'):
                        link = item.find('a', class_='pcv3__info-content css-gwkf0u')['href']
                        link_data_toko.append((link))

                    time.sleep(1)

            except Exception as e:
                print(f"Terjadi kesalahan saat scraping link barang di toko: {str(e)}")

            driver.quit()

            toko_df = pd.DataFrame(link_data_toko, columns=['Link'])
            toko_df.to_csv(file_name, index=False)
            print(f"Data toko {store_name} telah tersimpan di {file_name}")
            
            if scrape_link == 1:
                if not file_name.endswith('.csv'):
                    file_name += '.csv'

                df = pd.read_csv(file_name)
                url_list = df['Link'].tolist()

                list_barang = []

                driver = webdriver.Chrome()

                try:
                    for url in url_list:
                        driver.get(url)
                        driver.set_window_size(1080, 1080)
                        time.sleep(4)

                        soup = BeautifulSoup(driver.page_source, "html.parser")

                        for item1 in soup.findAll('div', class_='css-1vh65tm'):
                            try:
                                nama_toko = item1.find('a', {'class': 'css-1sl4zpk'}).find('h2', {'class': 'css-1wdzqxj-unf-heading e1qvo2ff2'}).text
                            except AttributeError:
                                nama_toko = None

                        for item2 in soup.findAll('div', class_='css-jmbq56'):
                            try:
                                nama_produk = item2.find('h1', {'class': 'css-1os9jjn'}).text
                            except AttributeError:
                                nama_produk = None

                            try:
                                terjual = item2.find('p', {'class': 'css-vni7t6-unf-heading e1qvo2ff8'}).text
                            except AttributeError:
                                terjual = None

                            try:
                                harga = item2.find('div', {'class': 'price'}).text
                            except AttributeError:
                                harga = None

                            try:
                                rating = item2.find('span', {'data-testid': 'lblPDPDetailProductRatingCounter'}).text
                            except AttributeError:
                                rating = None

                        for item3 in soup.findAll('div', class_='css-1o8qs2p'):
                            try:
                                stok = item3.find('p', {'class': 'css-1yy88m3-unf-heading'}).text
                            except AttributeError:
                                stok = None

                        for item4 in soup.findAll('h2', class_='css-1pd07ge-unf-heading e1qvo2ff2'):
                            try:
                                lokasi = item4.find('b').text
                            except AttributeError:
                                lokasi = None

                        list_barang.append([nama_toko, nama_produk, harga, stok, terjual, rating, lokasi])

                except Exception as e:
                    print(f"Terjadi kesalahan saat scraping item di toko: {str(e)}")

                time.sleep(2) 

                driver.quit()
                df_barang = pd.DataFrame(list_barang, columns=['Nama Toko', 'Nama Produk', 'Harga', 'Stok', 'Terjual', 'Rating', 'Lokasi'])
                df_barang.index = df_barang.index + 1
                
                barang_file_name = file_name.replace(".csv", "_barang.xlsx")
                df_barang.to_excel(barang_file_name, index=False)
                print(f"Data toko telah tersimpan di {barang_file_name}")
        
            else:
                print("Link tidak di scraping.")

    except Exception as e:
        print(f"Terjadi kesalahan saat scrape data toko dan produk: {str(e)}")


if scrape_choice == "5":
    try:
        cari_link_barang = input("masukkan nama barang yang ingin dicari (scrape url barang): ")
        total_link_barang = int(input("Jumlah halaman yang ingin Anda scrape untuk URL barang: "))
        file_name = input("Simpan dengan nama file: ")
        clean_link = int(input("Apakah link mau di cleaning? 1.Ya 2.Tidak "))
        scrape_link = int(input("Apakah link mau langsung di scraping? 1.Ya 2.Tidak "))
        file_name = f"{file_name}.xlsx"
        link_data = []

        driver = webdriver.Chrome()
        driver.set_window_size(1080, 1080)

        for page in range(1, total_link_barang + 1):
            base_barang_url = f'https://www.tokopedia.com/search?navsource=&page={page}&q={cari_link_barang}&srp_component_id=02.01.00.00&srp_page_id=&srp_page_title=&st=product'
            driver.get(base_barang_url)
            time.sleep(2)

            WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.CSS_SELECTOR, "#zeus-root")))
            time.sleep(2)

            last_height = driver.execute_script("return document.body.scrollHeight")
            for j in range(9):
                driver.execute_script("window.scrollBy(0, 800)")
                time.sleep(2)
                new_height = driver.execute_script("return document.body.scrollHeight")

            time.sleep(2)
            soup = BeautifulSoup(driver.page_source, "html.parser")
            for item in soup.findAll('div', class_='css-1izdl9e'):
                link = item.find('a', class_='pcv3__info-content css-gwkf0u')['href']
                link_data.append(link)

            time.sleep(1)

        driver.quit()
        link_df = pd.DataFrame(link_data, columns=['Link'])
        print(link_df)
        time.sleep(1)

        link_df.to_csv(file_name, index=False)
        print(f"Data telah tersimpan di file {file_name}")

        if clean_link == 1:
            def url_click(url):
                return "https://ta.tokopedia.com/promo/v1/clicks" in url

            try:
                link_df = pd.read_csv(file_name)
                link_df['url_click'] = link_df['Link'].apply(url_click)
                link_df_clean = link_df[~link_df['url_click']]
                link_df_clean = link_df_clean.drop(columns=['url_click'])

                filename_clean = file_name.replace(".csv", "_clean.csv")
                print(f"Data bersih telah tersimpan di file {filename_clean}")
            except Exception as e:
                print(f"Terjadi kesalahan saat membersihkan data: {str(e)}")

        if scrape_link == 1:
            if not filename_clean.endswith('_clean.csv'):
                filename_clean = filename_clean.replace(".csv", "_clean.csv")

            list_barang = []

            driver = webdriver.Chrome()
            try:
                for url in link_df_clean['Link']:
                    driver.get(url)
                    driver.set_window_size(1080, 1080)
                    time.sleep(4)

                    soup = BeautifulSoup(driver.page_source, "html.parser")
                    nama_toko, nama_produk, terjual, harga, stok, rating, lokasi = None, None, None, None, None, None, None

                    try:
                        nama_toko = soup.find('a', {'class': 'css-1sl4zpk'}).find('h2', {'class': 'css-1wdzqxj-unf-heading e1qvo2ff2'}).text
                    except AttributeError:
                        pass

                    try:
                        item2 = soup.find('div', class_='css-jmbq56')
                        nama_produk = item2.find('h1', {'class': 'css-1os9jjn'}).text
                        terjual = item2.find('p', {'class': 'css-vni7t6-unf-heading e1qvo2ff8'}).text
                        harga = item2.find('div', {'class': 'price'}).text
                        rating = item2.find('span', {'data-testid': 'lblPDPDetailProductRatingCounter'}).text
                    except AttributeError:
                        pass

                    try:
                        stok = soup.find('p', {'class': 'css-1yy88m3-unf-heading'}).text
                    except AttributeError:
                        pass

                    try:
                        item3 = soup.find('h2', class_='css-1pd07ge-unf-heading e1qvo2ff2')
                        lokasi = item3.find('b').text
                    except AttributeError:
                        pass

                    list_barang.append([nama_toko, nama_produk, harga, stok, terjual, lokasi])
            except Exception as e:
                print(f"Terjadi kesalahan saat scraping item di toko: {str(e)}")

            driver.quit()
            df_barang = pd.DataFrame(list_barang, columns=['Nama Toko', 'Nama Produk', 'Harga', 'Stok', 'Terjual', 'Lokasi'])
            df_barang.index = df_barang.index + 1

            barang_file_name = filename_clean.replace("_clean.csv", "_barang.xlsx")
            df_barang.to_excel(barang_file_name, index=False)
            print(f"Data toko telah tersimpan di {barang_file_name}")

        else:
            print("Link tidak di scraping.")

    except Exception as e:
        print(f"Terjadi kesalahan: {str(e)}")

else :
    print("pilihan tidak valid, pilih 1/2/3/4/5")