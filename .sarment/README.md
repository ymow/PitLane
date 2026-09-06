# .sarment/

Sarment 驗證核心（`sarment-verify` wheel + ed25519 `.sig`），由 coordinator 放在預設分支，`.github/workflows/sarment-v1.yml`
安裝它來跑 V1。與 coordinator 跑 V2/V3 的是同一份 core（SPEC §10.3.2）。worker 的交付不能改這個目錄（V0 擋 `.github/**` 與 `.sarment/**`）。
