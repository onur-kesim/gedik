# KRITER — gedik benchmark hüküm kapısı (KİLİTLİ)

> Kilit: Onur, 2026-09-29 ("yap" ile Cowork'e devredilen 4 kararın önerilen varsayılanlarıyla).
> Benchmark KOŞUMUNDAN ÖNCE değiştirilebilir; KOŞUMDAN SONRA değişmez (hüküm kapısı).
> İlke: ölçmeden "daha iyi" yazılmaz; sonuç ne çıkarsa (kötü de olsa) yayımlanır.

## Hedefler (iki)
- **Hedef 1 — üçüncü taraf, önyargısız:** cevap anahtarı yayımlanmış, açığı bilinen hazır
  uygulama. **Karar D1 (kilitli):** Code iki adayı — OWASP Juice Shop ve daha küçük bir
  hedef — ölçüp seçer; seçim gerekçesi bu dosyaya eklenir. (Ölçmeden hedef sabitlenmez.)
- **Hedef 2 — niş, güçlü yan:** Supabase-RLS + LLM araç-yetkisi açıkları EKİLMİŞ küçük depo.
  Cevap anahtarı koşan ajanın göremeyeceği ayrı yerde; koşum temiz oturumda. (Kurulumu Code.)

## Yarışanlar (Karar D2, kilitli) — hepsi AYNI modelle
1. gedik (v2.6.0)
2. Anthropic `/security-review`
3. Anthropic `claude-security` plugin
4. `cloudflare/security-audit-skill`
5. Semgrep (mekanik taban çizgisi)

## Ortak model (Karar D3, kilitli)
Beş araç da TEK ve AYNI Claude modeliyle koşar; kullanılan modelin tam adı koşum anında
bu dosyaya yazılır. (Model farkı sonucu kirletmesin — kıyas planı escape.tech dersi.)

## Ölçü
- **recall** = bulunan / (bulunan + kaçan), ekilmiş/bilinen açıklara göre.
- **yanlış pozitif (FP)** sayısı.
- **şerit başına kırılım** (A/B/C/D/E).
- **K4 ölçüsü:** hedefin test paketine ekilen M6 (yetki) / M7 (doğrulama) mutantlarını kim
  yakalıyor — gedik'in ayırt edici iddiası; rakiplerde eşi var mı ölçülür.

## HÜKÜM EŞİĞİ (Karar D4, kilitli)
- **gedik recall ≥ en iyi rakip VE FP ≤ en iyi rakip** ise "daha iyi" denir.
- Biri tutmazsa: **"şu şeritte daha iyi, şurada geride"** yazılır — genel "daha iyi" YOK.
- Sonuç kötü çıkarsa da yayımlanır (README "NE TESLİM EDİLMEDİ" / dürüst kıyas, B3).

## Koşum dürüstlüğü
- Bu dosya KİLİTLİ; koşumdan sonra eşik değişmez.
- Her araç aynı koşulda (adil); cevap anahtarı koşan ajana kapalı.
- gedik'in canlı-test modu (§0.1) benchmark'ta KAPALI (hedefler yerel, yetki yok) — yalnız
  kaynak/artefakt okuma yüzeyi ölçülür; gedik'i dezavantaja sokar, ama dürüst olan bu.

## Değiştirilebilir varsayılan notu
D1–D4 Cowork'ün önerdiği varsayılanlardır; Onur benchmark başlamadan önce herhangi birini
değiştirebilir. Değişiklik bu dosyaya + DURUM karar günlüğüne yazılır. Koşum başladıktan
sonra kilit mutlaktır.
