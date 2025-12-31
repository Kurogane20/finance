-- Initial Seed for Chart of Accounts (Standar Akuntansi Indonesia)

-- ASSETS (1)
INSERT INTO accounts_coa (id, code, name, type, level, parent_id) VALUES (1, '10000', 'Aset', 'ASSET', 1, NULL);
-- Current Assets (11)
INSERT INTO accounts_coa (id, code, name, type, level, parent_id) VALUES (2, '11000', 'Aset Lancar', 'ASSET', 2, 1);
INSERT INTO accounts_coa (id, code, name, type, level, parent_id) VALUES (3, '11100', 'Kas & Bank', 'ASSET', 3, 2);
INSERT INTO accounts_coa (id, code, name, type, level, parent_id) VALUES (4, '11110', 'Kas Kecil', 'ASSET', 4, 3);
INSERT INTO accounts_coa (id, code, name, type, level, parent_id) VALUES (5, '11120', 'Bank BCA', 'ASSET', 4, 3);
INSERT INTO accounts_coa (id, code, name, type, level, parent_id) VALUES (6, '11130', 'Bank Mandiri', 'ASSET', 4, 3);

-- Receivables (12)
INSERT INTO accounts_coa (id, code, name, type, level, parent_id) VALUES (7, '11200', 'Piutang Usaha', 'ASSET', 3, 2);
INSERT INTO accounts_coa (id, code, name, type, level, parent_id) VALUES (8, '11300', 'Persediaan', 'ASSET', 3, 2);

-- Fixed Assets (13)
INSERT INTO accounts_coa (id, code, name, type, level, parent_id) VALUES (9, '12000', 'Aset Tetap', 'ASSET', 2, 1);
INSERT INTO accounts_coa (id, code, name, type, level, parent_id) VALUES (10, '12100', 'Tanah & Bangunan', 'ASSET', 3, 9);
INSERT INTO accounts_coa (id, code, name, type, level, parent_id) VALUES (11, '12200', 'Kendaraan', 'ASSET', 3, 9);
INSERT INTO accounts_coa (id, code, name, type, level, parent_id) VALUES (12, '12210', 'Akumulasi Penyusutan Kendaraan', 'ASSET', 4, 11);

-- LIABILITIES (2)
INSERT INTO accounts_coa (id, code, name, type, level, parent_id) VALUES (13, '20000', 'Kewajiban', 'LIABILITY', 1, NULL);
INSERT INTO accounts_coa (id, code, name, type, level, parent_id) VALUES (14, '21000', 'Kewajiban Lancar', 'LIABILITY', 2, 13);
INSERT INTO accounts_coa (id, code, name, type, level, parent_id) VALUES (15, '21100', 'Utang Usaha', 'LIABILITY', 3, 14);
INSERT INTO accounts_coa (id, code, name, type, level, parent_id) VALUES (16, '21200', 'Utang Gaji', 'LIABILITY', 3, 14);
INSERT INTO accounts_coa (id, code, name, type, level, parent_id) VALUES (17, '21300', 'Utang Pajak', 'LIABILITY', 3, 14);

-- EQUITY (3)
INSERT INTO accounts_coa (id, code, name, type, level, parent_id) VALUES (18, '30000', 'Ekuitas', 'EQUITY', 1, NULL);
INSERT INTO accounts_coa (id, code, name, type, level, parent_id) VALUES (19, '31000', 'Modal Disetor', 'EQUITY', 2, 18);
INSERT INTO accounts_coa (id, code, name, type, level, parent_id) VALUES (20, '32000', 'Laba Ditahan', 'EQUITY', 2, 18);

-- REVENUE (4)
INSERT INTO accounts_coa (id, code, name, type, level, parent_id) VALUES (21, '40000', 'Pendapatan', 'REVENUE', 1, NULL);
INSERT INTO accounts_coa (id, code, name, type, level, parent_id) VALUES (22, '41000', 'Pendapatan Usaha', 'REVENUE', 2, 21);
INSERT INTO accounts_coa (id, code, name, type, level, parent_id) VALUES (23, '41100', 'Penjualan Jasa', 'REVENUE', 3, 22);
INSERT INTO accounts_coa (id, code, name, type, level, parent_id) VALUES (24, '41200', 'Penjualan Produk', 'REVENUE', 3, 22);

-- EXPENSES (5) - (6)
INSERT INTO accounts_coa (id, code, name, type, level, parent_id) VALUES (25, '50000', 'Beban Pokok Penjualan', 'EXPENSE', 1, NULL);
INSERT INTO accounts_coa (id, code, name, type, level, parent_id) VALUES (26, '60000', 'Beban Operasional', 'EXPENSE', 1, NULL);
INSERT INTO accounts_coa (id, code, name, type, level, parent_id) VALUES (27, '61000', 'Beban Gaji', 'EXPENSE', 2, 26);
INSERT INTO accounts_coa (id, code, name, type, level, parent_id) VALUES (28, '62000', 'Beban Sewa', 'EXPENSE', 2, 26);
INSERT INTO accounts_coa (id, code, name, type, level, parent_id) VALUES (29, '63000', 'Beban Listrik & Air', 'EXPENSE', 2, 26);
INSERT INTO accounts_coa (id, code, name, type, level, parent_id) VALUES (30, '64000', 'Beban Pemasaran', 'EXPENSE', 2, 26);
