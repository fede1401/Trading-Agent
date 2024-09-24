symbols = ['AAPL', 'ABNB', 'ACGL', 'ADBE', 'ADI', 'ADP', 'ADSK', 'AKAM', 'ALGN', 'AMAT', 'AMD',
               'AMGN', 'AMZN', 'AVGO', 'AZN', 'BIDU', 'BKNG', 'BL', 'BMRN', 
               'BNTX', 'CAR', 'CARG', 'CDNS', 'CDW', 'CG', 'CMCSA', 'CME', 'COIN',
               'COST', 'CROX', 'CRWD', 'CSCO', 'CTAS', 'CTSH', 'DASH', 'DDOG', 'DKNG', 'DLTR', 
                'EA', 'EBAY', 'ENPH', 'ENTA', 'ENTG', 'ERII', 'ETSY', 'EVBG', 'EXAS', 'EXPE', 'EYE', 'FANG', 'FAST', 'FIVE', 
               'FLEX', 'FOLD', 'FORM', 'FOX', 'FRPT', 'FSLR', 'FTNT', 'GBDC', 'GDS', 'GH', 'GILD', 'GLNG', 'GLPI', 'GOGL', 'GOOGL', 'GPRE', 'GPRO', 
               'GTLB', 'HAIN', 'HCM', 'HCSG', 'HIBB', 'HOOD', 'HQY', 'HTHT', 'IART', 'IBKR', 'ICLR', 'ILMN', 'INCY', 'INSM', 'INTC', 'IOVA', 'IRDM', 
               'IRTC', 'IRWD', 'ISRG', 'ITRI', 'JACK', 'JD', 'KLIC', 'KRNT', 'KTOS', 'LAUR', 'LBRDK', 'LBTYA', 'LI', 'LITE', 'LIVN', 'LNT', 'LNTH', 
               'LOGI', 'LOPE', 'LPLA', 'LPSN', 'LRCX', 'LSCC', 'LYFT', 'MANH', 'MAR', 'MASI', 'MDB', 'MDLZ', 'MEDP', 'META', 'MKSI', 'MMSI', 
               'MNRO', 'MNST', 'MPWR', 'MRCY', 'MRNA', 'MSFT', 'MSTR', 'MTCH', 'MTSI', 'MU', 'MYGN', 'NAVI', 'NBIX', 'NDAQ', 'NEOG', 'NFLX', 'NMIH', 
               'NSIT', 'NTCT', 'NTES', 'NTNX', 'NTRA', 'NVCR', 'NVDA', 'NWSA', 'ODP', 'OKTA', 'OLLI', 'OMCL', 'ORLY', 'PAYX', 'PCH', 'PDD', 'PEGA', 
               'PENN', 'PEP', 'PGNY', 'PLAY', 'PLUG', 'POOL', 'POWI', 'PPC', 'PRAA', 'PRGS', 'PTC', 'PTCT', 'PTEN', 'PTON', 'PYPL', 'PZZA', 'QCOM', 
               'QDEL', 'QFIN', 'QLYS', 'RARE', 'RCM', 'REG', 'REGN', 'REYN', 'RGEN', 'RIVN', 'RMBS', 'ROIC', 'ROKU', 'RPD', 'RRR', 'RUN', 'SAGE', 
               'SAIA', 'SANM', 'SBAC', 'SBGI', 'SBLK', 'SBRA', 'SBUX', 'SEDG', 'SFM', 'SGRY', 'SHOO', 'SKYW', 'SLM', 'SMTC', 'SONO', 'SPWR', 'SRCL', 
               'SRPT', 'SSRM', 'STX', 'SWKS', 'SYNA', 'TMUS', 'TRIP', 'TRMB', 'TROW', 'TSCO', 'TSLA', 'TTEK', 'TTMI', 'TTWO', 'TXG', 'TXRH', 'UAL', 
               'UCTT', 'URBN', 'VCYT', 'VECO', 'VIAV', 'VIRT', 'VRNS', 'VRNT', 'VRSK', 'VRSN', 'VRTX', 'VSAT', 'WB', 'WDC', 'WERN', 'WING', 'WIX', 
               'WMG', 'WSC', 'WSFS', 'WWD', 'XP', 'XRAY', 'YY', 'ZD', 'ZG', 'ZI', 'ZLA']

"""
i = 0
symbols5Caps = []
with open('csv_files/nasdaq_symbols_sorted.csv', mode='r') as file:
    for line in file:
        line = line.split(',')
        if line[0] in symbols:
            if i < 200:
                symbols5Caps.append(line[0])
            i += 1
             
print(symbols5Caps)
"""

s = ['AAPL', 'MSFT', 'NVDA', 'GOOGL', 'AMZN', 'META', 'AVGO', 'TSLA', 'COST', 'NFLX', 'AMD', 'AZN', 'QCOM', 'ADBE', 'PEP', 'TMUS', 
     'PDD', 'AMAT', 'CSCO', 'AMGN', 'MU', 'ISRG', 'CMCSA', 'LRCX', 'BKNG', 'INTC', 'VRTX', 'REGN', 'ADI', 'ADP', 'ABNB', 'CRWD', 
     'SBUX', 'MDLZ', 'CDNS', 'GILD', 'CTAS', 'CME', 'MAR', 'PYPL', 'ORLY', 'NTES', 'COIN', 'MRNA', 'ADSK', 'MNST', 'FTNT', 'JD', 
     'DASH', 'PAYX', 'MPWR', 'DDOG', 'VRSK', 'ACGL', 'EA', 'FAST', 'NDAQ', 'FANG', 'BIDU', 'CTSH', 'TSCO', 'CDW', 'FSLR', 'TTWO', 
     'EBAY', 'ICLR', 'MSTR', 'TROW', 'WDC', 'DLTR', 'STX', 'BNTX', 'LPLA', 'PTC', 'SBAC', 'ENTG', 'HOOD', 'DKNG', 'LI', 'ALGN', 'VRSN', 
     'ILMN', 'ENPH', 'SWKS', 'EXPE', 'MDB', 'UAL', 'WMG', 'BMRN', 'LOGI', 'NWSA', 'OKTA', 'FOX', 'MANH', 'CG', 'INCY', 'NTRA', 'NBIX', 
     'AKAM', 'TRMB', 'NTNX', 'POOL', 'IBKR', 'LNT', 'FLEX', 'MEDP', 'WING', 'SAIA', 'GLPI', 'SRPT', 'REG', 'TXRH', 'TTEK', 'WWD', 'ZG', 
     'RIVN', 'HTHT', 'CROX', 'INSM', 'XP', 'WIX', 'MKSI', 'LSCC', 'PPC', 'MTCH', 'SFM', 'ROKU', 'EXAS', 'MTSI', 'MASI', 'HQY', 'LBRDK', 
     'WSC', 'RGEN', 'ETSY', 'GTLB',  'NSIT', 'LBTYA', 'FIVE', 'FRPT', 'RMBS', 'REYN', 'LYFT', 'OLLI', 'LNTH', 'RRR', 'SRCL', 'XRAY', 'RCM', 
     'QLYS', 'PEGA', 'VRNS', 'MMSI', 'ITRI', 'ZI', 'FORM', 'SLM', 'GBDC', 'POWI', 'LOPE', 'URBN', 'PTEN', 'VIRT', 'CAR', 'GH', 'SANM', 
     'NEOG', 'SYNA', 'SBRA', 'RARE', 'LITE', 'PCH', 'SGRY', 'IRDM', 'SHOO', 'HCM', 'SKYW', 'QFIN', 'GLNG', 'FOLD', 'KTOS', 'IRTC', 
     'RUN', 'LIVN', 'BL', 'PTCT', 'PENN', 'CARG', 'VECO', 'WSFS', 'NMIH', 'GOGL', 'ZD', 'PGNY', 'KLIC', 'TRIP', 'QDEL', 'TXG', 'IART', 
     'WERN']
        
"""for ele in s:
    if ele not in symbols:
        print(ele)"""
        
        
live = ['AAPL', 'MSFT', 'NVDA', 'GOOGL', 'AMZN', 'META', 'AVGO', 'TSLA', 'COST', 'NFLX', 'AMD', 'AZN', 'QCOM', 'ADBE', 'PEP', 
        'TMUS', 'PDD', 'AMAT', 'CSCO', 'AMGN', 'MU', 'ISRG', 'CMCSA', 'LRCX', 'BKNG', 'INTC', 'VRTX', 'REGN', 'ADI', 'ADP', 'ABNB', 
        'CRWD', 'SBUX', 'MDLZ', 'CDNS', 'GILD', 'CTAS', 'CME', 'MAR', 'PYPL', 'ORLY', 'NTES', 'COIN', 'MRNA', 'ADSK', 'MNST',
        'FTNT', 'JD', 'DASH', 'PAYX', 'MPWR', 'DDOG', 'VRSK', 'ACGL', 'EA', 'FAST', 'NDAQ', 'FANG', 'BIDU', 'CTSH', 'TSCO', 'CDW', 
        'FSLR', 'TTWO', 'EBAY', 'ICLR', 'MSTR', 'TROW', 'WDC', 'DLTR', 'STX', 'BNTX', 'LPLA', 'PTC', 'SBAC', 'ENTG', 'HOOD',
        'DKNG', 'LI', 'ALGN', 'VRSN', 'ZM', 'ILMN', 'ENPH', 'SWKS', 'EXPE', 'MDB', 'UAL', 'WMG', 'BMRN', 'LOGI', 'NWSA', 'OKTA', 
        'FOX', 'MANH', 'CG', 'INCY', 'NTRA', 'NBIX', 'AKAM', 'TRMB', 'NTNX', 'POOL', 'IBKR', 'LNT', 'FLEX', 'MEDP', 'WING', 
        'SAIA', 'GLPI', 'SRPT', 'REG', 'TXRH', 'TTEK', 'WWD', 'ZG', 'RIVN', 'HTHT', 'DOCU', 'BRKR', 'CROX', 'INSM', 'XP', 'WIX', 
        'MKSI', 'AMKR', 'LSCC', 'PPC', 'MTCH', 'SFM', 'CGNX', 'ROKU', 'EXAS', 'CZR', 'MTSI', 'AAL', 'MASI', 'HQY', 'LBRDK', 'WSC', 
        'RGEN', 'ETSY', 'GTLB', 'DBX', 'BPMC', 'NSIT', 'LBTYA', 'BILI', 'FIVE', 'FRPT', 'RMBS', 'REYN', 'LYFT', 'OLLI', 'LNTH', 
        'CYTK', 'RRR', 'SRCL', 'CRSP', 'XRAY', 'RCM', 'APLS', 'QLYS', 'EEFT', 'PEGA', 'COLM', 'VRNS', 'MMSI', 'ITRI', 'ZI', 
        'FORM', 'SLM', 'GBDC', 'POWI', 'LOPE', 'URBN', 'PTEN', 'ACIW', 'VIRT', 'CAR', 'GH', 'SANM', 'NEOG', 'SYNA', 'SBRA', 'RARE', 
        'MEOH', 'LITE', 'PCH', 'SGRY', 'IRDM', 'SHOO', 'HCM', 'ARWR', 'ALRM', 'SKYW', 'QFIN', 'GLNG', 'AMED', 'CORT', 'FOLD', 'KTOS', 
        'IRTC', 'RUN', 'DNLI', 'CALM', 'LIVN', 'BL', 'PTCT', 'PENN', 'CARG', 'VECO', 'WSFS', 'NMIH', 'GOGL', 'ZD', 'PGNY', 'KLIC', 
        'TRIP', 'AGIO', 'ACAD', 'QDEL', 'TXG', 'IART', 'WERN', 'RPD', 'IOVA', 'SEDG', 'NVCR', 'DLO', 'LAUR', 'VRNT', 'UCTT', 'PRGS', 
        'MYGN', 'SBLK', 'CAKE', 'PLUG', 'WB', 'SMTC', 'TTMI', 'SONO', 'ZLAB', 'GDS', 'PLAY', 'VSAT', 'MRCY', 'YY', 'VIAV', 'BLMN', 
        'VCYT', 'NAVI', 'PZZA', 'ROIC', 'EVBG', 'PTON', 'ODP', 'BMBL', 'NTCT', 'OMCL', 'BCRX', 'CSIQ', 'HIBB', 'JACK', 'EYE', 
        'CBRL', 'GPRE', 'SSRM', 'IRWD', 'ATSG', 'PRAA', 'HCSG', 'ERII', 'SAGE', 'KRNT', 'MNRO', 'HAIN', 'SPWR', 'SBGI', 'CYRX', 
        'ENTA', 'GPRO', 'APPS', 'LPSN']


for ele in s:
    if ele not in live:
        print(f"S-Live: {ele}")
        
print('\n\n--------------')

for ele in live:
    if ele not in s:
        print(f"Live-S: {ele}")
        
