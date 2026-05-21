"""
Türk üniversitelerinde bulunan tüm fakülte, bölüm, sınıf ve ders referans verisi.
"""

# ─── SINIF SEVİYELERİ ────────────────────────────────────────────────────────

def get_class_levels(yil=4):
    levels = []
    for y in range(1, yil + 1):
        for sube in ["A", "B"]:
            levels.append(f"{y}. Sınıf - {sube}")
    return levels

SINIF_4YIL  = get_class_levels(4)   # Standart 4 yıllık
SINIF_5YIL  = get_class_levels(5)   # Eczacılık, Diş, Veteriner
SINIF_6YIL  = get_class_levels(6)   # Tıp

# ─── ÜNİVERSİTE YAPISI ───────────────────────────────────────────────────────
# Yapı: { "Fakülte Adı": { "Bölüm Adı": { "siniflar": [...], "yil": int } } }

UNIVERSITY_STRUCTURE = {

    # ═══════════════════════════════════════════════════════════════════════
    # 1. MÜHENDİSLİK FAKÜLTESİ
    # ═══════════════════════════════════════════════════════════════════════
    "Mühendislik Fakültesi": {
        "Bilgisayar Mühendisliği":            {"siniflar": SINIF_4YIL, "yil": 4},
        "Yazılım Mühendisliği":               {"siniflar": SINIF_4YIL, "yil": 4},
        "Elektrik-Elektronik Mühendisliği":   {"siniflar": SINIF_4YIL, "yil": 4},
        "Makine Mühendisliği":                {"siniflar": SINIF_4YIL, "yil": 4},
        "İnşaat Mühendisliği":                {"siniflar": SINIF_4YIL, "yil": 4},
        "Endüstri Mühendisliği":              {"siniflar": SINIF_4YIL, "yil": 4},
        "Kimya Mühendisliği":                 {"siniflar": SINIF_4YIL, "yil": 4},
        "Biyomedikal Mühendisliği":           {"siniflar": SINIF_4YIL, "yil": 4},
        "Çevre Mühendisliği":                 {"siniflar": SINIF_4YIL, "yil": 4},
        "Mekatronik Mühendisliği":            {"siniflar": SINIF_4YIL, "yil": 4},
        "Havacılık ve Uzay Mühendisliği":     {"siniflar": SINIF_4YIL, "yil": 4},
        "Metalurji ve Malzeme Mühendisliği":  {"siniflar": SINIF_4YIL, "yil": 4},
        "Gıda Mühendisliği":                  {"siniflar": SINIF_4YIL, "yil": 4},
        "Petrol ve Doğalgaz Mühendisliği":    {"siniflar": SINIF_4YIL, "yil": 4},
        "Jeoloji Mühendisliği":               {"siniflar": SINIF_4YIL, "yil": 4},
        "Jeofizik Mühendisliği":              {"siniflar": SINIF_4YIL, "yil": 4},
        "Maden Mühendisliği":                 {"siniflar": SINIF_4YIL, "yil": 4},
        "Tekstil Mühendisliği":               {"siniflar": SINIF_4YIL, "yil": 4},
        "Harita Mühendisliği":                {"siniflar": SINIF_4YIL, "yil": 4},
        "Nükleer Enerji Mühendisliği":        {"siniflar": SINIF_4YIL, "yil": 4},
        "Biyoloji Mühendisliği":              {"siniflar": SINIF_4YIL, "yil": 4},
        "Kontrol ve Otomasyon Mühendisliği":  {"siniflar": SINIF_4YIL, "yil": 4},
        "Sistem Mühendisliği":                {"siniflar": SINIF_4YIL, "yil": 4},
    },

    # ═══════════════════════════════════════════════════════════════════════
    # 2. TIP FAKÜLTESİ
    # ═══════════════════════════════════════════════════════════════════════
    "Tıp Fakültesi": {
        "Tıp": {"siniflar": SINIF_6YIL, "yil": 6},
    },

    # ═══════════════════════════════════════════════════════════════════════
    # 3. DİŞ HEKİMLİĞİ FAKÜLTESİ
    # ═══════════════════════════════════════════════════════════════════════
    "Diş Hekimliği Fakültesi": {
        "Diş Hekimliği": {"siniflar": SINIF_5YIL, "yil": 5},
    },

    # ═══════════════════════════════════════════════════════════════════════
    # 4. ECZACILIK FAKÜLTESİ
    # ═══════════════════════════════════════════════════════════════════════
    "Eczacılık Fakültesi": {
        "Eczacılık": {"siniflar": SINIF_5YIL, "yil": 5},
    },

    # ═══════════════════════════════════════════════════════════════════════
    # 5. VETERİNER FAKÜLTESİ
    # ═══════════════════════════════════════════════════════════════════════
    "Veteriner Fakültesi": {
        "Veteriner Hekimliği": {"siniflar": SINIF_5YIL, "yil": 5},
    },

    # ═══════════════════════════════════════════════════════════════════════
    # 6. HUKUK FAKÜLTESİ
    # ═══════════════════════════════════════════════════════════════════════
    "Hukuk Fakültesi": {
        "Hukuk": {"siniflar": SINIF_4YIL, "yil": 4},
    },

    # ═══════════════════════════════════════════════════════════════════════
    # 7. İKTİSADİ VE İDARİ BİLİMLER FAKÜLTESİ (İİBF)
    # ═══════════════════════════════════════════════════════════════════════
    "İktisadi ve İdari Bilimler Fakültesi": {
        "İktisat":                                     {"siniflar": SINIF_4YIL, "yil": 4},
        "İşletme":                                     {"siniflar": SINIF_4YIL, "yil": 4},
        "Kamu Yönetimi":                               {"siniflar": SINIF_4YIL, "yil": 4},
        "Uluslararası İlişkiler":                      {"siniflar": SINIF_4YIL, "yil": 4},
        "Maliye":                                      {"siniflar": SINIF_4YIL, "yil": 4},
        "Çalışma Ekonomisi ve Endüstri İlişkileri":    {"siniflar": SINIF_4YIL, "yil": 4},
        "Ekonometri":                                  {"siniflar": SINIF_4YIL, "yil": 4},
        "Siyaset Bilimi ve Yönetim":                   {"siniflar": SINIF_4YIL, "yil": 4},
        "Yönetim Bilişim Sistemleri":                  {"siniflar": SINIF_4YIL, "yil": 4},
        "Uluslararası Ticaret ve Lojistik":            {"siniflar": SINIF_4YIL, "yil": 4},
        "Bankacılık ve Finans":                        {"siniflar": SINIF_4YIL, "yil": 4},
        "Muhasebe ve Finansal Yönetim":                {"siniflar": SINIF_4YIL, "yil": 4},
    },

    # ═══════════════════════════════════════════════════════════════════════
    # 8. FEN-EDEBİYAT FAKÜLTESİ
    # ═══════════════════════════════════════════════════════════════════════
    "Fen-Edebiyat Fakültesi": {
        "Matematik":                       {"siniflar": SINIF_4YIL, "yil": 4},
        "Fizik":                           {"siniflar": SINIF_4YIL, "yil": 4},
        "Kimya":                           {"siniflar": SINIF_4YIL, "yil": 4},
        "Biyoloji":                        {"siniflar": SINIF_4YIL, "yil": 4},
        "İstatistik":                      {"siniflar": SINIF_4YIL, "yil": 4},
        "Moleküler Biyoloji ve Genetik":   {"siniflar": SINIF_4YIL, "yil": 4},
        "Türk Dili ve Edebiyatı":          {"siniflar": SINIF_4YIL, "yil": 4},
        "Tarih":                           {"siniflar": SINIF_4YIL, "yil": 4},
        "Coğrafya":                        {"siniflar": SINIF_4YIL, "yil": 4},
        "Psikoloji":                       {"siniflar": SINIF_4YIL, "yil": 4},
        "Sosyoloji":                       {"siniflar": SINIF_4YIL, "yil": 4},
        "Felsefe":                         {"siniflar": SINIF_4YIL, "yil": 4},
        "Arkeoloji":                       {"siniflar": SINIF_4YIL, "yil": 4},
        "Sanat Tarihi":                    {"siniflar": SINIF_4YIL, "yil": 4},
        "İngiliz Dili ve Edebiyatı":       {"siniflar": SINIF_4YIL, "yil": 4},
        "Fransız Dili ve Edebiyatı":       {"siniflar": SINIF_4YIL, "yil": 4},
        "Alman Dili ve Edebiyatı":         {"siniflar": SINIF_4YIL, "yil": 4},
        "İtalyan Dili ve Edebiyatı":       {"siniflar": SINIF_4YIL, "yil": 4},
        "İspanyol Dili ve Edebiyatı":      {"siniflar": SINIF_4YIL, "yil": 4},
        "Arap Dili ve Edebiyatı":          {"siniflar": SINIF_4YIL, "yil": 4},
        "Rus Dili ve Edebiyatı":           {"siniflar": SINIF_4YIL, "yil": 4},
        "Japon Dili ve Edebiyatı":         {"siniflar": SINIF_4YIL, "yil": 4},
        "Çin Dili ve Edebiyatı":           {"siniflar": SINIF_4YIL, "yil": 4},
        "Farsça ve Fars Dili Edebiyatı":   {"siniflar": SINIF_4YIL, "yil": 4},
    },

    # ═══════════════════════════════════════════════════════════════════════
    # 9. EĞİTİM FAKÜLTESİ
    # ═══════════════════════════════════════════════════════════════════════
    "Eğitim Fakültesi": {
        "Okul Öncesi Öğretmenliği":                          {"siniflar": SINIF_4YIL, "yil": 4},
        "Sınıf Öğretmenliği":                                {"siniflar": SINIF_4YIL, "yil": 4},
        "Türkçe Öğretmenliği":                               {"siniflar": SINIF_4YIL, "yil": 4},
        "Matematik Öğretmenliği":                            {"siniflar": SINIF_4YIL, "yil": 4},
        "Fen Bilgisi Öğretmenliği":                          {"siniflar": SINIF_4YIL, "yil": 4},
        "Sosyal Bilgiler Öğretmenliği":                      {"siniflar": SINIF_4YIL, "yil": 4},
        "İngilizce Öğretmenliği":                            {"siniflar": SINIF_4YIL, "yil": 4},
        "Almanca Öğretmenliği":                              {"siniflar": SINIF_4YIL, "yil": 4},
        "Fransızca Öğretmenliği":                            {"siniflar": SINIF_4YIL, "yil": 4},
        "Rehberlik ve Psikolojik Danışmanlık":               {"siniflar": SINIF_4YIL, "yil": 4},
        "Özel Eğitim Öğretmenliği":                          {"siniflar": SINIF_4YIL, "yil": 4},
        "Bilgisayar ve Öğretim Teknolojileri Öğretmenliği":  {"siniflar": SINIF_4YIL, "yil": 4},
        "Müzik Öğretmenliği":                                {"siniflar": SINIF_4YIL, "yil": 4},
        "Görsel Sanatlar Öğretmenliği":                      {"siniflar": SINIF_4YIL, "yil": 4},
        "Beden Eğitimi ve Spor Öğretmenliği":                {"siniflar": SINIF_4YIL, "yil": 4},
        "Din Kültürü ve Ahlak Bilgisi Öğretmenliği":         {"siniflar": SINIF_4YIL, "yil": 4},
        "Tarih Öğretmenliği":                                {"siniflar": SINIF_4YIL, "yil": 4},
        "Coğrafya Öğretmenliği":                             {"siniflar": SINIF_4YIL, "yil": 4},
        "Kimya Öğretmenliği":                                {"siniflar": SINIF_4YIL, "yil": 4},
        "Fizik Öğretmenliği":                                {"siniflar": SINIF_4YIL, "yil": 4},
        "Biyoloji Öğretmenliği":                             {"siniflar": SINIF_4YIL, "yil": 4},
        "Felsefe Grubu Öğretmenliği":                        {"siniflar": SINIF_4YIL, "yil": 4},
    },

    # ═══════════════════════════════════════════════════════════════════════
    # 10. MİMARLIK FAKÜLTESİ
    # ═══════════════════════════════════════════════════════════════════════
    "Mimarlık Fakültesi": {
        "Mimarlık":                  {"siniflar": SINIF_4YIL, "yil": 4},
        "Şehir ve Bölge Planlama":   {"siniflar": SINIF_4YIL, "yil": 4},
        "İç Mimarlık":               {"siniflar": SINIF_4YIL, "yil": 4},
        "Endüstriyel Tasarım":       {"siniflar": SINIF_4YIL, "yil": 4},
        "Peyzaj Mimarlığı":          {"siniflar": SINIF_4YIL, "yil": 4},
    },

    # ═══════════════════════════════════════════════════════════════════════
    # 11. GÜZEL SANATLAR FAKÜLTESİ
    # ═══════════════════════════════════════════════════════════════════════
    "Güzel Sanatlar Fakültesi": {
        "Resim":                  {"siniflar": SINIF_4YIL, "yil": 4},
        "Heykel":                 {"siniflar": SINIF_4YIL, "yil": 4},
        "Grafik Tasarım":         {"siniflar": SINIF_4YIL, "yil": 4},
        "Müzik":                  {"siniflar": SINIF_4YIL, "yil": 4},
        "Sahne Sanatları":        {"siniflar": SINIF_4YIL, "yil": 4},
        "Seramik":                {"siniflar": SINIF_4YIL, "yil": 4},
        "Tekstil Tasarımı":       {"siniflar": SINIF_4YIL, "yil": 4},
        "Fotoğraf ve Video":      {"siniflar": SINIF_4YIL, "yil": 4},
        "Geleneksel Türk Sanatları": {"siniflar": SINIF_4YIL, "yil": 4},
        "Animasyon":              {"siniflar": SINIF_4YIL, "yil": 4},
    },

    # ═══════════════════════════════════════════════════════════════════════
    # 12. İLETİŞİM FAKÜLTESİ
    # ═══════════════════════════════════════════════════════════════════════
    "İletişim Fakültesi": {
        "Gazetecilik":                        {"siniflar": SINIF_4YIL, "yil": 4},
        "Radyo, Televizyon ve Sinema":         {"siniflar": SINIF_4YIL, "yil": 4},
        "Halkla İlişkiler ve Reklamcılık":    {"siniflar": SINIF_4YIL, "yil": 4},
        "Yeni Medya ve İletişim":             {"siniflar": SINIF_4YIL, "yil": 4},
        "Görsel İletişim Tasarımı":           {"siniflar": SINIF_4YIL, "yil": 4},
        "İletişim Tasarımı ve Yönetimi":      {"siniflar": SINIF_4YIL, "yil": 4},
    },

    # ═══════════════════════════════════════════════════════════════════════
    # 13. SAĞLIK BİLİMLERİ FAKÜLTESİ
    # ═══════════════════════════════════════════════════════════════════════
    "Sağlık Bilimleri Fakültesi": {
        "Hemşirelik":                            {"siniflar": SINIF_4YIL, "yil": 4},
        "Ebelik":                                {"siniflar": SINIF_4YIL, "yil": 4},
        "Fizyoterapi ve Rehabilitasyon":         {"siniflar": SINIF_4YIL, "yil": 4},
        "Beslenme ve Diyetetik":                 {"siniflar": SINIF_4YIL, "yil": 4},
        "Sağlık Yönetimi":                       {"siniflar": SINIF_4YIL, "yil": 4},
        "Sosyal Hizmet":                         {"siniflar": SINIF_4YIL, "yil": 4},
        "Ergoterapi":                            {"siniflar": SINIF_4YIL, "yil": 4},
        "Dil ve Konuşma Terapisi":               {"siniflar": SINIF_4YIL, "yil": 4},
        "Odyoloji":                              {"siniflar": SINIF_4YIL, "yil": 4},
    },

    # ═══════════════════════════════════════════════════════════════════════
    # 14. SPOR BİLİMLERİ FAKÜLTESİ
    # ═══════════════════════════════════════════════════════════════════════
    "Spor Bilimleri Fakültesi": {
        "Beden Eğitimi ve Spor Öğretmenliği":  {"siniflar": SINIF_4YIL, "yil": 4},
        "Antrenörlük Eğitimi":                 {"siniflar": SINIF_4YIL, "yil": 4},
        "Spor Yöneticiliği":                   {"siniflar": SINIF_4YIL, "yil": 4},
        "Rekreasyon":                          {"siniflar": SINIF_4YIL, "yil": 4},
    },

    # ═══════════════════════════════════════════════════════════════════════
    # 15. ZİRAAT FAKÜLTESİ
    # ═══════════════════════════════════════════════════════════════════════
    "Ziraat Fakültesi": {
        "Ziraat Mühendisliği":        {"siniflar": SINIF_4YIL, "yil": 4},
        "Tarla Bitkileri":            {"siniflar": SINIF_4YIL, "yil": 4},
        "Bahçe Bitkileri":            {"siniflar": SINIF_4YIL, "yil": 4},
        "Bitki Koruma":               {"siniflar": SINIF_4YIL, "yil": 4},
        "Tarım Ekonomisi":            {"siniflar": SINIF_4YIL, "yil": 4},
        "Tarım Makineleri":           {"siniflar": SINIF_4YIL, "yil": 4},
        "Toprak Bilimi ve Bitki Besleme": {"siniflar": SINIF_4YIL, "yil": 4},
        "Biyosistem Mühendisliği":    {"siniflar": SINIF_4YIL, "yil": 4},
        "Su Ürünleri":                {"siniflar": SINIF_4YIL, "yil": 4},
        "Peyzaj Mimarlığı":           {"siniflar": SINIF_4YIL, "yil": 4},
    },

    # ═══════════════════════════════════════════════════════════════════════
    # 16. İLAHİYAT FAKÜLTESİ
    # ═══════════════════════════════════════════════════════════════════════
    "İlahiyat Fakültesi": {
        "İlahiyat":                    {"siniflar": SINIF_4YIL, "yil": 4},
        "İslam İktisadı ve Finansı":   {"siniflar": SINIF_4YIL, "yil": 4},
    },

    # ═══════════════════════════════════════════════════════════════════════
    # 17. SİYASAL BİLGİLER FAKÜLTESİ
    # ═══════════════════════════════════════════════════════════════════════
    "Siyasal Bilgiler Fakültesi": {
        "Siyaset Bilimi ve Uluslararası İlişkiler": {"siniflar": SINIF_4YIL, "yil": 4},
        "Kamu Yönetimi":                            {"siniflar": SINIF_4YIL, "yil": 4},
        "İktisat":                                  {"siniflar": SINIF_4YIL, "yil": 4},
        "İşletme":                                  {"siniflar": SINIF_4YIL, "yil": 4},
    },

    # ═══════════════════════════════════════════════════════════════════════
    # 18. TURİZM FAKÜLTESİ
    # ═══════════════════════════════════════════════════════════════════════
    "Turizm Fakültesi": {
        "Turizm İşletmeciliği":        {"siniflar": SINIF_4YIL, "yil": 4},
        "Otel Yönetimi":               {"siniflar": SINIF_4YIL, "yil": 4},
        "Seyahat İşletmeciliği":       {"siniflar": SINIF_4YIL, "yil": 4},
        "Gastronomi ve Mutfak Sanatları": {"siniflar": SINIF_4YIL, "yil": 4},
        "Rekreasyon Yönetimi":         {"siniflar": SINIF_4YIL, "yil": 4},
    },

    # ═══════════════════════════════════════════════════════════════════════
    # 19. ORMAN FAKÜLTESİ
    # ═══════════════════════════════════════════════════════════════════════
    "Orman Fakültesi": {
        "Orman Mühendisliği":       {"siniflar": SINIF_4YIL, "yil": 4},
        "Orman Endüstrisi Mühendisliği": {"siniflar": SINIF_4YIL, "yil": 4},
        "Peyzaj Mimarlığı":         {"siniflar": SINIF_4YIL, "yil": 4},
    },

    # ═══════════════════════════════════════════════════════════════════════
    # 20. SOSYAL VE BEŞERİ BİLİMLER FAKÜLTESİ
    # ═══════════════════════════════════════════════════════════════════════
    "Sosyal ve Beşeri Bilimler Fakültesi": {
        "Sosyoloji":                     {"siniflar": SINIF_4YIL, "yil": 4},
        "Psikoloji":                     {"siniflar": SINIF_4YIL, "yil": 4},
        "Tarih":                         {"siniflar": SINIF_4YIL, "yil": 4},
        "Felsefe":                       {"siniflar": SINIF_4YIL, "yil": 4},
        "Antropoloji":                   {"siniflar": SINIF_4YIL, "yil": 4},
        "Türk Dili ve Edebiyatı":        {"siniflar": SINIF_4YIL, "yil": 4},
        "Karşılaştırmalı Edebiyat":      {"siniflar": SINIF_4YIL, "yil": 4},
        "Uluslararası İlişkiler":        {"siniflar": SINIF_4YIL, "yil": 4},
        "Siyaset Bilimi":                {"siniflar": SINIF_4YIL, "yil": 4},
    },

    # ═══════════════════════════════════════════════════════════════════════
    # 21. UYGULAMALI BİLİMLER FAKÜLTESİ / MESLEK YÜKSEKOKULU
    # ═══════════════════════════════════════════════════════════════════════
    "Uygulamalı Bilimler Fakültesi": {
        "Bankacılık ve Sigortacılık":           {"siniflar": SINIF_4YIL, "yil": 4},
        "Finans ve Bankacılık":                 {"siniflar": SINIF_4YIL, "yil": 4},
        "Muhasebe ve Vergi Uygulamaları":       {"siniflar": SINIF_4YIL, "yil": 4},
        "Lojistik Yönetimi":                    {"siniflar": SINIF_4YIL, "yil": 4},
        "Pazarlama":                            {"siniflar": SINIF_4YIL, "yil": 4},
        "İnsan Kaynakları Yönetimi":            {"siniflar": SINIF_4YIL, "yil": 4},
    },

    # ═══════════════════════════════════════════════════════════════════════
    # 22. BİLGİSAYAR VE BİLİŞİM FAKÜLTESİ
    # ═══════════════════════════════════════════════════════════════════════
    "Bilgisayar ve Bilişim Fakültesi": {
        "Bilgisayar Mühendisliği":          {"siniflar": SINIF_4YIL, "yil": 4},
        "Yazılım Mühendisliği":             {"siniflar": SINIF_4YIL, "yil": 4},
        "Bilişim Sistemleri Mühendisliği":  {"siniflar": SINIF_4YIL, "yil": 4},
        "Yapay Zeka Mühendisliği":          {"siniflar": SINIF_4YIL, "yil": 4},
        "Siber Güvenlik":                   {"siniflar": SINIF_4YIL, "yil": 4},
        "Veri Bilimi":                      {"siniflar": SINIF_4YIL, "yil": 4},
    },

    # ═══════════════════════════════════════════════════════════════════════
    # 23. DENİZCİLİK FAKÜLTESİ
    # ═══════════════════════════════════════════════════════════════════════
    "Denizcilik Fakültesi": {
        "Deniz Ulaştırma İşletme Mühendisliği": {"siniflar": SINIF_4YIL, "yil": 4},
        "Gemi Makineleri İşletme Mühendisliği": {"siniflar": SINIF_4YIL, "yil": 4},
        "Gemi İnşaatı ve Gemi Makineleri Mühendisliği": {"siniflar": SINIF_4YIL, "yil": 4},
        "Deniz İşletmeciliği ve Yönetimi":      {"siniflar": SINIF_4YIL, "yil": 4},
    },

    # ═══════════════════════════════════════════════════════════════════════
    # 24. HAVACILIK VE UZAY BİLİMLERİ FAKÜLTESİ
    # ═══════════════════════════════════════════════════════════════════════
    "Havacılık ve Uzay Bilimleri Fakültesi": {
        "Havacılık ve Uzay Mühendisliği":   {"siniflar": SINIF_4YIL, "yil": 4},
        "Uçak Mühendisliği":                {"siniflar": SINIF_4YIL, "yil": 4},
        "Uzay Mühendisliği":                {"siniflar": SINIF_4YIL, "yil": 4},
        "Havacılık Yönetimi":               {"siniflar": SINIF_4YIL, "yil": 4},
        "Pilotaj":                          {"siniflar": SINIF_4YIL, "yil": 4},
        "Uçak Bakım ve Onarım Teknolojisi": {"siniflar": SINIF_4YIL, "yil": 4},
        "Hava Trafik Kontrolü":             {"siniflar": SINIF_4YIL, "yil": 4},
    },
}


# ─── BÖLÜM BAZINDA DERS LİSTELERİ ───────────────────────────────────────────
# { "Bölüm Adı": { "1. Yıl": [...], "2. Yıl": [...], "3. Yıl": [...], "4. Yıl": [...] } }

DEPARTMENT_COURSES = {

    # ── Bilgisayar Mühendisliği ──────────────────────────────────────────────
    "Bilgisayar Mühendisliği": {
        "1. Yıl": [
            {"code": "BLM101", "name": "Programlamaya Giriş",           "credits": 4, "has_project": True,  "hours": 4},
            {"code": "MAT101", "name": "Matematik I",                   "credits": 4, "has_project": False, "hours": 4},
            {"code": "FIZ101", "name": "Fizik I",                       "credits": 3, "has_project": False, "hours": 3},
            {"code": "ING101", "name": "İngilizce I",                   "credits": 2, "has_project": False, "hours": 2},
            {"code": "AIT101", "name": "Atatürk İlkeleri I",            "credits": 2, "has_project": False, "hours": 2},
            {"code": "MAT102", "name": "Matematik II",                  "credits": 4, "has_project": False, "hours": 4},
            {"code": "FIZ102", "name": "Fizik II",                      "credits": 3, "has_project": False, "hours": 3},
            {"code": "ING102", "name": "İngilizce II",                  "credits": 2, "has_project": False, "hours": 2},
            {"code": "AIT102", "name": "Atatürk İlkeleri II",           "credits": 2, "has_project": False, "hours": 2},
            {"code": "BLM102", "name": "Nesne Yönelimli Programlama",   "credits": 4, "has_project": True,  "hours": 4},
        ],
        "2. Yıl": [
            {"code": "BLM201", "name": "Veri Yapıları ve Algoritmalar", "credits": 4, "has_project": True,  "hours": 4},
            {"code": "BLM202", "name": "Ayrık Matematik",              "credits": 3, "has_project": False, "hours": 3},
            {"code": "BLM203", "name": "Bilgisayar Organizasyonu",     "credits": 3, "has_project": False, "hours": 3},
            {"code": "MAT201", "name": "Lineer Cebir",                 "credits": 3, "has_project": False, "hours": 3},
            {"code": "BLM204", "name": "Veri Tabanı Sistemleri",       "credits": 3, "has_project": True,  "hours": 3},
            {"code": "BLM205", "name": "Sayısal Analiz",               "credits": 3, "has_project": False, "hours": 3},
            {"code": "BLM206", "name": "Olasılık ve İstatistik",       "credits": 3, "has_project": False, "hours": 3},
            {"code": "BLM207", "name": "Mantıksal Tasarım",            "credits": 3, "has_project": False, "hours": 3},
        ],
        "3. Yıl": [
            {"code": "BLM301", "name": "İşletim Sistemleri",           "credits": 3, "has_project": True,  "hours": 3},
            {"code": "BLM302", "name": "Bilgisayar Ağları",            "credits": 3, "has_project": False, "hours": 3},
            {"code": "BLM303", "name": "Yazılım Mühendisliği",         "credits": 3, "has_project": True,  "hours": 3},
            {"code": "BLM304", "name": "Yapay Zeka",                   "credits": 3, "has_project": True,  "hours": 3},
            {"code": "BLM305", "name": "Web Programlama",              "credits": 3, "has_project": True,  "hours": 3},
            {"code": "BLM306", "name": "Mikroişlemciler",              "credits": 3, "has_project": False, "hours": 3},
            {"code": "BLM307", "name": "Teori ve Hesaplama",           "credits": 3, "has_project": False, "hours": 3},
            {"code": "BLM308", "name": "Görüntü İşleme",              "credits": 3, "has_project": True,  "hours": 3},
        ],
        "4. Yıl": [
            {"code": "BLM401", "name": "Bitirme Projesi I",            "credits": 4, "has_project": True,  "hours": 4},
            {"code": "BLM402", "name": "Veri Madenciliği",             "credits": 3, "has_project": True,  "hours": 3},
            {"code": "BLM403", "name": "Derin Öğrenme",                "credits": 3, "has_project": True,  "hours": 3},
            {"code": "BLM404", "name": "Bulut Bilişim",                "credits": 3, "has_project": False, "hours": 3},
            {"code": "BLM405", "name": "Bitirme Projesi II",           "credits": 4, "has_project": True,  "hours": 4},
            {"code": "BLM406", "name": "Siber Güvenlik",               "credits": 3, "has_project": False, "hours": 3},
            {"code": "BLM407", "name": "Mobil Uygulama Geliştirme",    "credits": 3, "has_project": True,  "hours": 3},
        ],
    },

    # ── Yazılım Mühendisliği ─────────────────────────────────────────────────
    "Yazılım Mühendisliği": {
        "1. Yıl": [
            {"code": "YZM101", "name": "Programlamaya Giriş",            "credits": 4, "has_project": True,  "hours": 4},
            {"code": "MAT101", "name": "Matematik I",                    "credits": 4, "has_project": False, "hours": 4},
            {"code": "FIZ101", "name": "Fizik I",                        "credits": 3, "has_project": False, "hours": 3},
            {"code": "ING101", "name": "İngilizce I",                    "credits": 2, "has_project": False, "hours": 2},
            {"code": "AIT101", "name": "Atatürk İlkeleri I",             "credits": 2, "has_project": False, "hours": 2},
            {"code": "YZM102", "name": "Nesne Yönelimli Programlama",    "credits": 4, "has_project": True,  "hours": 4},
            {"code": "MAT102", "name": "Matematik II",                   "credits": 4, "has_project": False, "hours": 4},
            {"code": "AIT102", "name": "Atatürk İlkeleri II",            "credits": 2, "has_project": False, "hours": 2},
        ],
        "2. Yıl": [
            {"code": "YZM201", "name": "Veri Yapıları",                  "credits": 4, "has_project": True,  "hours": 4},
            {"code": "YZM202", "name": "Veri Tabanı Yönetimi",           "credits": 3, "has_project": True,  "hours": 3},
            {"code": "YZM203", "name": "Yazılım Gereksinimleri",         "credits": 3, "has_project": False, "hours": 3},
            {"code": "YZM204", "name": "Ayrık Matematik",                "credits": 3, "has_project": False, "hours": 3},
            {"code": "YZM205", "name": "İleri Programlama",              "credits": 4, "has_project": True,  "hours": 4},
            {"code": "YZM206", "name": "Olasılık ve İstatistik",         "credits": 3, "has_project": False, "hours": 3},
        ],
        "3. Yıl": [
            {"code": "YZM301", "name": "Yazılım Mimarileri",             "credits": 3, "has_project": True,  "hours": 3},
            {"code": "YZM302", "name": "Yazılım Test ve Doğrulama",      "credits": 3, "has_project": True,  "hours": 3},
            {"code": "YZM303", "name": "Web Uygulama Geliştirme",        "credits": 3, "has_project": True,  "hours": 3},
            {"code": "YZM304", "name": "İşletim Sistemleri",             "credits": 3, "has_project": False, "hours": 3},
            {"code": "YZM305", "name": "Bilgisayar Ağları",              "credits": 3, "has_project": False, "hours": 3},
            {"code": "YZM306", "name": "Yapay Zeka",                     "credits": 3, "has_project": True,  "hours": 3},
        ],
        "4. Yıl": [
            {"code": "YZM401", "name": "Yazılım Projesi I",              "credits": 4, "has_project": True,  "hours": 4},
            {"code": "YZM402", "name": "Yazılım Projesi II",             "credits": 4, "has_project": True,  "hours": 4},
            {"code": "YZM403", "name": "DevOps ve Çevik Geliştirme",     "credits": 3, "has_project": True,  "hours": 3},
            {"code": "YZM404", "name": "Mobil Yazılım Geliştirme",       "credits": 3, "has_project": True,  "hours": 3},
            {"code": "YZM405", "name": "Bulut Teknolojileri",            "credits": 3, "has_project": False, "hours": 3},
        ],
    },

    # ── Elektrik-Elektronik Mühendisliği ────────────────────────────────────
    "Elektrik-Elektronik Mühendisliği": {
        "1. Yıl": [
            {"code": "EEM101", "name": "Devre Analizi I",               "credits": 4, "has_project": False, "hours": 4},
            {"code": "MAT101", "name": "Matematik I",                   "credits": 4, "has_project": False, "hours": 4},
            {"code": "FIZ101", "name": "Fizik I",                       "credits": 3, "has_project": False, "hours": 3},
            {"code": "ING101", "name": "İngilizce I",                   "credits": 2, "has_project": False, "hours": 2},
            {"code": "AIT101", "name": "Atatürk İlkeleri I",            "credits": 2, "has_project": False, "hours": 2},
            {"code": "EEM102", "name": "Devre Analizi II",              "credits": 4, "has_project": False, "hours": 4},
            {"code": "MAT102", "name": "Matematik II",                  "credits": 4, "has_project": False, "hours": 4},
            {"code": "FIZ102", "name": "Fizik II",                      "credits": 3, "has_project": False, "hours": 3},
        ],
        "2. Yıl": [
            {"code": "EEM201", "name": "Elektronik I",                  "credits": 4, "has_project": True,  "hours": 4},
            {"code": "EEM202", "name": "Elektromanyetik Alan",          "credits": 3, "has_project": False, "hours": 3},
            {"code": "EEM203", "name": "Sayısal Elektronik",            "credits": 3, "has_project": True,  "hours": 3},
            {"code": "MAT201", "name": "Diferansiyel Denklemler",       "credits": 3, "has_project": False, "hours": 3},
            {"code": "EEM204", "name": "Elektronik II",                 "credits": 4, "has_project": True,  "hours": 4},
            {"code": "EEM205", "name": "Olasılık ve Stokastik Süreçler","credits": 3, "has_project": False, "hours": 3},
        ],
        "3. Yıl": [
            {"code": "EEM301", "name": "Sinyal ve Sistemler",           "credits": 3, "has_project": False, "hours": 3},
            {"code": "EEM302", "name": "Haberleşme Teorisi",            "credits": 3, "has_project": False, "hours": 3},
            {"code": "EEM303", "name": "Kontrol Sistemleri",            "credits": 3, "has_project": True,  "hours": 3},
            {"code": "EEM304", "name": "Enerji Sistemleri",             "credits": 3, "has_project": False, "hours": 3},
            {"code": "EEM305", "name": "Mikroelektronik",               "credits": 3, "has_project": True,  "hours": 3},
            {"code": "EEM306", "name": "Sayısal Sinyal İşleme",         "credits": 3, "has_project": True,  "hours": 3},
        ],
        "4. Yıl": [
            {"code": "EEM401", "name": "Bitirme Projesi I",             "credits": 4, "has_project": True,  "hours": 4},
            {"code": "EEM402", "name": "Bitirme Projesi II",            "credits": 4, "has_project": True,  "hours": 4},
            {"code": "EEM403", "name": "Anten ve Yayılma",              "credits": 3, "has_project": False, "hours": 3},
            {"code": "EEM404", "name": "Güç Elektroniği",               "credits": 3, "has_project": True,  "hours": 3},
            {"code": "EEM405", "name": "Gömülü Sistemler",              "credits": 3, "has_project": True,  "hours": 3},
        ],
    },

    # ── Makine Mühendisliği ──────────────────────────────────────────────────
    "Makine Mühendisliği": {
        "1. Yıl": [
            {"code": "MAK101", "name": "Mühendislik Çizimi",           "credits": 3, "has_project": True,  "hours": 3},
            {"code": "MAT101", "name": "Matematik I",                  "credits": 4, "has_project": False, "hours": 4},
            {"code": "FIZ101", "name": "Fizik I",                      "credits": 3, "has_project": False, "hours": 3},
            {"code": "KIM101", "name": "Kimya",                        "credits": 3, "has_project": False, "hours": 3},
            {"code": "AIT101", "name": "Atatürk İlkeleri I",           "credits": 2, "has_project": False, "hours": 2},
            {"code": "MAK102", "name": "Statik",                       "credits": 3, "has_project": False, "hours": 3},
            {"code": "MAT102", "name": "Matematik II",                 "credits": 4, "has_project": False, "hours": 4},
            {"code": "FIZ102", "name": "Fizik II",                     "credits": 3, "has_project": False, "hours": 3},
        ],
        "2. Yıl": [
            {"code": "MAK201", "name": "Dinamik",                      "credits": 3, "has_project": False, "hours": 3},
            {"code": "MAK202", "name": "Mukavemet",                    "credits": 4, "has_project": False, "hours": 4},
            {"code": "MAK203", "name": "Termodinamik",                 "credits": 4, "has_project": False, "hours": 4},
            {"code": "MAT201", "name": "Diferansiyel Denklemler",      "credits": 3, "has_project": False, "hours": 3},
            {"code": "MAK204", "name": "Malzeme Bilimi",               "credits": 3, "has_project": False, "hours": 3},
            {"code": "MAK205", "name": "Makine Elemanları I",          "credits": 3, "has_project": True,  "hours": 3},
        ],
        "3. Yıl": [
            {"code": "MAK301", "name": "Akışkanlar Mekaniği",          "credits": 4, "has_project": False, "hours": 4},
            {"code": "MAK302", "name": "Isı Transferi",                "credits": 3, "has_project": False, "hours": 3},
            {"code": "MAK303", "name": "Makine Elemanları II",         "credits": 3, "has_project": True,  "hours": 3},
            {"code": "MAK304", "name": "Üretim Yöntemleri",            "credits": 3, "has_project": True,  "hours": 3},
            {"code": "MAK305", "name": "Kontrol Teorisi",              "credits": 3, "has_project": False, "hours": 3},
            {"code": "MAK306", "name": "Titreşimler",                  "credits": 3, "has_project": False, "hours": 3},
        ],
        "4. Yıl": [
            {"code": "MAK401", "name": "Bitirme Projesi I",            "credits": 4, "has_project": True,  "hours": 4},
            {"code": "MAK402", "name": "Bitirme Projesi II",           "credits": 4, "has_project": True,  "hours": 4},
            {"code": "MAK403", "name": "Sonlu Elemanlar Yöntemi",      "credits": 3, "has_project": True,  "hours": 3},
            {"code": "MAK404", "name": "İçten Yanmalı Motorlar",       "credits": 3, "has_project": False, "hours": 3},
            {"code": "MAK405", "name": "Enerji Sistemleri",            "credits": 3, "has_project": False, "hours": 3},
        ],
    },

    # ── İnşaat Mühendisliği ──────────────────────────────────────────────────
    "İnşaat Mühendisliği": {
        "1. Yıl": [
            {"code": "INS101", "name": "Mühendislik Çizimi",           "credits": 3, "has_project": True,  "hours": 3},
            {"code": "MAT101", "name": "Matematik I",                  "credits": 4, "has_project": False, "hours": 4},
            {"code": "FIZ101", "name": "Fizik I",                      "credits": 3, "has_project": False, "hours": 3},
            {"code": "KIM101", "name": "Kimya",                        "credits": 3, "has_project": False, "hours": 3},
            {"code": "AIT101", "name": "Atatürk İlkeleri I",           "credits": 2, "has_project": False, "hours": 2},
            {"code": "INS102", "name": "Statik",                       "credits": 3, "has_project": False, "hours": 3},
            {"code": "MAT102", "name": "Matematik II",                 "credits": 4, "has_project": False, "hours": 4},
        ],
        "2. Yıl": [
            {"code": "INS201", "name": "Mukavemet",                    "credits": 4, "has_project": False, "hours": 4},
            {"code": "INS202", "name": "Yapı Mekaniği I",              "credits": 3, "has_project": False, "hours": 3},
            {"code": "INS203", "name": "Zemin Mekaniği",               "credits": 3, "has_project": False, "hours": 3},
            {"code": "INS204", "name": "Akışkanlar Mekaniği",          "credits": 3, "has_project": False, "hours": 3},
            {"code": "INS205", "name": "İnşaat Malzemeleri",           "credits": 3, "has_project": True,  "hours": 3},
            {"code": "INS206", "name": "Hidroloji",                    "credits": 3, "has_project": False, "hours": 3},
        ],
        "3. Yıl": [
            {"code": "INS301", "name": "Yapı Mekaniği II",             "credits": 3, "has_project": False, "hours": 3},
            {"code": "INS302", "name": "Betonarme I",                  "credits": 4, "has_project": True,  "hours": 4},
            {"code": "INS303", "name": "Çelik Yapılar",                "credits": 3, "has_project": True,  "hours": 3},
            {"code": "INS304", "name": "Ulaşım Mühendisliği",          "credits": 3, "has_project": False, "hours": 3},
            {"code": "INS305", "name": "Su Yapıları",                  "credits": 3, "has_project": False, "hours": 3},
        ],
        "4. Yıl": [
            {"code": "INS401", "name": "Bitirme Projesi I",            "credits": 4, "has_project": True,  "hours": 4},
            {"code": "INS402", "name": "Bitirme Projesi II",           "credits": 4, "has_project": True,  "hours": 4},
            {"code": "INS403", "name": "Betonarme II",                 "credits": 3, "has_project": True,  "hours": 3},
            {"code": "INS404", "name": "Deprem Mühendisliği",          "credits": 3, "has_project": False, "hours": 3},
            {"code": "INS405", "name": "İnşaat Proje Yönetimi",        "credits": 3, "has_project": True,  "hours": 3},
        ],
    },

    # ── Endüstri Mühendisliği ────────────────────────────────────────────────
    "Endüstri Mühendisliği": {
        "1. Yıl": [
            {"code": "END101", "name": "Mühendisliğe Giriş",           "credits": 2, "has_project": False, "hours": 2},
            {"code": "MAT101", "name": "Matematik I",                  "credits": 4, "has_project": False, "hours": 4},
            {"code": "FIZ101", "name": "Fizik I",                      "credits": 3, "has_project": False, "hours": 3},
            {"code": "ING101", "name": "İngilizce I",                  "credits": 2, "has_project": False, "hours": 2},
            {"code": "AIT101", "name": "Atatürk İlkeleri I",           "credits": 2, "has_project": False, "hours": 2},
            {"code": "END102", "name": "Programlamaya Giriş",          "credits": 3, "has_project": True,  "hours": 3},
            {"code": "MAT102", "name": "Matematik II",                 "credits": 4, "has_project": False, "hours": 4},
        ],
        "2. Yıl": [
            {"code": "END201", "name": "İstatistik ve Olasılık",       "credits": 3, "has_project": False, "hours": 3},
            {"code": "END202", "name": "Üretim Yönetimi",              "credits": 3, "has_project": False, "hours": 3},
            {"code": "END203", "name": "Yöneylem Araştırması I",       "credits": 3, "has_project": False, "hours": 3},
            {"code": "END204", "name": "İş Etüdü",                    "credits": 3, "has_project": True,  "hours": 3},
            {"code": "END205", "name": "Mühendislik Ekonomisi",        "credits": 3, "has_project": False, "hours": 3},
            {"code": "END206", "name": "Yöneylem Araştırması II",      "credits": 3, "has_project": True,  "hours": 3},
        ],
        "3. Yıl": [
            {"code": "END301", "name": "Kalite Yönetimi",              "credits": 3, "has_project": True,  "hours": 3},
            {"code": "END302", "name": "Simülasyon",                   "credits": 3, "has_project": True,  "hours": 3},
            {"code": "END303", "name": "Stok Yönetimi",                "credits": 3, "has_project": False, "hours": 3},
            {"code": "END304", "name": "Lojistik ve Tedarik Zinciri",  "credits": 3, "has_project": False, "hours": 3},
            {"code": "END305", "name": "Ergonomi",                     "credits": 3, "has_project": False, "hours": 3},
        ],
        "4. Yıl": [
            {"code": "END401", "name": "Bitirme Projesi I",            "credits": 4, "has_project": True,  "hours": 4},
            {"code": "END402", "name": "Bitirme Projesi II",           "credits": 4, "has_project": True,  "hours": 4},
            {"code": "END403", "name": "İleri Üretim Sistemleri",      "credits": 3, "has_project": False, "hours": 3},
            {"code": "END404", "name": "Çok Kriterli Karar Verme",     "credits": 3, "has_project": True,  "hours": 3},
        ],
    },

    # ── Tıp ──────────────────────────────────────────────────────────────────
    "Tıp": {
        "1. Yıl": [
            {"code": "TIP101", "name": "Anatomi I",                    "credits": 6, "has_project": False, "hours": 8},
            {"code": "TIP102", "name": "Tıbbi Biyoloji",               "credits": 4, "has_project": False, "hours": 4},
            {"code": "TIP103", "name": "Tıbbi Biyokimya I",            "credits": 4, "has_project": False, "hours": 4},
            {"code": "TIP104", "name": "Histoloji ve Embriyoloji I",   "credits": 4, "has_project": False, "hours": 4},
            {"code": "AIT101", "name": "Atatürk İlkeleri",             "credits": 2, "has_project": False, "hours": 2},
            {"code": "TIP105", "name": "Anatomi II",                   "credits": 6, "has_project": False, "hours": 8},
            {"code": "TIP106", "name": "Tıbbi Biyokimya II",           "credits": 4, "has_project": False, "hours": 4},
        ],
        "2. Yıl": [
            {"code": "TIP201", "name": "Fizyoloji I",                  "credits": 6, "has_project": False, "hours": 8},
            {"code": "TIP202", "name": "Mikrobiyoloji I",              "credits": 4, "has_project": False, "hours": 4},
            {"code": "TIP203", "name": "Patoloji I",                   "credits": 4, "has_project": False, "hours": 4},
            {"code": "TIP204", "name": "Farmakoloji I",                "credits": 4, "has_project": False, "hours": 4},
            {"code": "TIP205", "name": "Fizyoloji II",                 "credits": 6, "has_project": False, "hours": 8},
            {"code": "TIP206", "name": "Mikrobiyoloji II",             "credits": 4, "has_project": False, "hours": 4},
        ],
        "3. Yıl": [
            {"code": "TIP301", "name": "İç Hastalıkları I",            "credits": 6, "has_project": False, "hours": 8},
            {"code": "TIP302", "name": "Genel Cerrahi I",              "credits": 6, "has_project": False, "hours": 8},
            {"code": "TIP303", "name": "Patoloji II",                  "credits": 4, "has_project": False, "hours": 4},
            {"code": "TIP304", "name": "Farmakoloji II",               "credits": 4, "has_project": False, "hours": 4},
        ],
        "4. Yıl": [
            {"code": "TIP401", "name": "İç Hastalıkları II",           "credits": 6, "has_project": False, "hours": 8},
            {"code": "TIP402", "name": "Genel Cerrahi II",             "credits": 6, "has_project": False, "hours": 8},
            {"code": "TIP403", "name": "Pediatri",                     "credits": 4, "has_project": False, "hours": 6},
            {"code": "TIP404", "name": "Kadın Hastalıkları",           "credits": 4, "has_project": False, "hours": 6},
        ],
        "5. Yıl": [
            {"code": "TIP501", "name": "Psikiyatri",                   "credits": 4, "has_project": False, "hours": 6},
            {"code": "TIP502", "name": "Nöroloji",                     "credits": 4, "has_project": False, "hours": 6},
            {"code": "TIP503", "name": "Kardiyoloji",                  "credits": 4, "has_project": False, "hours": 6},
            {"code": "TIP504", "name": "Ortopedi",                     "credits": 4, "has_project": False, "hours": 6},
        ],
        "6. Yıl": [
            {"code": "TIP601", "name": "İntörnlük - İç Hastalıkları",  "credits": 8, "has_project": False, "hours": 10},
            {"code": "TIP602", "name": "İntörnlük - Cerrahi",          "credits": 8, "has_project": False, "hours": 10},
            {"code": "TIP603", "name": "İntörnlük - Pediatri",         "credits": 6, "has_project": False, "hours": 8},
            {"code": "TIP604", "name": "İntörnlük - Kadın Doğum",      "credits": 6, "has_project": False, "hours": 8},
        ],
    },

    # ── Hukuk ─────────────────────────────────────────────────────────────────
    "Hukuk": {
        "1. Yıl": [
            {"code": "HUK101", "name": "Hukuka Giriş",                 "credits": 3, "has_project": False, "hours": 3},
            {"code": "HUK102", "name": "Medeni Hukuk I",               "credits": 4, "has_project": False, "hours": 4},
            {"code": "HUK103", "name": "Anayasa Hukuku I",             "credits": 4, "has_project": False, "hours": 4},
            {"code": "HUK104", "name": "Roma Hukuku",                  "credits": 3, "has_project": False, "hours": 3},
            {"code": "AIT101", "name": "Atatürk İlkeleri I",           "credits": 2, "has_project": False, "hours": 2},
            {"code": "HUK105", "name": "Medeni Hukuk II",              "credits": 4, "has_project": False, "hours": 4},
            {"code": "HUK106", "name": "Anayasa Hukuku II",            "credits": 4, "has_project": False, "hours": 4},
        ],
        "2. Yıl": [
            {"code": "HUK201", "name": "Borçlar Hukuku Genel",         "credits": 4, "has_project": False, "hours": 4},
            {"code": "HUK202", "name": "İdare Hukuku I",               "credits": 4, "has_project": False, "hours": 4},
            {"code": "HUK203", "name": "Ceza Hukuku Genel",            "credits": 4, "has_project": False, "hours": 4},
            {"code": "HUK204", "name": "Ticaret Hukuku I",             "credits": 4, "has_project": False, "hours": 4},
            {"code": "HUK205", "name": "Borçlar Hukuku Özel",          "credits": 4, "has_project": False, "hours": 4},
            {"code": "HUK206", "name": "İdare Hukuku II",              "credits": 4, "has_project": False, "hours": 4},
        ],
        "3. Yıl": [
            {"code": "HUK301", "name": "Medeni Usul Hukuku",           "credits": 4, "has_project": False, "hours": 4},
            {"code": "HUK302", "name": "İş Hukuku",                   "credits": 3, "has_project": False, "hours": 3},
            {"code": "HUK303", "name": "Ticaret Hukuku II",            "credits": 4, "has_project": False, "hours": 4},
            {"code": "HUK304", "name": "Ceza Muhakemesi Hukuku",       "credits": 4, "has_project": False, "hours": 4},
            {"code": "HUK305", "name": "Devletler Özel Hukuku",        "credits": 3, "has_project": False, "hours": 3},
        ],
        "4. Yıl": [
            {"code": "HUK401", "name": "İcra ve İflas Hukuku",         "credits": 4, "has_project": False, "hours": 4},
            {"code": "HUK402", "name": "Vergi Hukuku",                 "credits": 3, "has_project": False, "hours": 3},
            {"code": "HUK403", "name": "Devletler Genel Hukuku",       "credits": 3, "has_project": False, "hours": 3},
            {"code": "HUK404", "name": "Avrupa Birliği Hukuku",        "credits": 3, "has_project": False, "hours": 3},
            {"code": "HUK405", "name": "Miras Hukuku",                 "credits": 3, "has_project": False, "hours": 3},
        ],
    },

    # ── İktisat ──────────────────────────────────────────────────────────────
    "İktisat": {
        "1. Yıl": [
            {"code": "IKT101", "name": "Mikro İktisat I",              "credits": 4, "has_project": False, "hours": 4},
            {"code": "MAT101", "name": "Matematik I",                  "credits": 4, "has_project": False, "hours": 4},
            {"code": "IKT102", "name": "Muhasebe I",                   "credits": 3, "has_project": False, "hours": 3},
            {"code": "AIT101", "name": "Atatürk İlkeleri I",           "credits": 2, "has_project": False, "hours": 2},
            {"code": "ING101", "name": "İngilizce I",                  "credits": 2, "has_project": False, "hours": 2},
            {"code": "IKT103", "name": "Makro İktisat I",              "credits": 4, "has_project": False, "hours": 4},
            {"code": "MAT102", "name": "Matematik II",                 "credits": 4, "has_project": False, "hours": 4},
        ],
        "2. Yıl": [
            {"code": "IKT201", "name": "Mikro İktisat II",             "credits": 4, "has_project": False, "hours": 4},
            {"code": "IKT202", "name": "Makro İktisat II",             "credits": 4, "has_project": False, "hours": 4},
            {"code": "IKT203", "name": "İstatistik",                   "credits": 3, "has_project": False, "hours": 3},
            {"code": "IKT204", "name": "Para Teorisi ve Politikası",   "credits": 3, "has_project": False, "hours": 3},
            {"code": "IKT205", "name": "Ekonometri I",                 "credits": 3, "has_project": True,  "hours": 3},
        ],
        "3. Yıl": [
            {"code": "IKT301", "name": "Uluslararası İktisat",         "credits": 3, "has_project": False, "hours": 3},
            {"code": "IKT302", "name": "Kalkınma İktisadı",            "credits": 3, "has_project": False, "hours": 3},
            {"code": "IKT303", "name": "Ekonometri II",                "credits": 3, "has_project": True,  "hours": 3},
            {"code": "IKT304", "name": "Maliye Teorisi",               "credits": 3, "has_project": False, "hours": 3},
        ],
        "4. Yıl": [
            {"code": "IKT401", "name": "Bitirme Ödevi",                "credits": 4, "has_project": True,  "hours": 4},
            {"code": "IKT402", "name": "Oyun Teorisi",                 "credits": 3, "has_project": False, "hours": 3},
            {"code": "IKT403", "name": "Finansal İktisat",             "credits": 3, "has_project": False, "hours": 3},
        ],
    },

    # ── İşletme ──────────────────────────────────────────────────────────────
    "İşletme": {
        "1. Yıl": [
            {"code": "ISL101", "name": "İşletmeye Giriş",              "credits": 3, "has_project": False, "hours": 3},
            {"code": "MAT101", "name": "Matematik",                    "credits": 4, "has_project": False, "hours": 4},
            {"code": "ISL102", "name": "Genel Muhasebe I",             "credits": 4, "has_project": False, "hours": 4},
            {"code": "AIT101", "name": "Atatürk İlkeleri I",           "credits": 2, "has_project": False, "hours": 2},
            {"code": "ING101", "name": "İngilizce I",                  "credits": 2, "has_project": False, "hours": 2},
            {"code": "ISL103", "name": "İktisada Giriş",               "credits": 3, "has_project": False, "hours": 3},
            {"code": "ISL104", "name": "Genel Muhasebe II",            "credits": 4, "has_project": False, "hours": 4},
        ],
        "2. Yıl": [
            {"code": "ISL201", "name": "Yönetim ve Organizasyon",      "credits": 3, "has_project": False, "hours": 3},
            {"code": "ISL202", "name": "Pazarlama",                    "credits": 3, "has_project": False, "hours": 3},
            {"code": "ISL203", "name": "İstatistik",                   "credits": 3, "has_project": False, "hours": 3},
            {"code": "ISL204", "name": "Finansman I",                  "credits": 3, "has_project": False, "hours": 3},
            {"code": "ISL205", "name": "Maliyet Muhasebesi",           "credits": 3, "has_project": False, "hours": 3},
        ],
        "3. Yıl": [
            {"code": "ISL301", "name": "İnsan Kaynakları Yönetimi",    "credits": 3, "has_project": False, "hours": 3},
            {"code": "ISL302", "name": "Finansman II",                 "credits": 3, "has_project": False, "hours": 3},
            {"code": "ISL303", "name": "Üretim Yönetimi",              "credits": 3, "has_project": False, "hours": 3},
            {"code": "ISL304", "name": "Stratejik Yönetim",            "credits": 3, "has_project": False, "hours": 3},
        ],
        "4. Yıl": [
            {"code": "ISL401", "name": "Bitirme Projesi",              "credits": 4, "has_project": True,  "hours": 4},
            {"code": "ISL402", "name": "Girişimcilik",                 "credits": 3, "has_project": True,  "hours": 3},
            {"code": "ISL403", "name": "İş Etiği",                    "credits": 3, "has_project": False, "hours": 3},
        ],
    },

    # ── Psikoloji ─────────────────────────────────────────────────────────────
    "Psikoloji": {
        "1. Yıl": [
            {"code": "PSI101", "name": "Psikolojiye Giriş I",          "credits": 4, "has_project": False, "hours": 4},
            {"code": "PSI102", "name": "Sosyolojiye Giriş",            "credits": 3, "has_project": False, "hours": 3},
            {"code": "PSI103", "name": "Felsefeye Giriş",              "credits": 3, "has_project": False, "hours": 3},
            {"code": "AIT101", "name": "Atatürk İlkeleri I",           "credits": 2, "has_project": False, "hours": 2},
            {"code": "PSI104", "name": "Psikolojiye Giriş II",         "credits": 4, "has_project": False, "hours": 4},
            {"code": "PSI105", "name": "Biyolojik Psikoloji",          "credits": 3, "has_project": False, "hours": 3},
        ],
        "2. Yıl": [
            {"code": "PSI201", "name": "Sosyal Psikoloji",             "credits": 3, "has_project": False, "hours": 3},
            {"code": "PSI202", "name": "Gelişim Psikolojisi",          "credits": 3, "has_project": False, "hours": 3},
            {"code": "PSI203", "name": "Araştırma Yöntemleri I",       "credits": 3, "has_project": True,  "hours": 3},
            {"code": "PSI204", "name": "Öğrenme Psikolojisi",          "credits": 3, "has_project": False, "hours": 3},
        ],
        "3. Yıl": [
            {"code": "PSI301", "name": "Klinik Psikoloji",             "credits": 3, "has_project": False, "hours": 3},
            {"code": "PSI302", "name": "Endüstri-Örgüt Psikolojisi",   "credits": 3, "has_project": False, "hours": 3},
            {"code": "PSI303", "name": "Psikolojik Test ve Ölçme",     "credits": 3, "has_project": True,  "hours": 3},
            {"code": "PSI304", "name": "Anormal Psikoloji",            "credits": 3, "has_project": False, "hours": 3},
        ],
        "4. Yıl": [
            {"code": "PSI401", "name": "Bitirme Tezi",                 "credits": 6, "has_project": True,  "hours": 6},
            {"code": "PSI402", "name": "Psikoterapi Kuramları",        "credits": 3, "has_project": False, "hours": 3},
            {"code": "PSI403", "name": "Nöropsikoloji",                "credits": 3, "has_project": False, "hours": 3},
        ],
    },

    # ── Hemşirelik ────────────────────────────────────────────────────────────
    "Hemşirelik": {
        "1. Yıl": [
            {"code": "HEM101", "name": "Hemşireliğe Giriş",            "credits": 3, "has_project": False, "hours": 3},
            {"code": "HEM102", "name": "Anatomi ve Fizyoloji",         "credits": 4, "has_project": False, "hours": 4},
            {"code": "HEM103", "name": "Mikrobiyoloji",                "credits": 3, "has_project": False, "hours": 3},
            {"code": "AIT101", "name": "Atatürk İlkeleri I",           "credits": 2, "has_project": False, "hours": 2},
            {"code": "HEM104", "name": "Hemşirelik Becerileri I",      "credits": 4, "has_project": True,  "hours": 6},
        ],
        "2. Yıl": [
            {"code": "HEM201", "name": "İç Hastalıkları Hemşireliği",  "credits": 4, "has_project": True,  "hours": 6},
            {"code": "HEM202", "name": "Cerrahi Hastalıkları Hemşireliği","credits": 4, "has_project": True, "hours": 6},
            {"code": "HEM203", "name": "Farmakoloji",                  "credits": 3, "has_project": False, "hours": 3},
            {"code": "HEM204", "name": "Hemşirelik Araştırması",       "credits": 3, "has_project": True,  "hours": 3},
        ],
        "3. Yıl": [
            {"code": "HEM301", "name": "Çocuk Sağlığı Hemşireliği",    "credits": 4, "has_project": True,  "hours": 6},
            {"code": "HEM302", "name": "Kadın Sağlığı Hemşireliği",    "credits": 4, "has_project": True,  "hours": 6},
            {"code": "HEM303", "name": "Ruh Sağlığı Hemşireliği",      "credits": 4, "has_project": True,  "hours": 6},
        ],
        "4. Yıl": [
            {"code": "HEM401", "name": "Toplum Sağlığı Hemşireliği",   "credits": 4, "has_project": True,  "hours": 6},
            {"code": "HEM402", "name": "Hemşirelik Yönetimi",          "credits": 3, "has_project": False, "hours": 3},
            {"code": "HEM403", "name": "Bitirme Ödevi",                "credits": 4, "has_project": True,  "hours": 4},
        ],
    },

    # ── Mimarlık ──────────────────────────────────────────────────────────────
    "Mimarlık": {
        "1. Yıl": [
            {"code": "MIM101", "name": "Mimari Tasarım I",             "credits": 6, "has_project": True,  "hours": 8},
            {"code": "MIM102", "name": "Teknik Resim",                 "credits": 3, "has_project": True,  "hours": 4},
            {"code": "MIM103", "name": "Yapı Bilgisi I",               "credits": 3, "has_project": False, "hours": 3},
            {"code": "MIM104", "name": "Sanat Tarihi",                 "credits": 3, "has_project": False, "hours": 3},
            {"code": "AIT101", "name": "Atatürk İlkeleri I",           "credits": 2, "has_project": False, "hours": 2},
            {"code": "MIM105", "name": "Mimari Tasarım II",            "credits": 6, "has_project": True,  "hours": 8},
        ],
        "2. Yıl": [
            {"code": "MIM201", "name": "Mimari Tasarım III",           "credits": 6, "has_project": True,  "hours": 8},
            {"code": "MIM202", "name": "Yapı Bilgisi II",              "credits": 3, "has_project": False, "hours": 3},
            {"code": "MIM203", "name": "Statik",                       "credits": 3, "has_project": False, "hours": 3},
            {"code": "MIM204", "name": "Mimarlık Tarihi I",            "credits": 3, "has_project": False, "hours": 3},
        ],
        "3. Yıl": [
            {"code": "MIM301", "name": "Mimari Tasarım V",             "credits": 6, "has_project": True,  "hours": 8},
            {"code": "MIM302", "name": "Kentsel Tasarım",              "credits": 3, "has_project": True,  "hours": 4},
            {"code": "MIM303", "name": "Çevre Denetimi",               "credits": 3, "has_project": False, "hours": 3},
            {"code": "MIM304", "name": "Mimarlık Teorisi",             "credits": 3, "has_project": False, "hours": 3},
        ],
        "4. Yıl": [
            {"code": "MIM401", "name": "Bitirme Projesi I",            "credits": 6, "has_project": True,  "hours": 8},
            {"code": "MIM402", "name": "Bitirme Projesi II",           "credits": 6, "has_project": True,  "hours": 8},
            {"code": "MIM403", "name": "Mesleki Uygulama",             "credits": 3, "has_project": True,  "hours": 4},
        ],
    },

    # ── Gazetecilik ───────────────────────────────────────────────────────────
    "Gazetecilik": {
        "1. Yıl": [
            {"code": "GAZ101", "name": "İletişime Giriş",              "credits": 3, "has_project": False, "hours": 3},
            {"code": "GAZ102", "name": "Haber Yazarlığı",              "credits": 3, "has_project": True,  "hours": 3},
            {"code": "GAZ103", "name": "Türkçe Yazılı Anlatım",       "credits": 3, "has_project": False, "hours": 3},
            {"code": "AIT101", "name": "Atatürk İlkeleri I",           "credits": 2, "has_project": False, "hours": 2},
        ],
        "2. Yıl": [
            {"code": "GAZ201", "name": "Medya ve Toplum",              "credits": 3, "has_project": False, "hours": 3},
            {"code": "GAZ202", "name": "Gazetecilik Tarihi",           "credits": 3, "has_project": False, "hours": 3},
            {"code": "GAZ203", "name": "Fotoğrafçılık",                "credits": 3, "has_project": True,  "hours": 4},
        ],
        "3. Yıl": [
            {"code": "GAZ301", "name": "Dijital Gazetecilik",          "credits": 3, "has_project": True,  "hours": 3},
            {"code": "GAZ302", "name": "Radyo ve TV Haberciliği",      "credits": 3, "has_project": True,  "hours": 4},
            {"code": "GAZ303", "name": "Medya Hukuku",                 "credits": 3, "has_project": False, "hours": 3},
        ],
        "4. Yıl": [
            {"code": "GAZ401", "name": "Bitirme Projesi",              "credits": 4, "has_project": True,  "hours": 4},
            {"code": "GAZ402", "name": "Araştırmacı Gazetecilik",      "credits": 3, "has_project": True,  "hours": 3},
        ],
    },

    # ── Matematik ─────────────────────────────────────────────────────────────
    "Matematik": {
        "1. Yıl": [
            {"code": "MAT101", "name": "Analiz I",                     "credits": 4, "has_project": False, "hours": 4},
            {"code": "MAT102", "name": "Cebir I",                      "credits": 4, "has_project": False, "hours": 4},
            {"code": "MAT103", "name": "Analitik Geometri",            "credits": 3, "has_project": False, "hours": 3},
            {"code": "AIT101", "name": "Atatürk İlkeleri I",           "credits": 2, "has_project": False, "hours": 2},
            {"code": "MAT104", "name": "Analiz II",                    "credits": 4, "has_project": False, "hours": 4},
            {"code": "MAT105", "name": "Cebir II",                     "credits": 4, "has_project": False, "hours": 4},
        ],
        "2. Yıl": [
            {"code": "MAT201", "name": "Analiz III",                   "credits": 4, "has_project": False, "hours": 4},
            {"code": "MAT202", "name": "Lineer Cebir",                 "credits": 4, "has_project": False, "hours": 4},
            {"code": "MAT203", "name": "Diferansiyel Denklemler",      "credits": 4, "has_project": False, "hours": 4},
            {"code": "MAT204", "name": "Sayı Teorisi",                 "credits": 3, "has_project": False, "hours": 3},
        ],
        "3. Yıl": [
            {"code": "MAT301", "name": "Kompleks Analiz",              "credits": 4, "has_project": False, "hours": 4},
            {"code": "MAT302", "name": "Soyut Cebir",                  "credits": 4, "has_project": False, "hours": 4},
            {"code": "MAT303", "name": "Topoloji",                     "credits": 3, "has_project": False, "hours": 3},
            {"code": "MAT304", "name": "Olasılık Teorisi",             "credits": 3, "has_project": False, "hours": 3},
        ],
        "4. Yıl": [
            {"code": "MAT401", "name": "Bitirme Semineri",             "credits": 4, "has_project": True,  "hours": 4},
            {"code": "MAT402", "name": "Fonksiyonel Analiz",           "credits": 4, "has_project": False, "hours": 4},
            {"code": "MAT403", "name": "Diferansiyel Geometri",        "credits": 3, "has_project": False, "hours": 3},
        ],
    },
}

# ─── YARDIMCI FONKSİYONLAR ───────────────────────────────────────────────────

def get_all_departments():
    """Tüm bölümlerin listesini döndürür."""
    result = []
    for faculty, depts in UNIVERSITY_STRUCTURE.items():
        for dept in depts:
            result.append({"fakulte": faculty, "bolum": dept})
    return result

def get_departments_by_faculty(faculty_name):
    """Belirtilen fakültenin bölümlerini döndürür."""
    return list(UNIVERSITY_STRUCTURE.get(faculty_name, {}).keys())

def get_class_levels_for_department(dept_name):
    """Belirtilen bölümün sınıf seviyelerini döndürür."""
    for faculty_depts in UNIVERSITY_STRUCTURE.values():
        if dept_name in faculty_depts:
            return faculty_depts[dept_name]["siniflar"]
    return SINIF_4YIL

def get_courses_for_department(dept_name, year_label=None):
    """Bölüme ait dersleri döndürür. year_label = '1. Yıl', '2. Yıl' vb."""
    dept_data = DEPARTMENT_COURSES.get(dept_name, {})
    if year_label:
        return dept_data.get(year_label, [])
    all_courses = []
    for courses in dept_data.values():
        all_courses.extend(courses)
    return all_courses

def get_all_faculty_names():
    return list(UNIVERSITY_STRUCTURE.keys())

def get_year_label_from_class(class_name):
    """'2. Sınıf - A' -> '2. Yıl' dönüşümü."""
    if class_name:
        part = class_name.split(".")[0].strip()
        if part.isdigit():
            return f"{part}. Yıl"
    return "1. Yıl"
