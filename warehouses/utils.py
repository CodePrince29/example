from io import BytesIO
from django.http import HttpResponse
from django.template.loader import get_template
from xhtml2pdf import pisa
import pdfkit
from pyvirtualdisplay import Display

options = {
    'encoding': "utf-8",
    'custom-header' : [
        ('Accept-Encoding', 'gzip')
    ],
    'no-outline': None
}

def render_to_pdf(template_src, context_dict={}):
	try:
		template = get_template(template_src)
		html  = template.render(context_dict)
		pdf = None
		display = Display(visible=0, size=(640,480))
		try:
			display.start()
			pdf = pdfkit.from_string(html, False)
		finally:
			display.stop()
		return pdf
	except Exception as ex:
		print(ex)
		return None



def render_entrance_pdf(path= str, params= {}):
    template = get_template(path)
    html = template.render(params)
    response = BytesIO()
    pdf = pisa.pisaDocument(BytesIO(html.encode("UTF-8",'A4 landscape')), response)
    if not pdf.err:
        return HttpResponse(response.getvalue(), content_type='application/pdf')
    else:
        return HttpResponse("Error Rendering PDF", status=400)