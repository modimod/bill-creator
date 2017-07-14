# from jinja2 import Template, Environment, PackageLoader, select_autoescape
#
# template = Template('template.html')
# print template.render(items=([{'amount':1,'text':'hallo'},{'amount':2,'text':'hallo 2'},{'amount':3,'text':'hallo 3'}]), a_variable='here')
#

import os
import jinja2
import codecs

INDICES = {
	'date': 0,
	'receiver': 1,
	'address': 2,
	'city': 3,
	'bill_no': 4,
	'start_items': 5
}

heads = list(['amount','unit','text','price_per_unit','price'])


def render(tpl_path, context):
	path, filename = os.path.split(tpl_path)
	return jinja2.Environment(
					loader=jinja2.FileSystemLoader(path or './')
	).get_template(filename).render(context)

def read_source(src):
	data = None
	with codecs.open(src, "r", "utf-8") as file:
					data = list(file)

	context = {}
	context['date'] = data[INDICES['date']]
	context['receiver'] = data[INDICES['receiver']]
	context['address'] = data[INDICES['address']]
	context['city'] = data[INDICES['city']]
	context['bill_no'] = data[INDICES['bill_no']]


	start = INDICES['start_items']

	ids = list()

	for i,d in enumerate(data[start:]):
		if d.startswith('#'): ids.append(i+start)
	print('ids:',ids)
	print('len data',len(data))

	items_outer_list = list()
	for i,id in enumerate(ids):
		next_id = ids[i+1] if (i+1)<len(ids) else len(data)
		item = {}
		item['name'] = data[id][1:].rstrip()
		item['items'] = [{h: v.rstrip() for (h,v) in zip(heads,d.split(','))} for d in data[ids[i]+1:next_id]]

		items_outer_list.append(item)

	context['items'] = items_outer_list


	return context






def get_total_price(context):
	netto = 0.0
	mwst = 0.0
	brutto = 0.0

	for item in context['items']:
		for i in item['items']:
			netto += float(i['price'])

	mwst = netto*0.2
	brutto = netto+mwst
	return netto,mwst,brutto

context = {
	'items':
		[{
		'name': 'Kommission 1',
		'items': ([
			{'amount':5, 'unit': 'lfm', 'text': 'Store nähen', 'price_per_unit': 10, 'price': -50},
			{'amount':5, 'unit': 'lfm', 'text': 'FB', 'price_per_unit': 1, 'price': 5},
			{'amount':5,'unit':'lfm','text':'ziehen','price_per_unit':2,'price':10}
		])
	},{
		'name': 'Kommission 2',
		'items': ([
			{'amount': 5, 'unit': 'lfm', 'text': 'Store naehen', 'price_per_unit': 10, 'price': 50},
			{'amount': 5, 'unit': 'lfm', 'text': 'FB', 'price_per_unit': 1, 'price': 5},
			{'amount': 5, 'unit': 'lfm', 'text': 'ziehen', 'price_per_unit': 2, 'price': 10}
		])
	},{
		'name': 'Kommission 3',
		'items': ([
			{'amount': 5, 'unit': 'lfm', 'text': 'Store naehen', 'price_per_unit': 10, 'price': 50},
			{'amount': 5, 'unit': 'lfm', 'text': 'FB', 'price_per_unit': 1, 'price': 5},
			{'amount': 5, 'unit': 'lfm', 'text': 'ziehen', 'price_per_unit': 2, 'price': 10}
		])
	}],
	'location': 'Tragwein',
	'date': '15.06.2017',
	'receiver': 'Patrick Moertenboeck',
	'address': 'Gartenstrasse 12',
	'city': 'Tragwein',
	'bill_no': 'TR231'
}

context['netto'],context['mwst'],context['brutto'] = get_total_price(context)

#result = render('template.html', context)

scontext = read_source('source.txt')
scontext['netto'],scontext['mwst'],scontext['brutto'] = get_total_price(scontext)
result = render('template.html', scontext)

with open("bill.html", "w") as f:
	f.write(result)

print(read_source('source.txt'))