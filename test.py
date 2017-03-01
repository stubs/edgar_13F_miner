#!/usr/bin/env python
from challenge import PageData


names = ['BILL & MELINDA GATES FOUNDATION TRUST','ABBEY NATIONAL TREASURY SERVICES PLC/ENG','ADVANTAGE INVESTMENT MANAGEMENT, LLC','AXIS CAPITAL HOLDINGS LTD','Alyeska Investment Group, L.P.','Banco Santander (Mexico) S.A., Institucion de Banca Multiple','Banco Santander, S.A.','CLOUGH CAPITAL PARTNERS L P','COURAGE CAPITAL MANAGEMENT LLC','CSOB Asset Management a.s.','Canty James Edward','Cardinal Capital Management','Ceskoslovenska Obchodni Banka a.s.','Clough Charles JR','Comprehensive Portfolio Management, LLC','First Light Asset Management, LLC','GREEN SQUARE CAPITAL LLC','GSB Wealth Management, LLC','Harrell Christopher J.','Harrell William H. Jr.','High Falls Advisors, Inc','INSIGHT CAPITAL RESEARCH & MANAGEMENT INC','KBC Participations Renta C','MACQUARIE BANK LTD','MACQUARIE GROUP LTD','MALTESE CAPITAL MANAGEMENT LLC','Macquarie Capital Investment Management LLC','Macquarie Funds Management Hong Kong Ltd','Macquarie Investment Management Austria Kapitalanlage AG','Macquarie Investment Management LTD','Pacific Center for Financial Services','PagnatoKarp Partners LLC','River Wealth Advisors LLC','Shepherd Financial Partners LLC','Sterling Investment Management, Inc.','TRG Investments, LLC','WEALTHSOURCE PARTNERS, LLC','WESTWOOD HOLDINGS GROUP INC','Wills Financial Group, Inc.','ZEVIN ASSET MANAGEMENT LLC']
ciks = ['1166559','931061','1697815','1214816','1453072','1698287','891478','1276144','1119376','1698364','1298578','1434845','1698340','1299903','1698218','1600004','1166308','1660694','1698066','1698064','1569139','938506','1698351','1257135','1418333','1040762','1313281','1590021','1548607','1435053','1698222','1698215','1642570','1696628','1509873','1675088','1674623','1165002','1525109','1394096']

test_dict = dict(zip(names, ciks))

for v in test_dict.values():
    PageData(v)
