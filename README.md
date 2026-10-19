# 藥品仿單快查

輸入健保碼（或第 3–7 碼的五碼數字）、商品名、學名或許可證字號，查詢適應症、常見頻次，並直接開啟衛福部食藥署的官方仿單。

純靜態網站（`index.html` + `drugs.json`），不需要建置步驟，可直接部署到 Vercel。

## 資料來源

- 衛生福利部食品藥物管理署：全部藥品許可證、藥品仿單或外盒資料集
- 衛生福利部中央健康保險署：健保用藥品項
- 經開源專案 [TFDA-drug-info-search](https://github.com/liangRXdev/TFDA-drug-info-search) 每週整併，再精簡為 `drugs.json`

本工具協助查找官方仿單，非官方服務。用藥請以醫師、藥師指示與最新核准仿單為準。

作者：[AI效能實驗室－許秉軒藥師](https://hsuportfolio-o9pzopyg.manus.space/)
