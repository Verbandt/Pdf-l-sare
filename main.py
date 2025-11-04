from pdf_handling import PdfHandler, PdfTextMap, PdfVisualizer, PdfMultiRegionExtractor, PdfCoordinateViewer

schemes = ["VV065E_R14_Gripdon 626B_20251028.pdf", "VV065E_R24_Gripdon 626B_20251028.pdf",
           "VV065E_R52_Gripdon 626B.pdf"]

scheme_to_use = schemes[0]

pdf_handler = PdfHandler(scheme_to_use)
mapper = PdfTextMap(scheme_to_use)
visualizer = PdfVisualizer(scheme_to_use)
viewer = PdfCoordinateViewer(scheme_to_use)
extractor = PdfMultiRegionExtractor(scheme_to_use)

# viewer.view_page(page_number=1)
df = extractor.extract()
