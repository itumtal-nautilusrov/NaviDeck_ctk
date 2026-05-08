import matplotlib.pyplot as plt

# Zaman ekseni (tasarım süreci aşamaları gibi düşün)
stages = ["Tasarım", "Prototip", "Üretim", "Final Sistem"]

# Yerlilik artışı (örnek modelleme)
locality = [60, 72, 78, 78]

# Tedarik dağılımı (referans çizgi gibi)
domestic = [25, 18, 12, 12]
foreign = [15, 10, 10, 10]

plt.figure()

plt.plot(stages, locality, marker="o", label="Okulda Üretim (%)")
plt.plot(stages, domestic, marker="o", label="Türkiye Tedarik (%)")
plt.plot(stages, foreign, marker="o", label="Yurt Dışı (%)")

plt.title("ROV Geliştirme Sürecinde Yerlilik Dağılımı")
plt.ylabel("Oran (%)")
plt.ylim(0, 100)

plt.grid(True, linestyle="--", alpha=0.5)
plt.legend()

plt.show()