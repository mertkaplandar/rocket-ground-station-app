# Atmaca Roket Takımı - Yer İstasyonu Veri İzleme Aracı

![Logo](resources/logo.png)

Bu proje, Atmaca Roket Takımı'nın yer istasyonu verilerini izlemek için geliştirilmiş bir araçtır. Uygulama, PyQt5 ve diğer Python kütüphanelerini kullanarak, gerçek zamanlı veri akışını seri port üzerinden okuyup görselleştirir ve kaydeder.

Bu programın çalışması alınan verileri json formatında yazan örnek Arduino koduna [buraya](https://github.com/mertkaplandar/rocket-ground-station-hardware-code) tıklayarak ulaşabilirsiniz.

## Özellikler

- Seri port üzerinden veri alımı ve gösterimi
- Gerçek zamanlı harita üzerinde konum gösterimi
- Gerçek zamanlı grafikler ile irtifa, basınç ve hız verilerinin izlenmesi
- Test modu ile örnek verilerin görüntülenmesi
- Veri kayıt ve dışa aktarma
- graph-viewer.py aracı ile daha önce kaydedilmiş verileri detaylı olarak grafikler üzerinde inceleme

## Gereksinimler

Bu projeyi çalıştırmak için aşağıdaki Python kütüphanelerine ihtiyaç vardır:

- PyQt5
- pyserial
- folium
- matplotlib
- PyQtWebEngine

## Kurulum

1. **Depoyu Klonlayın:**

    ```sh
    git clone https://github.com/mertkaplandar/rocket-ground-station-app.git
    cd rocket-ground-station-app
    ```

2. **Gerekli Kütüphaneleri Yükleyin:**

    ```sh
    pip install -r requirements.txt
    ```

3. **Uygulamayı Başlatın:**

    ```sh
    python app.py
    ```

## Kullanım

1. **Port ve Baund Hızı Seçimi:**
   - Uygulamayı başlattığınızda, mevcut portları ve baund hızını seçin.
   - "Bağla" butonuna tıklayın.

2. **Veri İzleme:**
   - Veri akışı başladığında, "Veriler" sekmesinde anlık verileri görebilirsiniz.
   - "Grafikler" sekmesinde irtifa, basınç ve hız grafiklerini inceleyebilirsiniz.
   - "Harita" sekmesinde konumunuzu harita üzerinde takip edebilirsiniz.

3. **Test Modu:**
   - "Test Modu" butonuna tıklayarak uygulamayı test verileri ile çalıştırabilirsiniz.


## İletişim

Herhangi bir sorunuz veya öneriniz için lütfen [Mert Kaplandar](https://github.com/mertkaplandar) ile iletişime geçin.
