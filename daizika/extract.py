from edgar import SECHelper, SECEdgarParser

index_year = 2012
index_qtr = 1
print('{}/{}'.format(index_year, index_qtr))
formDownloader = SECHelper.FormDownloader()
formDownloader.download_qtr_forms(index_year=index_year, index_qtr=index_qtr, forms=['10-K'])
formProcessor = SECEdgarParser.FormProcessor()
form_list = formProcessor.extract_documents(form_type='10-K', extract_type=['10-K'], metadata=True)
form_list = formProcessor.extract_text(form_type='10-K')
formProcessor.convert_metadata_to_csv()
print('Done')
