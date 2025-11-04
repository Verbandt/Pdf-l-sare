from pdf_handling import PdfHandler, PdfMultiRegionExtractor, PdfCoordinateViewer

schemes = ["VV065E_R14_Gripdon 626B_20251028.pdf", "VV065E_R24_Gripdon 626B_20251028.pdf",
           "VV065E_R52_Gripdon 626B.pdf"]
scheme_to_use = schemes[0]

pdfHandler = PdfHandler(scheme_to_use)

pdfHandler.extract_pages()
pdfHandler.extract_information_from_pdf()
pdfHandler.export_data_to_excel()
