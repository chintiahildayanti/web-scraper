import streamlit as st      # Mengimpor Streamlit untuk membuat aplikasi web
import pandas as pd     # Mengimpor Pandas untuk manipulasi data
import time         # Mengimpor modul time untuk mengukur durasi scraping
from scraping import *      # Mengimpor semua fungsi dari file scraping

# Judul aplikasi
st.title("Bukit Vista Property Scraper")

# Cegah scraping otomatis dengan session_state
if "scraping_started" not in st.session_state:
    st.session_state.scraping_started = False       # Inisialisasi state scraping agar tidak otomatis berjalan

# Tombol untuk memulai scraping
if st.button("Start Scraping") and not st.session_state.scraping_started:
    st.session_state.scraping_started = True        # Set state scraping menjadi True saat tombol ditekan
    st.write("Starting the scraping process...")

    start_time = time.time()  # Mencatat waktu mulai scraping

    # Daftar lokasi yang akan di-scrape dengan URL masing-masing
    locations = {
        "Bali": "https://www.bukitvista.com/city/bali",
        "Nusa Penida": "https://www.bukitvista.com/city/nusa-penida",
        "Yogyakarta": "https://www.bukitvista.com/city/yogyakarta",
    }

    all_properties = []     # List untuk menyimpan hasil scraping dari berbagai lokasi
    
    for location, url in locations.items():     # Iterasi melalui setiap lokasi
        titles = scrape_property_title(url, 5, 'item-title')        # Scrape judul properti
        image_urls = scrape_images(url, 5, 'img', 'src')        # Scrape URL gambar properti

        property_df = pd.DataFrame({        # Membuat DataFrame untuk menyimpan hasil scraping
            'title': titles,
            'image_url': image_urls
        })

        all_properties.append(property_df)      # Menambahkan DataFrame ke dalam list

    # Menggabungkan semua hasil scraping ke dalam satu DataFrame
    images_title_df = pd.concat(all_properties, axis=0).reset_index(drop=True)

    # Scraping properti Uluwatu
    uluwatu_property = pd.DataFrame({
        'title': scrape_property_title('https://www.bukitvista.com/property-type/island-life', 1, 'item-title'),
        'tags': scrape_property_title('https://www.bukitvista.com/property-type/island-life', 1, 'labels-wrap labels-right'),
        'price': scrape_property_title('https://www.bukitvista.com/property-type/island-life', 1, 'item-price item-price-text'),
        'property_type': scrape_property_title('https://www.bukitvista.com/property-type/island-life', 1, 'h-type'),
        'address_detail': scrape_property_title('https://www.bukitvista.com/property-type/island-life', 1, 'item-address'),
    })

    # Scrape URL properti
    url_df = scrape_property_links("https://www.bukitvista.com/property/")
    
    # Scraping detail properti dari URL yang diperoleh
    property_data = scrape_property_combined(url_df)
    detail_properties = pd.DataFrame([property_details(url) for url in url_df['property_links']])
    property_address_details = address_details(url_df)

    # Menggabungkan semua hasil scraping ke dalam satu DataFrame utama
    bukit_vista_property = process_bukit_vista_data(
        url_df, property_data, detail_properties, property_address_details, uluwatu_property, images_title_df
    )

    # Membersihkan dan memproses data hasil scraping
    bukit_vista_df = data_cleaning(bukit_vista_property)
    bukit_vista_df = vectorizer(bukit_vista_df)
    bukit_vista_df = tokenizer(bukit_vista_df)

    # Simpan hasil scraping ke dalam file Excel
    bukit_vista_df.to_excel('data_bukit_vista.xlsx', index=False)

    end_time = time.time()  # Mencatat waktu selesai scraping
    duration = end_time - start_time    # Menghitung durasi scraping

    # Menampilkan pesan sukses dengan durasi scraping
    st.success(f"Scraping completed in {duration:.2f} seconds.")
    st.dataframe(bukit_vista_df)        # Menampilkan DataFrame di aplikasi Streamlit
    
    # Reset state agar bisa scraping lagi setelah selesai
    st.session_state.scraping_started = False
